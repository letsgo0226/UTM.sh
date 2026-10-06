# CLS Recursive Fixed Point

`fixed_point.sh` is a one-line, no-SHA, quine-style self-reference prototype.
It reconstructs a canonical Python payload, assigns that payload a reversible base-257 Gödel integer, and emits the integer in its certificate.

HTTP wrapper:
- `GET /health`
- `GET /one-liner`
- `GET /certificate`

Boundaries: this is a finite syntactic self-reference demonstration. It does not prove Kleene's theorem, imply self-awareness, provide an oracle, or guarantee real-world outcomes.

Run:
`python3 -m unittest -v test_runtime.py`
`PORT=8080 python3 server.py`
