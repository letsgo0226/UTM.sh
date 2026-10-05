# Riemann Proof-Carrying UTM

This subproject is a deployable, bounded research kernel integrating the repository's recurring design ideas without claiming results that the code does not establish.

Core chain:

    finite object
      -> canonical JSON
      -> reversible base-257 Goedel integer
      -> bounded transition-table UTM
      -> Dirichlet address n^-s (Re(s)>1 diagnostic)
      -> recomputable certificate
      -> proof-carrying candidate gate
      -> finite-stage continuation

The Riemann layer is a representation/benchmark layer. It does **not** claim that the classical zeta function is literally a UTM, that RH has been proved, or that a candidate passing the finite gate is ASI.

The hard constraints preserve finite executed stages, no oracle/hypercomputation, human agency, non-coercion, rollback, authorized shutdown, and formal/empirical separation.

## API

- GET /health
- GET /manifest
- POST /encode
- POST /verify
- POST /utm/run
- POST /riemann/coordinate
- POST /candidate/verify

### Example UTM request

    {
      "program":"0,A,1,F,R;1,A,2,I,R;2,A,3,E,R;3,A,4,L,R;4,A,H,D,R",
      "input":"AAAAA",
      "limit":100
    }

Expected output tape: FIELD.

## Deployment

Railway: set the service root directory to /utm_unified_domains/riemann_proof_asi and use the included railway.toml.

Render: Python web service, root directory utm_unified_domains/riemann_proof_asi, build command "python3 -m py_compile core.py server.py && python3 -m unittest -v test_core.py", start command "python3 server.py", health check /health.
