# UFAL_NATIVE

UFAL means **Unique Factorization Additive Log Principle**.

For a finite-support state

```text
m = (m_0,m_1,...)
```

the canonical exact encoding is

```text
Gamma(m) = product_i p_i^m_i
```

and, for one fixed logarithm base `c>0, c!=1`, the derived coordinate is

```text
Lambda_c(m) = sum_i m_i log_c(p_i).
```

Unique prime factorization gives an exact bijection between `m` and `Gamma(m)`. On this canonical domain, exact equality of `Lambda_c` also implies equality of the exponent vectors. Floating-point logarithms are never used as authoritative identity checks.

The sum identifies the canonical prime-exponent multiset, not an arbitrary ordered list of summands. When causal replay matters, subsystem/role/step metadata is encoded into the prime index itself.
