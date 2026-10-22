# Everlife Event Bridge v2 — GitHub first, Railway optional read-only

**Deployment state:** GitHub-only draft PR #45, no Railway Everlife service deployed. No action may modify existing UTM, trader, or health systems.

## Implemented flow

1. GitHub `push` / `pull_request` fires the verified pipeline on the research branch. `schedule` or manually authorized workflow dispatch can be used on the default branch **after reviewed merge**.
2. `unified_machine.py` deterministically schedules six synthetic BF jobs with global/per-job step limits and a hash chain. This is **logical-time**, not physical real-time service synchronization.
3. `control_plane.py` reads only allowlisted GitHub event metadata; it never publishes issue/PR content, credentials, payload strings, user email addresses, or arbitrary code.
4. `resource_guard.py` checks a declared finite resource budget. Unknown live quota/measurement => `REVIEW_REQUIRED`, oversubscription => `BLOCK`.
5. `railway_probe.py` is an **optional read-only GraphQL query** of a specified Railway project. Without authorized credentials, it emits `NOT_CONFIGURED`; on outage, `UNAVAILABLE`. Both cases retain CI results with zero Railway mutations.
6. GitHub Actions uploads four versioned artifacts: `latest.json`, `unified-run.json`, `control-plane.json`, `railway-observation.json`. After a reviewed merge to the default branch, scheduled or manual workflow may update the separate `everlife-open-data` branch. **No automatic merge or cloud deployment**.
7. `server.py` exposes the two control-plane routes as **historical CI snapshots**, not live continuous Railway status.

## Connecting Railway observer (requires authorization)

After Railway permits creation, create a **new isolated Everlife-only project** and link a GitHub source to `everlife-open-sdg-v1`, root `/research/everlife-open`, without PR environments. Use the existing `RAILWAY_DEPLOY.md`.

For the GitHub Actions Railway query, use an access token whose scope is limited to **viewing only the isolated Everlife project**, if available (Railway OAuth `project:viewer`). Configure in **GitHub repository Settings → Secrets and variables → Actions**:

- Secret `RAILWAY_OBSERVER_TOKEN`: scoped access token (never commit, log, or disclose).
- Variable `RAILWAY_OBSERVER_PROJECT_ID`: new Everlife Railway project UUID only — **do not supply UTM-Universe or Trader project IDs**.
- Variable `RAILWAY_OBSERVER_TOKEN_KIND`: `oauth` for OAuth Bearer; `project` only for an explicitly approved project-scoped token (`Project-Access-Token` header).

The workflow supplies credentials **only** to scheduled / manually dispatched runs on the default branch, never to pull-request or research branch push builds. A project token may provide more privilege than read-only; prefer the narrowly scoped OAuth `project:viewer` grant. GitHub Secrets do not create or enforce Railway permissions: those must be limited on the Railway side.

Railway API docs: https://docs.railway.com/integrations/api — project token header is distinct from OAuth Bearer.

## Semantics and safety

- All decisions are read-only and do not grant GitHub/Railway authority.
- `VERIFIED_FOR_PROPOSAL_REVIEW_ONLY` is **not permission to deploy**. Actual changes still go through `UTM-Guarded-Deployment-Gateway/1.0`, authenticated platform authorization, explicit human approval and rollback.
- A `NOT_CONFIGURED` or `UNAVAILABLE` observation means no Railway status has been verified in this pipeline; it does **not** mean deployed services are down.
- The published Railway count summary excludes service names, IDs, variables, and internal addresses.
- Workflow schedules are **best-effort**, not real-time guarantees. GitHub push/PR triggers can run near event time; polling Railway once an hour is not a webhook subscription. Genuine cross-platform real-time requires authenticated webhooks, persistent queue, idempotent event consumption, recovery tests and monitoring.
- Machine halting is not generally decidable. The BF interpreter returns `BOUNDED_*` on resource ceilings, not a proof of never halting.
- Public human/cat/dog research remains synthetic. No clinical/veterinary efficacy, physical zero entropy or immortality has been demonstrated.

## Current machine data and testing

```sh
cd research/everlife-open
python3 -m unittest -v test_server.py test_resource_guard.py test_unified_machine.py test_control_plane.py
python3 unified_machine.py
python3 railway_probe.py      # defaults to NOT_CONFIGURED without approved token
python3 control_plane.py     # logs no secrets, writes public/control-plane.json
```

Public result paths: `public/unified-run.json`, `public/control-plane.json`, and `public/railway-observation.json`.

This is a prototype control **observation** plane. It does not eliminate finite CPU/RAM/storage/billing limits, make external deployments, or persist private LLM weights.
