# Pure-UTM scalar valuation addition.
# Input:  1^m#1^n
# Output: 1^(m+n)
# The machine replaces # by 1, scans to the right end,
# then erases exactly one 1 to compensate for the separator.
0 1 -> 0 1 R
0 # -> 1 1 R
1 1 -> 1 1 R
1 _ -> 2 _ L
2 1 -> 3 _ S
