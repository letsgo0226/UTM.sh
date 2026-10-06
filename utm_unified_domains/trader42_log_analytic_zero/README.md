# Trader_42 Log-Analytic Zero Kernel

A bounded verification/simulation service integrating Trader_42 invariant preservation with the Analytic-Lift zero-point model.

## Formal core

```
p_formal = exp(-|G|^2)
G = 0  <=>  p_formal = 1
P_total = max(P_AC, P_risk, P_cert, |G|^2)
```

A candidate is certified only when all four formal residuals are zero.

**Important:** `p_formal=1` is a model acceptance condition. It is not a proof that a real trade will profit, not a calibrated market probability, and not permission to bypass risk controls.

The service never places orders.

## API

- `GET /health`
- `GET /manifest`
- `POST /evaluate`
- `POST /transition`
- `POST /encode`

Example:

```json
{"g_re":"0","g_im":"0","continuation_residual":"0","risk_residual":"0","certificate_residual":"0"}
```

The result may be `CERTIFIED_CANDIDATE` or `HOLD`. It is still not an order.

## Invariant principle

This preserves the existing Trader_42 separation:

```
protocol correctness != guaranteed profitability
```

The invariant layer certifies guarded/risk-valid/auditable transitions; market outcome remains external and statistical.
