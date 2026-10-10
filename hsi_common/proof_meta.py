#!/usr/bin/env python3
"""HSI-UPOK/0.1: bounded predicate proof search and modal meta-logic research.

NO network, subprocess, file writes, deployment privileges, or trading.
The finite proof checker recognizes only explicitly listed inference rules.
A successful finite model check is not validity across all possible models.
"""
from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import re
import sys

PROTOCOL = "HSI-UPOK/0.1"
IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,30}$")
OPS = {"pred", "and", "or", "imp", "not", "forall", "exists", "box", "diamond"}
MAX_FORMULA_BYTES = 4096
MAX_DEPTH = 24
MAX_STEPS = 256
MAX_WORLDS = 24
MAX_DOMAIN = 24
MAX_EVAL_CALLS = 50000
MAX_GODEL_BYTES = 1024


class Invalid(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def godel_encode(value):
    return functools.reduce(lambda n, b: n * 257 + b + 1, canonical(value).encode("utf-8"), 1)


def validate_formula(f, depth=0):
    if depth > MAX_DEPTH or not isinstance(f, dict) or f.get("op") not in OPS:
        raise Invalid("invalid formula or depth")
    op = f["op"]
    spec = {"pred": {"op", "name", "args"}, "and": {"op", "left", "right"},
            "or": {"op", "left", "right"}, "imp": {"op", "left", "right"},
            "not": {"op", "arg"}, "box": {"op", "arg"}, "diamond": {"op", "arg"},
            "forall": {"op", "var", "body"}, "exists": {"op", "var", "body"}}
    if set(f) != spec[op]:
        raise Invalid("formula fields do not match grammar")
    if op == "pred":
        if not isinstance(f["name"], str) or not IDENT.fullmatch(f["name"]):
            raise Invalid("invalid predicate")
        if not isinstance(f["args"], list) or len(f["args"]) > 8 or any(
                not isinstance(t, str) or not IDENT.fullmatch(t) for t in f["args"]):
            raise Invalid("invalid predicate terms")
    elif op in {"and", "or", "imp"}:
        validate_formula(f["left"], depth+1)
        validate_formula(f["right"], depth+1)
    elif op in {"not", "box", "diamond"}:
        validate_formula(f["arg"], depth+1)
    else:
        if not isinstance(f["var"], str) or not IDENT.fullmatch(f["var"]):
            raise Invalid("invalid binder")
        validate_formula(f["body"], depth+1)
    if depth == 0 and len(canonical(f).encode("utf-8")) > MAX_FORMULA_BYTES:
        raise Invalid("formula too large")
    return f


def free_occurs(f, var, bound=frozenset()):
    op = f["op"]
    if op == "pred":
        return var not in bound and var in f["args"]
    if op in {"forall", "exists"}:
        return free_occurs(f["body"], var, bound | {f["var"]})
    if op in {"and", "or", "imp"}:
        return free_occurs(f["left"], var, bound) or free_occurs(f["right"], var, bound)
    return free_occurs(f["arg"], var, bound)


def substitute(f, var, term):
    """Capture-avoiding substitution; reject capture rather than alpha-renaming."""
    if not isinstance(term, str) or not IDENT.fullmatch(term):
        raise Invalid("invalid substitution term")
    op = f["op"]
    if op == "pred":
        return {**f, "args": [term if a == var else a for a in f["args"]]}
    if op in {"forall", "exists"}:
        if f["var"] == var:
            return copy.deepcopy(f)
        if f["var"] == term and free_occurs(f["body"], var):
            raise Invalid("substitution would capture a variable")
        return {**f, "body": substitute(f["body"], var, term)}
    if op in {"and", "or", "imp"}:
        return {"op": op, "left": substitute(f["left"], var, term),
                "right": substitute(f["right"], var, term)}
    return {"op": op, "arg": substitute(f["arg"], var, term)}


def verify_proof(premises, steps, goal):
    """Check each natural-deduction inference independently of proof search."""
    if (not isinstance(premises, list) or len(premises) > MAX_STEPS or
            not isinstance(steps, list) or len(steps) > MAX_STEPS):
        raise Invalid("invalid proof length")
    validate_formula(goal)
    premise_set = set()
    for p in premises:
        validate_formula(p)
        premise_set.add(canonical(p))
    known = []
    for i, s in enumerate(steps):
        if not isinstance(s, dict) or not isinstance(s.get("rule"), str) or "formula" not in s:
            raise Invalid("invalid proof step")
        f = validate_formula(s["formula"])
        rule = s["rule"]
        refs = s.get("refs", [])
        if not isinstance(refs, list) or any(type(r) is not int or r < 0 or r >= i for r in refs):
            raise Invalid("invalid proof references")
        args = [known[r] for r in refs]
        if rule == "premise":
            ok = set(s) == {"rule", "formula", "refs"} and not refs and canonical(f) in premise_set
        elif rule == "and_intro":
            ok = set(s) == {"rule", "formula", "refs"} and len(args) == 2 and f == {
                "op": "and", "left": args[0], "right": args[1]}
        elif rule in {"and_left", "and_right"}:
            side = "left" if rule == "and_left" else "right"
            ok = set(s) == {"rule", "formula", "refs"} and len(args) == 1 and args[0].get("op") == "and" and f == args[0][side]
        elif rule == "imp_elim":
            ok = set(s) == {"rule", "formula", "refs"} and len(args) == 2 and args[0].get("op") == "imp" and args[0]["left"] == args[1] and f == args[0]["right"]
        elif rule == "forall_elim":
            ok = set(s) == {"rule", "formula", "refs", "term"} and len(args) == 1 and args[0].get("op") == "forall" and isinstance(s.get("term"), str)
            if ok:
                try:
                    ok = f == substitute(args[0]["body"], args[0]["var"], s["term"])
                except Invalid:
                    ok = False
        elif rule == "exists_intro":
            ok = set(s) == {"rule", "formula", "refs", "term"} and len(args) == 1 and f.get("op") == "exists" and isinstance(s.get("term"), str)
            if ok:
                try:
                    ok = args[0] == substitute(f["body"], f["var"], s["term"])
                except Invalid:
                    ok = False
        else:
            ok = False
        if not ok:
            raise Invalid(f"unverified inference at step {i}: {rule}")
        known.append(f)
    return bool(known) and known[-1] == goal


def constants_in_formula(f, bound=frozenset()):
    if f["op"] == "pred":
        return set(f["args"]) - bound
    if f["op"] in {"forall", "exists"}:
        return constants_in_formula(f["body"], bound | {f["var"]})
    if f["op"] in {"and", "or", "imp"}:
        return constants_in_formula(f["left"], bound) | constants_in_formula(f["right"], bound)
    return constants_in_formula(f["arg"], bound)


def prove_bounded(premises, goal, max_steps=MAX_STEPS):
    """Sound but incomplete proof search, using a limited rule set and budget."""
    if type(max_steps) is not int or not 1 <= max_steps <= MAX_STEPS:
        raise Invalid("invalid step budget")
    if not isinstance(premises, list) or len(premises)>MAX_STEPS:
        raise Invalid("invalid premises")
    validate_formula(goal)
    for p in premises:
        validate_formula(p)
    terms = sorted(set().union(*(constants_in_formula(f) for f in [*premises, goal])))[:32]
    seen, steps = {}, []

    def add(rule, f, refs, term=None):
        key = canonical(f)
        if key in seen or len(steps) >= max_steps:
            return False
        s = {"rule": rule, "formula": f, "refs": list(refs)}
        if term is not None:
            s["term"] = term
        seen[key] = len(steps)
        steps.append(s)
        return True

    for p in premises:
        add("premise", p, [])
    idx = 0
    while idx < len(steps):
        formula = steps[idx]["formula"]
        op = formula["op"]
        if op == "and":
            add("and_left", formula["left"], [idx])
            add("and_right", formula["right"], [idx])
        if op == "forall":
            for t in terms:
                try:
                    add("forall_elim", substitute(formula["body"], formula["var"], t), [idx], t)
                except Invalid:
                    pass
        if op == "imp":
            ante = seen.get(canonical(formula["left"]))
            if ante is not None:
                add("imp_elim", formula["right"], [idx, ante])
        for other_idx in range(len(steps)):
            other = steps[other_idx]["formula"]
            if other.get("op") == "imp" and other["left"] == formula:
                add("imp_elim", other["right"], [other_idx, idx])
        if goal["op"] == "and":
            l, r = seen.get(canonical(goal["left"])), seen.get(canonical(goal["right"]))
            if l is not None and r is not None:
                add("and_intro", goal, [l, r])
        elif goal["op"] == "exists":
            for t in terms:
                try:
                    witness = substitute(goal["body"], goal["var"], t)
                    pos = seen.get(canonical(witness))
                    if pos is not None:
                        add("exists_intro", goal, [pos], t)
                except Invalid:
                    pass
        if canonical(goal) in seen:
            pos = seen[canonical(goal)]
            cut = steps[:pos+1]
            if not verify_proof(premises, cut, goal):
                raise Invalid("internal checker rejected candidate")
            serialized = canonical(cut).encode("utf-8")
            return {
                "status": "PROVED_WITHIN_BUDGET", "steps": cut,
                "certificate": {
                    "verified": True,
                    "proof_godel": str(godel_encode(cut)) if len(serialized) <= MAX_GODEL_BYTES else None,
                    "proof_sha256": hashlib.sha256(serialized).hexdigest(),
                    "proof_utf8_bytes": len(serialized),
                    "scope": "finite derivation under explicitly listed assumptions",
                },
                "external_authorization": False,
            }
        idx += 1
    return {"status": "UNRESOLVED_WITHIN_BUDGET", "steps": [],
            "certificate": {"verified": False}, "external_authorization": False}


def _validate_model(m):
    if not isinstance(m, dict) or set(m) != {"worlds", "edges", "domain", "predicates"}:
        raise Invalid("invalid model schema")
    worlds, domain, edges, valuation = m["worlds"], m["domain"], m["edges"], m["predicates"]
    if not isinstance(worlds, list) or not 1 <= len(worlds) <= MAX_WORLDS or any(type(w) is not str or not IDENT.fullmatch(w) for w in worlds) or len(set(worlds)) != len(worlds):
        raise Invalid("invalid worlds")
    if not isinstance(domain, list) or not 1 <= len(domain) <= MAX_DOMAIN or any(type(c) is not str or not IDENT.fullmatch(c) for c in domain) or len(set(domain)) != len(domain):
        raise Invalid("invalid domain")
    if not isinstance(edges, list) or len(edges) > MAX_WORLDS**2 or any(not isinstance(e, list) or len(e) != 2 or any(w not in worlds for w in e) for e in edges):
        raise Invalid("invalid accessibility edges")
    if not isinstance(valuation, dict) or set(valuation) != set(worlds):
        raise Invalid("invalid valuations")
    for w in worlds:
        if not isinstance(valuation[w], dict):
            raise Invalid("invalid world predicates")
        for pred, tuples in valuation[w].items():
            if not isinstance(pred, str) or not IDENT.fullmatch(pred) or not isinstance(tuples, list) or len(tuples)>512:
                raise Invalid("invalid relation interpretation")
            if any(not isinstance(t, list) or len(t)>8 or any(c not in domain for c in t) for t in tuples):
                raise Invalid("invalid relation tuple")
    return set(map(tuple, edges))


def holds(f, model, world, env=None):
    """Evaluate a predicate-modal formula in a finite, constant-domain model."""
    validate_formula(f)
    edges = _validate_model(model)
    if world not in model["worlds"]:
        raise Invalid("unknown evaluation world")
    if not isinstance(env, dict) and env is not None:
        raise Invalid("invalid environment")
    return _eval(f, model, edges, world, dict(env or {}), [MAX_EVAL_CALLS])


def _eval(f, model, edges, w, env, fuel):
    fuel[0] -= 1
    if fuel[0] < 0:
        raise Invalid("finite model-checking budget exhausted")
    op = f["op"]
    if op == "pred":
        args = [env.get(a, a) for a in f["args"]]
        if any(a not in model["domain"] for a in args):
            raise Invalid("unassigned/free variable or unknown domain constant")
        return args in model["predicates"][w].get(f["name"], [])
    if op == "not":
        return not _eval(f["arg"], model, edges, w, env, fuel)
    if op == "and":
        return _eval(f["left"], model, edges, w, env, fuel) and _eval(f["right"], model, edges, w, env, fuel)
    if op == "or":
        return _eval(f["left"], model, edges, w, env, fuel) or _eval(f["right"], model, edges, w, env, fuel)
    if op == "imp":
        return not _eval(f["left"], model, edges, w, env, fuel) or _eval(f["right"], model, edges, w, env, fuel)
    if op in {"forall", "exists"}:
        truth=[]
        for v in model["domain"]:
            child=dict(env)
            child[f["var"]]=v
            truth.append(_eval(f["body"], model, edges, w, child, fuel))
        return all(truth) if op == "forall" else any(truth)
    accessible=[v for v in model["worlds"] if (w,v) in edges]
    truth=[_eval(f["arg"], model, edges, v, env, fuel) for v in accessible]
    return all(truth) if op == "box" else any(truth)


def classify_frame(model):
    """Classify supplied finite frames, not universal validity of a logic."""
    r=_validate_model(model)
    w=model["worlds"]
    reflexive=all((x,x) in r for x in w)
    transitive=all((x,z) in r for x,y in r for y2,z in r if y == y2)
    symmetric=all((y,x) in r for x,y in r)
    euclidean=all((y,z) in r for x,y in r for a,z in r if a==x)
    accepted=["K"]
    if reflexive:
        accepted.append("T")
    if reflexive and transitive:
        accepted.append("S4")
    if reflexive and symmetric and transitive:
        accepted.append("S5")
    return {"protocol": PROTOCOL, "status": "FINITE_FRAME_CLASSIFIED",
            "satisfies_frame_conditions_for": accepted,
            "properties": {"reflexive":reflexive, "transitive":transitive,
                           "symmetric":symmetric, "euclidean":euclidean},
            "scope": "particular finite frame; not a proof of all frame models",
            "external_authorization": False}


def explore_axioms(model):
    """Explore a fixed modal axiom library and verify finite countermodels."""
    edges = _validate_model(model)
    worlds = model["worlds"]
    p = {"op": "pred", "name": "Probe", "args": []}
    axioms = {
        "K": {"op":"imp", "left":{"op":"box", "arg":{"op":"imp", "left":p, "right":{"op":"pred","name":"Other","args":[]}}},
              "right":{"op":"imp", "left":{"op":"box","arg":p}, "right":{"op":"box","arg":{"op":"pred","name":"Other","args":[]}}}},
        "T": {"op":"imp", "left":{"op":"box","arg":p}, "right":p},
        "4": {"op":"imp", "left":{"op":"box","arg":p}, "right":{"op":"box","arg":{"op":"box","arg":p}}},
        "5": {"op":"imp", "left":{"op":"diamond","arg":p}, "right":{"op":"box","arg":{"op":"diamond","arg":p}}},
    }
    candidates = {}
    for name in ("K", "T", "4", "5"):
        witness = None
        if name == "T":
            for w in worlds:
                if (w,w) not in edges:
                    witness = (w, {v for v in worlds if (w,v) in edges})
                    break
        elif name == "4":
            for w in worlds:
                for v in worlds:
                    for z in worlds:
                        if (w,v) in edges and (v,z) in edges and (w,z) not in edges:
                            witness = (w, set(worlds)-{z})
                            break
                    if witness: break
                if witness: break
        elif name == "5":
            for w in worlds:
                for v in worlds:
                    for z in worlds:
                        if (w,v) in edges and (w,z) in edges and (v,z) not in edges:
                            witness = (w, {z})
                            break
                    if witness: break
                if witness: break
        if witness is None:
            candidates[name] = {"valid_on_given_finite_frame":True, "counterexample":None}
            continue
        world, true_at = witness
        cm = copy.deepcopy(model)
        for v in worlds:
            cm["predicates"][v]["Probe"] = [[]] if v in true_at else []
        if holds(axioms[name], cm, world):
            raise Invalid("internal modal counterexample did not verify")
        candidates[name] = {"valid_on_given_finite_frame":False,
                            "counterexample":{"world":world, "true_at":sorted(true_at),
                                              "axiom":axioms[name], "model":cm}}
    return {"protocol":PROTOCOL, "status":"FINITE_AXIOM_LIBRARY_ANALYZED",
            "candidate_axioms":candidates,
            "selected_frame_logics":classify_frame(model)["satisfies_frame_conditions_for"],
            "scope":"this supplied finite frame only, for the fixed K/T/4/5 axiom library",
            "unrestricted_logic_synthesis":False, "external_authorization":False}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task",choices=["proof","frame","model","explore_axioms"],required=True)
    ap.add_argument("--max-steps",type=int,default=MAX_STEPS)
    args=ap.parse_args()
    raw = sys.stdin.read(131073)
    if len(raw) > 131072:
        raise Invalid("input exceeds 128 KiB")
    input_doc=json.loads(raw)
    if args.task=="proof":
        result=prove_bounded(input_doc["premises"],input_doc["goal"],max_steps=args.max_steps)
    elif args.task=="frame":
        result=classify_frame(input_doc["model"])
    elif args.task=="explore_axioms":
        result=explore_axioms(input_doc["model"])
    else:
        formula=input_doc["formula"]
        result={"protocol":PROTOCOL,"status":"FINITE_MODEL_CHECKED",
                "holds":holds(formula,input_doc["model"],input_doc["world"]),
                "scope":"the given finite model and world only","external_authorization":False}
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    main()
