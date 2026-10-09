# HSI-UPOK/0.1 — bounded proof and modal meta-logic

This independent, **review-only** kernel explores predicate logic and modal logic as formal HSI operations. It does not change the deployed HSI-3SYS/1.0 core or any trading service.

## Features

- `proof`: bounded forward search using `premise`, `and_left`, `and_right`, `and_intro`, `imp_elim`, `forall_elim`, `exists_intro`. Every successful proof is independently replayed by a rule checker. Unresolved does **not** mean false.
- `model`: predicate-modal formula evaluation in one supplied finite constant-domain Kripke model, where `box` means all accessible worlds and `diamond` means some accessible world.
- `frame`: exact finite-frame correspondence checks for modal logics K, T, S4, S5.
- `explore_axioms`: bounded exploration of a fixed K/T/4/5 axiom library; generates independently evaluated finite counterexamples to unsupported axioms.

## Predicate proof example

```json
{
  "premises": [
    {"op":"forall","var":"x","body":{"op":"imp","left":{"op":"pred","name":"P","args":["x"]},"right":{"op":"pred","name":"Q","args":["x"]}}},
    {"op":"pred","name":"P","args":["a"]}
  ],
  "goal":{"op":"pred","name":"Q","args":["a"]}
}
```

```sh
python3 hsi_common/proof_meta.py --task proof < proof.json
```

Successful output includes `PROVED_WITHIN_BUDGET`, a checked inference trace, a proof integrity digest, and a reversible Gödel integer for sufficiently small proofs. The integer representation and SHA-256 digest serve different purposes.

## Modal meta-logic example

```json
{
  "model":{
    "worlds":["w0","w1"],
    "edges":[["w0","w0"],["w1","w1"],["w0","w1"]],
    "domain":["a"],
    "predicates":{"w0":{},"w1":{}}
  }
}
```

```sh
python3 hsi_common/proof_meta.py --task explore_axioms < model.json
```

For this frame the K/T/S4 conditions hold, but modal axiom 5 fails. The output includes an explicit countermodel.

## Important limitations

- This is **bounded candidate-system analysis**, not unconstrained invention of arbitrary logics.
- Correct finite proofs are verified relative to their given assumptions and explicitly supported deduction rules; the checker does not decide first-order validity or the halting problem.
- Modal results concern the specified finite Kripke frame/model, not all possible universes or proofs of physical facts.
- The syntax supports predicate formulas and modal evaluations but not a complete predicate-modal natural-deduction calculus. Inference rule search is deliberately incomplete.
- A logic engine cannot, in general, establish its own full consistency or reliability merely by claiming an internal verification flag.
- There is no platform mutation, arbitrary remote code execution, source self-modification, trading, GitHub/Railway token usage or deployment authorization.

## Run tests

```sh
python3 -m unittest discover -s hsi_common -p 'test_*.py' -v
```

This module uses bounded input sizes, worlds, domains, proof steps, and semantic evaluation calls. Extending it toward self-deployment requires separate safety reviews, authorization and rollback.
