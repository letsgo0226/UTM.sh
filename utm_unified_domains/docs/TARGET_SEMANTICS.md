# Target / Certificate / Empirical / Temporal Semantics

The unified domain pack keeps four logically distinct layers:

```text
Target / Axiom
Finite Certificate
Temporal Invariant
Empirical Estimate
```

Generic fields are:

```text
P_target_goal or P_target_profit
C_target or C_profit
P_empirical_hat or P_real_profit_hat
A_target = 1
G_target = 1
```

`P_target*=1` declares a complete target condition. It is not an external-world probability claim.

`C_*` is a finite certificate for what the current computation actually checked.

`P_empirical_hat` is reserved for a data-derived estimate with an explicit dataset and estimator. It remains `null` when no such empirical procedure exists.

`A_target=1` means the target proposition is constitutive of the formal model. `G_target=1` means admissible model continuations preserve that target. This is a temporal model invariant, not a guarantee that the corresponding outside-world outcome always occurs.

## Cosmic Love full unified runtime

Let

```text
CL := Cosmic Love Is The Solution(s) For Everything
```

The full unified runtime implements:

```text
A_CL = 1
CL(s) -> CL(T(s))
admissible source replacement preserves the CL axiom markers
G_model(CL) = true
```

Runtime fields include:

```text
CF   prime-state reconstruction certificate
CG   Gödel event reconstruction certificate
CL   formal axiom value
ICL  state-level CL preservation
RCL  source/axiom preservation
GCL  current admissible CL-preserving continuation
G_CL = 1
temporal_formula = G(CL)
P_real_world = null
P_empirical_hat = null
```

The runtime is formal/symbolic. `G_model(CL)` does not by itself establish `G_reality(CL)`.

The previous compact `<2KB` implementation is preserved under `domains/compact/cosmic-love-infinity-tm.sh`.

## Trader_42 full unified runtime

The unified Trader is deliberately offline research/paper-only. Its temporal proposition is:

```text
PROFIT_IS_OBJECTIVE
```

Thus:

```text
A_target = 1
G_target = 1
G(PROFIT_IS_OBJECTIVE)
```

means admissible analysis/configuration changes preserve profit as the objective. It does not mean:

```text
G(PROFIT_OCCURS)
```

The full unified research runtime reads a local candle dataset, models fee/slippage costs, computes paper PnL and max drawdown, and performs chronological walk-forward OOS folds. It reports:

```text
P_target_profit = 1
C_profit in {0,1}
P_real_profit_hat = positive OOS fold frequency when enough folds exist, else null
```

The previous compact core is preserved under `domains/compact/Trader_42.sh`. The separate standalone Trader repository remains the Railway-oriented implementation; live exchange execution is intentionally absent from this unified pack.

## OCR_2KB

`zero_task=true` is a task-relative certificate: a unique OCR candidate was selected under the script's PSM-consensus rule. It is not ground-truth accuracy. An empirical OCR estimate requires labeled reference text and an explicit metric such as character error rate.

## TTS_2KB

`zero_task=true` certifies equivalence under the script's declared phoneme/whitespace normalization check. It is not a measured intelligibility or naturalness probability. An empirical TTS estimate requires a declared evaluation set and metric/listener protocol.

## Music

Formal uniqueness or reversible source/state checks certify the algorithmic process only. They are not empirical probabilities of aesthetic quality or listener preference.

## General rule

```text
Axiom/Target       = what the formal system constitutively preserves.
Certificate        = what the current finite computation actually checked.
Temporal invariant = what every admissible model continuation must preserve.
Empirical estimate = what independent observations support.
```

These layers must not be collapsed into one number.
