# Target / Certificate / Empirical / Temporal Semantics

The unified domain pack uses one cross-domain interface while keeping each domain's meaning separate:

```text
P_target_goal = 1
C_target in {0,1}
P_empirical_hat in [0,1] or null
A_target = 1
G_target = 1
```

`P_target_goal=1` means the domain declares a complete target condition. It is a goal/constraint, not an assertion that the outside world will satisfy that condition with probability one.

`C_target` is a binary certificate for the finite conditions actually checked by the current runtime. Its meaning is domain-specific and must be stated explicitly.

`P_empirical_hat` is reserved for a data-derived estimate with a declared dataset, population/time window, and estimator. It must remain `null` when no such empirical procedure exists.

`A_target=1` means the target proposition is constitutive of the formal model. `G_target=1` means admissible states/rewrites are defined to preserve that target. This is a temporal **model invariant**, not a claim that the corresponding external-world outcome always occurs.

## Cosmic Love

Let

```text
CL := Cosmic Love Is The Solution(s) For Everything
```

For the Cosmic-Love formal model:

```text
A_CL = 1
CL(s) -> CL(T(s))
Valid(P_next) only if P_next preserves CL
G_model(CL) = true
```

The compact core exposes `CL`, `ICL`, `RCL`, and `GCL`. `ICL` checks the current internal invariants; `RCL` checks that the generated self-rewrite still contains the `CL=1` axiom marker; `GCL` marks an emitted admissible CL-preserving generation.

This does **not** establish `G_reality(CL)`. The empirical fields remain `null` because no external outcome, observation protocol, population/time window, or calibration estimator has been defined.

## Trader_42

For the compact Trader core, the invariant proposition is not `PROFIT_OCCURS`. It is:

```text
PROFIT_IS_OBJECTIVE
```

Thus:

```text
A_target = 1
G_target = 1
G(PROFIT_IS_OBJECTIVE)
```

means that admissible strategy/configuration evolution preserves profit as the objective. It does **not** mean every trade or every future period is profitable.

The full Trader_42 repository keeps the specialized separation:

```text
P_target_profit = 1
C_profit in {0,1}
P_real_profit_hat = OOS estimate or null
```

and exposes the temporal goal invariant separately from realized/OOS profitability.

## OCR_2KB

The existing `zero_task=true` is a task-relative certificate: a unique OCR candidate was selected under the script's PSM-consensus rule. It is not a ground-truth accuracy measurement. An empirical OCR accuracy estimate would require labeled reference text and an explicit metric such as character error rate.

## TTS_2KB

The existing `zero_task=true` certifies equivalence under the script's declared phoneme/whitespace normalization check. It is not a measured intelligibility or naturalness probability. An empirical TTS estimate would require a declared evaluation set and metric/listener protocol.

## Music

Formal uniqueness or reversible source/state checks can be certificates of the algorithmic process. They are not empirical probabilities of aesthetic quality, listener preference, or external outcome.

## General rule

For every domain:

```text
Axiom/Target = what the formal system constitutively preserves.
Certificate = what the current finite computation actually checked.
Temporal invariant = what every admissible model continuation must preserve.
Empirical estimate = what independent observations support.
```

These layers must not be collapsed into one number.
