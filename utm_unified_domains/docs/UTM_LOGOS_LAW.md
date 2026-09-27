# UTM-Universe Logos Law

This document defines a **model-internal formal principle**. It is not presented as an established law of metaphysics, theology, or physics.

## Core distinction

Let a concept `I` be articulated by propositions `P` and `Q` inside a declared admissible state space `U`.

`I` is possible in the model iff at least one admissible state satisfies both `P` and `Q`:

```text
◇U I  :=  ∃s∈U : s ⊨ P ∧ Q
```

The dependency `P ⇒ Q` is valid in the model iff there is no admissible counterstate in which `P` is true and `Q` is false:

```text
P ⊨U Q  :=  ¬∃s∈U : s ⊨ P ∧ ¬Q
```

The combined finite Logos certificate is therefore:

```text
LogosU(I;P,Q) := ◇U(P∧Q) ∧ ¬◇U(P∧¬Q)
```

This captures two different claims:

1. **Admissibility** — the concept is not empty in the declared model.
2. **Necessary structural dependence** — within that model, `P` cannot hold while `Q` fails.

## Indivisibility

`Q` may be called essential to `I` in the declared model when retaining `I` while removing `Q` is inadmissible:

```text
¬◇U(I ∧ ¬Q)
```

This is **identity/structural indivisibility**, not a claim that `I` cannot be analyzed into parts. A concept may be analytically decomposable while its essential conditions cannot be removed without changing its identity.

## Important boundary

A finite state list can certify only the declared finite model. It does **not** prove global metaphysical possibility, divine permission, empirical truth, or a universal theological claim. In particular, examples involving God, Forms, or love are treated as propositions supplied to the formal model, not as independently established facts.

## Runtime

`domains/LOGOS_2KB.sh` uses two-bit states:

- `11` = `P ∧ Q`
- `10` = `P ∧ ¬Q`
- `01` = `¬P ∧ Q`
- `00` = `¬P ∧ ¬Q`

Example:

```sh
I='Love-as-principle' P='P' Q='Q' STATES='11,01' sh tools/run-domain.sh logos2
```

Expected interpretation:

```text
possible_I = true
counterpossible_P_and_not_Q = false
valid_P_implies_Q = true
logos_consistent = true
```

The same checker is exposed by the public API implementation at:

```text
/logos?states=11,01&i=I&p=P&q=Q
```
