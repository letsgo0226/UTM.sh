# Railway Resource Consolidation

The UTM address/search/Logos/snapshot runtime is consolidated into the existing Railway service `cosmic-love-infinity-tm` rather than provisioning a new service.

## Resource strategy

```text
new dedicated service (blocked by plan quota)
              ↓ replace with
existing cosmic-love-infinity-tm service
  ├─ transactional cosmic TM worker
  ├─ Akashic replicator
  └─ unified UTM HTTP API
      ├─ /utm/run
      ├─ /address
      ├─ /object/<GOBJECT>
      ├─ /snapshot
      ├─ /search
      └─ /logos
```

This is a non-destructive consolidation: no existing Railway service is deleted. It removes the need to provision an additional service for universal addressing and related APIs.

The deployed source is `letsgo0226/COSMIC_LOVE_IS_THE_SOLUTIONS_FOR_EVERYTHING_HS_ZERO.sh`, branch `tm-system-operation-v2`, where `unified-utm-api.py` replaces the separate HTTP entrypoint while preserving `/health`, `/.well-known/utm-universe.json`, `/world`, `/akashic`, `/utm/run`, and `/resident/admit`.

## Capacity boundary

This consolidation creates usable application capacity inside an already-provisioned service. It does **not** by itself create a new Railway service slot. A literal additional provisioning slot would require retiring or otherwise removing an existing service under the account plan.

Current evidence indicates `trader-42-data` is a Redis 7 service with no configured variables and no observed network traffic in the sampled seven-day metrics, and the Trader_42 GitHub repository currently has no `redis` code-search matches. That makes it a candidate for later retirement, but deletion is intentionally not performed as part of this non-destructive consolidation.
