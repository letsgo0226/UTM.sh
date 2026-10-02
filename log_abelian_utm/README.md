# Logarithmic Abelian UTM

This module adds an Abelian **representation layer** to the existing UTM toolchain without claiming that ordinary UTM state transitions commute.

## Kernel

For positive encoded states `a,b`:

```
x = log(a)
y = log(b)
x + y = log(a) + log(b) = log(ab)
```

A finite event `(step, op)` is mapped to a unique natural number by Cantor pairing and then to the corresponding prime:

```
(step,op) -> cantor(step,op) -> p_n
```

A finite event multiset is represented by the Gödel product

```
G = product p_n
```

and its logarithmic coordinate is

```
L = log(G) = sum log(p_n).
```

Multiplication of Gödel products is commutative, so composition in the representation layer is Abelian. The `step` coordinate is embedded inside each prime identity, so decoding can still reconstruct causal order.

## Important limit

This does **not** imply that arbitrary UTM program composition is commutative. It only makes the encoded information aggregate commutative while preserving enough metadata to reconstruct ordered computation.

## API

- `GET /health`
- `GET /spec`
- `POST /encode` with `{"events":[{"step":0,"op":1}]}`
- `POST /compose` with `{"left":[...],"right":[...]}`
- `POST /decode` with `{"godel":"..."}`

Example:

```sh
curl -s "$BASE/compose" \
  -H 'content-type: application/json' \
  -d '{"left":[{"step":0,"op":1},{"step":1,"op":2}],"right":[{"step":2,"op":0}]}'
```

The response includes checks for:

- `product_identity`
- `commutative_product`
- `commutative_log`
- `causal_order_recoverable`

This is a formal/computational representation. It does not establish physical zero entropy or a metaphysical claim.
