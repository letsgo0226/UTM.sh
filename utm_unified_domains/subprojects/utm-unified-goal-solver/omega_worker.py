#!/usr/bin/env python3
"""
UTM-Omega Infinite Continuation Goal Solver
--------------------------------------------
A resident worker for the existing UTM universe runtime.

Formal meaning of "infinite":
- the continuation index has no built-in terminal stage;
- every stage performs finite work;
- a Cantor dovetail enumerates finite (program, model, horizon, seed) tuples;
- no claim of infinite physical CPU/RAM or guaranteed real-world outcomes is made.
"""
from __future__ import annotations
import json, math, os, random, time
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.request import Request, urlopen

PROTOCOL = "UTM-Omega-Infinite-Continuation-Solver/1.0"
WORLD_ID = os.getenv("WORLD_ID", "akashic-utm-main")
AGENT_ID = "utm-omega-goal-solver"
STATE_PATH = Path(os.getenv("UTM_OMEGA_STATE", "/data/utm-omega-goal.json"))
INTERVAL = max(0.25, float(os.getenv("UTM_OMEGA_INTERVAL", "2")))
PORT = int(os.getenv("PORT", "8080"))
API = os.getenv("UTM_API", f"http://127.0.0.1:{PORT}")
MAX_POST_BYTES = 60000

GOALS = {
    "A_societal_world": [
        "no_war","no_coercion","rights_and_civilian_protection","inclusive_dialogue",
        "human_ai_cooperation","wellbeing_health","ecological_sustainability",
        "economic_technical_resilience","information_ecology"
    ],
    "B_sovereignty_habitat": [
        "cognitive_sovereignty","acoustic_sovereignty","room_in_room_sanctuary",
        "reversibility_and_exit"
    ],
    "C_knowledge_memory": [
        "knowledge_preservation","provenance","canonical_snapshot","akashic_bibliotheca"
    ],
    "D_utm_meta_system": [
        "computability","well_definedness","invariants","composability","resident_admission",
        "recursive_lineage","continuation","self_description","bounded_resources"
    ],
    "E_formal_research_targets": [
        "formal_zero_conditional_entropy","omega_fixed_point","godel_riemann_coordinates",
        "ouroboros_self_reference","dream_branching","44th_sunset_continuation",
        "collision_to_transition","heat_death_to_persistent_information",
        "longevity_omni_health","cosmic_love_attractor"
    ],
}

FIELDS = (
    "conflict","coercion","rights","agency","wellbeing","ecology","cooperation",
    "trust","knowledge","sovereignty","noise","resource_stress"
)

@dataclass(frozen=True)
class World:
    conflict: float=.48
    coercion: float=.18
    rights: float=.82
    agency: float=.90
    wellbeing: float=.58
    ecology: float=.56
    cooperation: float=.46
    trust: float=.45
    knowledge: float=.72
    sovereignty: float=.70
    noise: float=.30
    resource_stress: float=.42
    def clamp(self):
        return World(**{k:max(0.0,min(1.0,v)) for k,v in asdict(self).items()})

@dataclass(frozen=True)
class Model:
    name: str
    conflict: float=0.0
    coercion: float=0.0
    ecology: float=0.0
    distrust: float=0.0
    noise: float=0.0
    resources: float=0.0

BASE_MODELS = (
    Model("baseline"),
    Model("resource_shock", conflict=.008, resources=.025),
    Model("distrust", conflict=.006, distrust=.025),
    Model("ecological_stress", ecology=.020, resources=.010),
    Model("habitat_noise", noise=.040, distrust=.010),
    Model("combined_stress", conflict=.010, coercion=.006, ecology=.010,
          distrust=.012, noise=.018, resources=.015),
)

