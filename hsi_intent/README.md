# HSI Intent Field v1

HSI Intent Field turns long-running project goals, invariants, hypotheses and claim boundaries into a finite, canonical registry that can be checked alongside ordinary HSI state-transition certificates.

It does **not** treat conversation text as truth. It classifies persistent ideas into typed atoms such as GOAL, INVARIANT, HYPOTHESIS and CLAIM_BOUNDARY. A transition may advance, preserve, defer, violate or explicitly resolve atoms. Violating an active hard invariant or claim boundary fails closed.

The seed registry includes the recurring UTM / Trader_42 / Omega goals, finite-resource semantics, provenance/replayability, human agency, global conflict-reduction goals, dialogue/repair, ecological and information goals, the global morphogenesis hypothesis, and explicit boundaries against guaranteed peace, guaranteed profit, hypercomputation, global-optimum claims and unsupported physical conclusions.

The certificate contains a canonical registry digest and transition UID. The field is intentionally **non-executing**: it has no authority to place trades, change deployment modes, manipulate users, or assert that a modeled trajectory will occur in the real world.

Run:

```sh
cd hsi_intent
python3 -m unittest -v test_core.py
```

Future dialogue-derived atoms should be added incrementally with provenance and explicit status changes such as SUPERSEDED, REJECTED or DEPRECATED rather than silently deleting persistent goals.
