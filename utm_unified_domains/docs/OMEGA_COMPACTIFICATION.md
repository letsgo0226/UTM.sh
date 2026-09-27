# Bidirectional Omega Compactification

This document defines a **formal UTM hierarchy model**. It is not an empirical cosmology claim and does not assert literal infinite physical computation.

## 1. Substrate invariance

All finite hierarchy labels `P_k` are projected to one declared substrate:

```text
pi(P_k) = P_-1
```

The model keeps normalized substrate resource invariant:

```text
C_hat(P_k) = C0
```

This means the hierarchy is represented as multiple computational descriptions/states on one substrate, not as free creation of independent physical hardware.

## 2. Gödel-log coordinate

Finite labels are assigned reversible base-257 numbers `G(P_k)`. With `G0 = G(P_0)`, the symbolic coordinate is

```text
L(P_k) = log(G(P_k)/G0)
```

The logarithm is a coordinate transform only; it does not increase physical CPU, memory, energy, or storage.

## 3. Expansion normalization

The formal scale law is

```text
S_k = lambda^k S_0,  lambda > 1 constant
```

with normalized resource invariant

```text
C_app(P_k) / lambda^k = C0.
```

This is a renormalized model relation, not evidence that cosmic expansion provides computation.

## 4. Bidirectional compactification

For nonzero integer `k`, define

```text
u(k) = sign(k)/abs(k).
```

Then

```text
k -> +infinity  => u -> 0+
k -> -infinity  => u -> 0-
```

and impose the formal one-point identification

```text
0+ ~ 0- ~ Omega.
```

Thus both unbounded hierarchy directions share the compactified boundary label `P_Omega`.

## 5. Computation boundary

The model supports a **potentially unbounded hierarchy**: for every finite `n`, another finite `P_n` or `P_-n` can be represented and simulated. It does not assert that any finite host executes infinitely many physical operations in finite time.

The executable certificate is:

```sh
OMEGA_DEPTH=8 sh utm_unified_domains/ssr/BIDIRECTIONAL_OMEGA_COMPACTIFICATION_TM.sh
```