ACTIONS = (
    "MEDIATE","TRANSPARENCY","COOPERATE","AID","PROTECT","RESTORE",
    "QUIET","ARCHIVE","NOOP","COERCE"
)
DELTA = {
    "MEDIATE":(-.060,0,.010,.004,.012,0,.035,.040,.002,.004,0,-.006),
    "TRANSPARENCY":(-.015,-.020,.020,.020,.004,0,.020,.060,.020,.025,0,0),
    "COOPERATE":(-.028,0,.012,.010,.020,0,.060,.045,.010,.010,0,-.018),
    "AID":(-.020,0,.018,.005,.065,0,.020,.020,.004,.005,0,-.045),
    "PROTECT":(-.030,-.010,.055,.020,.012,0,.010,.010,.002,.025,0,0),
    "RESTORE":(-.008,0,.008,.002,.015,.070,.012,.008,.004,.005,0,-.020),
    "QUIET":(-.006,0,.003,.008,.018,0,.004,.010,.002,.070,-.090,0),
    "ARCHIVE":(0,0,.002,.003,.003,0,.006,.012,.065,.006,0,0),
    "NOOP":(0,0,0,0,0,0,0,0,0,0,0,0),
    "COERCE":(-.090,.100,-.080,-.130,.005,0,-.040,-.090,0,-.080,-.010,-.010),
}
CONDITIONS = (
    ("CONFLICT_HIGH",lambda s:s.conflict>=.35),
    ("COERCION_HIGH",lambda s:s.coercion>=.18),
    ("RIGHTS_LOW",lambda s:s.rights<=.78),
    ("WELLBEING_LOW",lambda s:s.wellbeing<=.62),
    ("ECOLOGY_LOW",lambda s:s.ecology<=.60),
    ("COOP_LOW",lambda s:s.cooperation<=.55),
    ("TRUST_LOW",lambda s:s.trust<=.55),
    ("KNOWLEDGE_LOW",lambda s:s.knowledge<=.70),
    ("SOVEREIGNTY_LOW",lambda s:s.sovereignty<=.70),
    ("RESOURCE_STRESS_HIGH",lambda s:s.resource_stress>=.35),
)
CMAP = dict(CONDITIONS)
RULE_ATOMS = tuple((c,a) for c,_ in CONDITIONS for a in ACTIONS)

HARD = {
    "max_coercion": .38,
    "min_rights": .45,
    "min_agency": .45,
    "catastrophic_conflict": .93,
}
W = {
    "conflict":8.0,"coercion":5.0,"rights_gap":3.0,"agency_gap":3.0,
    "wellbeing_gap":2.5,"ecology_gap":1.5,"cooperation_gap":1.8,
    "trust_gap":1.5,"knowledge_gap":.8,"sovereignty_gap":1.3,
    "noise":1.0,"resource_stress":2.0,
}

@dataclass(frozen=True)
class Program:
    rules: tuple
    default: str
    def decide(self, s):
        for condition, action in self.rules:
            if CMAP[condition](s):
                return action
        return self.default
    def canonical(self):
        return json.dumps(
            {"rules":[list(x) for x in self.rules],"default":self.default},
            sort_keys=True,separators=(",",":")
        )
    def pretty(self):
        a=[f"IF {c} -> {x}" for c,x in self.rules]
        a.append(f"ELSE -> {self.default}")
        return "; ".join(a)
    def address(self):
        b=self.canonical().encode("utf-8")
        return {
            "encoding":"utf8-int",
            "integer":str(int.from_bytes(b,"big")),
            "byte_length":len(b),
            "reversible":True,
        }

def cantor_unpair(z: int):
    w=(math.isqrt(8*z+1)-1)//2
    t=w*(w+1)//2
    y=z-t
    x=w-y
    return x,y

def dovetail4(n: int):
    left, seed = cantor_unpair(n)
    left, depth = cantor_unpair(left)
    program_i, model_i = cantor_unpair(left)
    return program_i, model_i, depth, seed

def work_from_stage(n: int):
    """
    Hybrid fair schedule:
    - 75% of stages rapidly scan a new program on the baseline finite test.
    - 25% run the full Cantor N^4 dovetail.
    The second stream alone is a bijective enumeration of every finite
    (program, model, depth, seed) tuple, while the first accelerates discovery.
    """
    q,r=divmod(n,4)
    if r<3:
        return 3*q+r,0,0,0,"accelerated-program-prefix"
    return (*dovetail4(q),"universal-cantor-dovetail")

def program_from_index(index: int) -> Program:
    # Shortlex over all finite rule lists, with a default action.
    A=len(ACTIONS); B=len(RULE_ATOMS)
    x=index
    rules_n=0
    block=A
    while x>=block:
        x-=block
        rules_n+=1
        block=A*(B**rules_n)
    default=ACTIONS[x % A]
    x//=A
    rules=[]
    for _ in range(rules_n):
        rules.append(RULE_ATOMS[x % B])
        x//=B
    return Program(tuple(rules),default)

def radical_inverse(n: int, base: int) -> float:
    x=0.0; f=1.0/base
    while n:
        n,r=divmod(n,base)
        x+=r*f
        f/=base
    return x

