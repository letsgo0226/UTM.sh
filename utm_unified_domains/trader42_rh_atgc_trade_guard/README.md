# Trader-42-RH-ATGC-TradeGuard/1.0

Guard-only deployment of the Trader_42 trading principle.

This service never sends exchange orders and contains no exchange credentials. It evaluates a candidate transition and either preserves the requested BUY/SELL candidate or fails closed to HOLD.

## Principle

```text
Signal -> TM candidate -> risk gate -> RH/GC critical certificate -> candidate allow/HOLD
```

The Riemann-critical term is a design invariant only:

```text
GC(w)=K <=> log(B^GC(w))/log(B^(2K)) = 1/2
```

It is not a proof of the Riemann hypothesis and does not test zeta zeros.

## ATGC certificate

The canonical candidate JSON is encoded byte-for-byte into an A/T payload and prefixed with exactly `K` G symbols:

```text
w = G^K || AT_payload(canonical_candidate)
```

Hence `GC(w)=K` by construction, while the A/T payload remains injective for the canonical body. The service also returns a base-4 sentinel UID.

## Existing Trader_42 constraints preserved

- Kernel gate requires `C=true` and `CF != false`.
- BUY must be `FLAT -> LONG`.
- SELL must be `LONG -> FLAT`.
- HOLD keeps capital state unchanged.
- Quote must be nonnegative and no larger than the hard cap.
- Volatility factor must be in `[0,1]`; it cannot increase position size.
- Active KILL fails closed to HOLD.

These mirror the repository's transactional-TM and decrease-only sizing principles. They do not guarantee profit or execution quality.

## HTTP

- `GET /health`
- `GET|POST /selftest`
- `POST /evaluate`
- `POST /verify`

No endpoint places an order.
