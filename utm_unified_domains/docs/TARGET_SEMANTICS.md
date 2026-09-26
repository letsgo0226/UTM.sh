# Target / Certificate / Empirical Semantics

The unified domain pack uses one cross-domain interface while keeping each domain's meaning separate:

```text
P_target_goal = 1
C_target in {0,1}
P_empirical_hat in [0,1] or null
```

`P_target_goal=1` means the domain declares a complete target condition. It is a goal/constraint, not an assertion that the outside world will satisfy that condition with probability one.

`C_target` is a binary certificate for the finite conditions actually checked by the current runtime. Its meaning is domain-specific and must be stated explicitly.

`P_empirical_hat` is reserved for a data-derived estimate with a declared dataset, population/time window, and estimator. It must remain `null` when no such empirical procedure exists.

## Domain mappings

### Trader_42 core in this pack

The compact `domains/Trader_42.sh` has no market dataset or PnL estimator. Therefore:

- `P_target_goal=1`: formal target enabled.
- `C_target=1`: the current prime/Gödel/reconstruction-side invariants represented by `C` pass.
- `P_empirical_hat=null`: this compact core does not estimate trading profitability.

The separate full Trader_42 repository exposes the specialized aliases `P_target_profit`, `C_profit`, and `P_real_profit_hat`, with the empirical value derived only from out-of-sample walk-forward folds when enough data exist.

### Cosmic Love core

- `P_target_goal=1`: formal/symbolic target enabled.
- `C_target=1`: the current internal invariants plus self-rewrite/syntax/size checks pass.
- `P_empirical_hat=null`: there is no defined external measured outcome, sampling population, or calibration procedure in this runtime.

`C_target=1` therefore does not establish a physical, cosmological, social, psychological, or spiritual external-world effect.

### OCR_2KB

The existing `zero_task=true` is the natural task-relative certificate: a unique OCR candidate was selected under the script's PSM-consensus rule. It is not a ground-truth accuracy measurement. An empirical OCR accuracy estimate would require labeled reference text and an explicit metric such as character error rate.

### TTS_2KB

The existing `zero_task=true` certifies equivalence under the script's declared phoneme/whitespace normalization check. It is not a measured intelligibility or naturalness probability. An empirical TTS estimate would require a declared evaluation set and metric/listener protocol.

### Music

Formal uniqueness or reversible source/state checks can be certificates of the algorithmic process. They are not empirical probabilities of aesthetic quality, listener preference, or external outcome.

## General rule

For every domain:

```text
Target = what the system is trying to satisfy.
Certificate = what the current finite computation actually checked.
Empirical estimate = what independent observations support.
```

These three layers must not be collapsed into one number.