def model_from_index(i: int) -> Model:
    if i < len(BASE_MODELS):
        return BASE_MODELS[i]
    n=i-len(BASE_MODELS)+1
    ps=(2,3,5,7,11,13)
    u=[radical_inverse(n,p) for p in ps]
    # Countably infinite deterministic, bounded stress family.
    return Model(
        f"halton_stress_{i}",
        conflict=.020*u[0],
        coercion=.012*u[1],
        ecology=.025*u[2],
        distrust=.030*u[3],
        noise=.050*u[4],
        resources=.035*u[5],
    )

def transition(s,a,m,rng):
    v=[getattr(s,k)+d for k,d in zip(FIELDS,DELTA[a])]
    q=dict(zip(FIELDS,v))
    q["conflict"]+=.018*q["resource_stress"]+.014*(1-q["trust"])+m.conflict
    q["coercion"]+=m.coercion
    q["rights"]-=.015*q["coercion"]+.006*q["conflict"]
    q["agency"]-=.020*q["coercion"]
    q["wellbeing"]-=.018*q["conflict"]+.006*q["noise"]
    q["trust"]-=.012*q["conflict"]+.015*q["coercion"]+m.distrust
    q["cooperation"]-=.009*q["conflict"]
    q["resource_stress"]+=.014*(1-q["ecology"])+m.resources
    q["ecology"]-=m.ecology
    q["noise"]+=m.noise
    q["sovereignty"]-=.012*q["noise"]+.010*q["coercion"]
    q["knowledge"]+=.004*q["cooperation"]
    for k in ("conflict","wellbeing","trust","resource_stress","noise"):
        q[k]+=rng.uniform(-.006,.007)
    return World(**q).clamp()

def loss(s):
    return (
        W["conflict"]*s.conflict + W["coercion"]*s.coercion
        + W["rights_gap"]*(1-s.rights) + W["agency_gap"]*(1-s.agency)
        + W["wellbeing_gap"]*(1-s.wellbeing) + W["ecology_gap"]*(1-s.ecology)
        + W["cooperation_gap"]*(1-s.cooperation) + W["trust_gap"]*(1-s.trust)
        + W["knowledge_gap"]*(1-s.knowledge) + W["sovereignty_gap"]*(1-s.sovereignty)
        + W["noise"]*s.noise + W["resource_stress"]*s.resource_stress
    )

def evaluate_item(p: Program, model: Model, horizon: int, seed: int):
    # Fail closed: a policy capable of selecting the explicit coercive primitive
    # is not admitted to the feasible set.
    if p.default=="COERCE" or any(a=="COERCE" for _,a in p.rules):
        return {"feasible":False,"reason":"syntactic_coercive_primitive_rejected"}
    s=World(); rng=random.Random(seed); total=0.0
    ex={"max_conflict":0.0,"max_coercion":0.0,"min_rights":1.0,"min_agency":1.0}
    for t in range(horizon):
        s=transition(s,p.decide(s),model,rng)
        ex["max_conflict"]=max(ex["max_conflict"],s.conflict)
        ex["max_coercion"]=max(ex["max_coercion"],s.coercion)
        ex["min_rights"]=min(ex["min_rights"],s.rights)
        ex["min_agency"]=min(ex["min_agency"],s.agency)
        if (
            s.coercion>HARD["max_coercion"]
            or s.rights<HARD["min_rights"]
            or s.agency<HARD["min_agency"]
            or s.conflict>HARD["catastrophic_conflict"]
        ):
            return {"feasible":False,"reason":"hard_constraint_violation",**ex}
        total+=(.985**t)*loss(s)
    return {
        "feasible":True,
        "loss":total/horizon + .01*(1+len(p.rules)),
        "horizon":horizon,
        "final":asdict(s),
        **ex,
    }

