# TRADER_42_NATIVE

This subproject places Trader_42's **paper-policy semantics** inside the UTM Universe while preserving the existing host-side empirical evaluator.

## Pure-UTM policy

`TRADER_POLICY.tm` receives one finite, host-certified market class and produces only a paper action:

```text
U -> L   PAPER_LONG
D -> X   PAPER_EXIT
F -> H   PAPER_HOLD
R -> H   PAPER_HOLD
C -> H   PAPER_HOLD
```

The market-data importer, continuous indicators, fee/slippage calculations, backtests, and walk-forward OOS estimates remain host-side empirical procedures. The UTM does not claim to observe the market directly.

The target invariant remains:

```text
PROFIT_IS_OBJECTIVE
```

not `PROFIT_ALWAYS_OCCURS`.

There is no exchange-order path, no credential access, and no live-trading authority in this native subproject.
