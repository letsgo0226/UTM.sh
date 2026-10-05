# UTM Generated Function

`UTM-Generated-Function/1.0` is a bounded research kernel that compiles a finite Turing-machine execution trace into exact symbolic function data.

Core relation:

```text
Gamma(delta(C)) = F_U(Gamma(C))
```

For a finite trace `C_0 -> ... -> C_N`, the service produces:

```text
H_U(s,z) = sum_{t=0}^N z^t G_t^(-s)
Xi_N(s)  = product_{t=0}^N [1 + (s-1/2)^2/G_t^2]
P_N(x)   = product_{t=0}^N (x^2 + 4 G_t^2),  x = 2s-1
```

The `Xi_N` zero locations are **defined by construction** as `1/2 +/- i G_t`; this is not a proof of the Riemann Hypothesis and does not claim the classical zeta function is a UTM. The service does not solve the halting problem, use an oracle, perform hypercomputation, prove ASI, enumerate all possible physical universes, or guarantee empirical-world outcomes.

The authoritative state identity is exact reversible base-257 encoding of finite canonical JSON. The spectral and series forms are generated views over that finite trace.

## API

- `GET /health`
- `GET /manifest`
- `POST /encode`
- `POST /verify`
- `POST /utm/trace`
- `POST /function/compile`
- `POST /function/verify`
- `POST /candidate/verify`

### Example

```json
{
  "program": "0,A,1,F,R;1,A,2,I,R;2,A,3,E,R;3,A,4,L,R;4,A,H,D,R",
  "input": "AAAAA",
  "limit": 100
}
```

`/function/compile` returns a finite function bundle plus a recomputable reversible certificate.

## Deployment

Railway service root directory:

```text
/utm_unified_domains/utm_function_generator
```

Render can use repository root with:

```text
build: cd utm_unified_domains/utm_function_generator && python3 -m py_compile core.py server.py && python3 -m unittest -v test_core.py
start: cd utm_unified_domains/utm_function_generator && python3 server.py
```

Every executed stage is finite. Omega means potentially unbounded continuation through further finite stages, not completed infinite physical computation.