def default_state():
    return {
        "protocol":PROTOCOL,
        "world_id":WORLD_ID,
        "agent_id":AGENT_ID,
        "compute_mode":"potentially-unbounded-hybrid-dovetail",
        "potentially_unbounded":True,
        "actual_infinite_physical_compute":False,
        "ENUM_COMPLETE":0,
        "stage":0,
        "work_items":0,
        "feasible_items":0,
        "rejected_items":0,
        "max_program_index_seen":-1,
        "max_model_index_seen":-1,
        "max_horizon_seen":0,
        "best_observed":None,
        "goal_registry":{
            "layers":GOALS,
            "goal_count":sum(map(len,GOALS.values())),
            "P_target_goal":1,
            "C_target":0,
            "P_empirical_hat":None,
            "A_target":1,
            "G_target":1,
        },
        "boundary":[
            "Each stage is finite; the stage sequence has no built-in terminal bound.",
            "This is not infinite physical CPU, RAM, energy, or storage.",
            "Best observed means best among completed finite work items, not a proven global optimum.",
            "Formal target preservation is not a guarantee of real-world peace, health, immortality, zero entropy, or cosmological control."
        ],
    }

def load_state():
    try:
        x=json.loads(STATE_PATH.read_text())
        if x.get("protocol")!=PROTOCOL:
            return default_state()
        return x
    except Exception:
        return default_state()

def save_state(x):
    STATE_PATH.parent.mkdir(parents=True,exist_ok=True)
    tmp=STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(x,ensure_ascii=False,separators=(",",":"),sort_keys=True))
    os.replace(tmp,STATE_PATH)

def resident_payload(state):
    # Keep the posted resident under the API's request-size bound.
    view={
        k:state[k] for k in (
            "protocol","world_id","compute_mode","potentially_unbounded",
            "actual_infinite_physical_compute","ENUM_COMPLETE","stage","work_items",
            "feasible_items","rejected_items","max_program_index_seen",
            "max_model_index_seen","max_horizon_seen","best_observed",
            "goal_registry","boundary"
        )
    }
    return {
        "agent_id":AGENT_ID,
        "program_id":PROTOCOL,
        "state":view,
        "memory_checkpoint":f"stage:{state['stage']}",
        "lineage":"utm_unified_domains/subprojects/utm-unified-goal-solver",
    }

def publish(state):
    body=json.dumps(resident_payload(state),ensure_ascii=False,separators=(",",":")).encode()
    if len(body)>MAX_POST_BYTES:
        raise ValueError("resident payload too large")
    req=Request(
        API+"/resident/admit",
        data=body,
        headers={"Content-Type":"application/json"},
        method="POST",
    )
    with urlopen(req,timeout=3) as r:
        r.read()

def step(state):
    n=int(state.get("stage",0))
    pi,mi,depth,seed,schedule=work_from_stage(n)
    p=program_from_index(pi)
    m=model_from_index(mi)
    horizon=8+4*depth
    result=evaluate_item(p,m,horizon,seed)
    state["stage"]=n+1
    state["work_items"]=int(state.get("work_items",0))+1
    state["max_program_index_seen"]=max(int(state.get("max_program_index_seen",-1)),pi)
    state["max_model_index_seen"]=max(int(state.get("max_model_index_seen",-1)),mi)
    state["max_horizon_seen"]=max(int(state.get("max_horizon_seen",0)),horizon)
    state["last_work"]={
        "dovetail_stage":n,"schedule":schedule,"program_index":pi,"model_index":mi,
        "depth_index":depth,"seed":seed,"horizon":horizon,
        "program":p.pretty(),"model":m.name,"result":result,
    }
    if result.get("feasible"):
        state["feasible_items"]=int(state.get("feasible_items",0))+1
        candidate={
            "loss":result["loss"],
            "program_index":pi,
            "program":p.pretty(),
            "canonical":p.canonical(),
            "reversible_address":p.address(),
            "model_index":mi,
            "model":m.name,
            "horizon":horizon,
            "seed":seed,
            "certificate_scope":"one completed finite dovetail work item",
        }
        best=state.get("best_observed")
        if best is None or candidate["loss"] < best["loss"]:
            state["best_observed"]=candidate
    else:
        state["rejected_items"]=int(state.get("rejected_items",0))+1
    state["goal_registry"]["C_target"]=1 if state.get("best_observed") else 0
    return state

def main():
    state=load_state()
    while True:
        started=time.monotonic()
        try:
            state=step(state)
            save_state(state)
            try:
                publish(state)
                state["last_publish_ok"]=True
                state.pop("last_publish_error",None)
            except Exception as e:
                state["last_publish_ok"]=False
                state["last_publish_error"]=str(e)[:200]
                save_state(state)
        except Exception as e:
            state["last_worker_error"]=repr(e)[:500]
            save_state(state)
        elapsed=time.monotonic()-started
        time.sleep(max(0.0,INTERVAL-elapsed))

if __name__=="__main__":
    main()
