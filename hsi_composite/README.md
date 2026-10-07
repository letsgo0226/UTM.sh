# HSI Composite v1

HSI-COMPOSITE/1.0 directly combines the existing finite HSI state certificate with the HSI Intent Field / Pleiadian Blue certificate.

A request contains two objects bound by the same non-empty `subject_uid`:

- `state`: certified by HSI-3SYS/1.0.
- `intent`: certified by HSI-INTENT/1.1.

The composite closes iff:

```text
state.closed == 1
AND intent.closed == 1
AND state.subject_uid == intent.subject_uid != ""
```

Because HSI-INTENT/1.1 requires every Blue dimension to be explicitly preserved or advanced, a locally valid state transition cannot close as a composite transition if it abandons Agency, Non-coercion, Truthfulness, Care, Dialogue/Repair, or Continuity.

Different transitions and worldlines may produce different `composite_uid` values while sharing the same `blue_uid`.

This service is a certificate layer only. It does not predict outcomes, place trades, change deployment modes, or act on people or institutions.

Run:

```sh
cd hsi_composite
python3 -m unittest -v test_core.py
python3 server.py
```
