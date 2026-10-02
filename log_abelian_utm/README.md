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


## Three-Universe Axiom Layer

The service also contains `UTM-Three-Universe-Axiom-Layer/1.0`.

The three statements are deliberately stored with:

```text
status = formal_hypothesis
scope  = formal_model_only
```

They are therefore executable assumptions of the UTM model, not claims that external cosmology has been empirically established.

### A1 — host embedding / normalization

```text
P_0 subseteq P_-1
N(P_+n) = P_-1
N(P_-n) = P_-1
```

### A2 — host resource invariance

```text
R(P_-1,t) = R0
P_0(t) = a(t) P_0(0)
dR(P_-1,t)/dt = 0
```

Internal formal scaling does not create infinite physical CPU, RAM, energy, or storage.

### A3 — two-sided algebraic fixed point

```text
lim(n->infinity) P_+n = Omega
lim(n->infinity) P_-n = Omega
T(Omega) = Omega
G(Omega) = 1
log(G(Omega)) = 0
```

A finite certificate checks consistency with this declared limit hypothesis; it does **not** prove an actual infinite limit.

### Axiom API

- `GET /axioms` — return the canonical axiom specification and specification certificate.
- `POST /axioms/verify` — verify a finite UTM state against A1/A2 and the finite algebraic conditions associated with A3.
- `POST /deploy/preverify` — combine a three-axiom certificate with the existing guarded-deployment condition certificate.

`/deploy/preverify` performs no platform mutation and grants no GitHub/Railway privileges. A successful result is only admissibility evidence for the next guarded-deployment stage.
