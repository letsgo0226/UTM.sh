# Trader_42 Native paper-policy gate.
# Input is a host-certified finite class:
# U = bullish/entry-admissible, D = bearish/exit-admissible,
# F = neutral/ambiguous, R = risk-blocked, C = cost-blocked.
# Output symbols: L=PAPER_LONG, X=PAPER_EXIT, H=PAPER_HOLD.
0 U -> A L S
0 D -> A X S
0 F -> A H S
0 R -> A H S
0 C -> A H S
