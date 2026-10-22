# G257 / ATGC finite resource deployment preflight

This is a **bounded engineering admission test**, not an unlimited-storage or universal halting solver.

## Why finite code does not eliminate volume quotas

G257 assigns an integer to finite byte strings and ATGC is an invertible symbolic map. A program interpreter can describe infinitely many candidate programs across arbitrarily long finite lengths, but cannot execute/store all of them at once; no lossless codec makes **all** finite strings shorter. CPU, RAM, disk, energy, and platform allocation stay finite.

## Current architecture

- `registry.py`: reproduce synthetic research certificates, separated from clinical / veterinary evidence.
- `resource_guard.py`: gate on **declared** build bytes, runtime RAM, volume allocation. Missing estimates or live account ceilings => `REVIEW_REQUIRED`; exceeded ceilings => `BLOCK`; all supplied and below ceiling => `PREFLIGHT_PASS` (not deployed). Its internal BF interpreter is step-, output-, and tape-bounded and does not execute shell commands.
- `resource_budget.json`: deliberately unknown live plan limits. It never claims production approval.
- `test_resource_guard.py`: demonstrates bounded and over-budget outcomes.

A reviewer/operator may measure accurate values outside this repository and supply a verified JSON budget. **Do not directly push this preflight verdict into privileged GitHub/Railway deployment operations.**

## Real incident distinctions

- Railway limited access / upstream pause => retry only after platform resumes; cannot be bypassed by G257.
- Missing `start.sh` or unknown builder => configure correct Dockerfile/root directory/start command.
- Build test / locked inventory mismatch => fix or reconcile the failing tests, do not suppress them.
- Volumes over the account's plan => size within plan, upgrade plan where allowed, or move large datasets to approved external object storage. Never delete existing persisted data without backup and explicit authorization.
- High memory / CPU => measure usage, add bounded queues and concurrency, optimize or resize.
- Unrelated monorepo commits => use per-service watch patterns and root directories to avoid unnecessary builds.

No safety claims or quota resolution can be concluded from a single passing unit test. Existing UTM/trading deployments are not modified.

Reference: https://docs.railway.com/deployments/reference ; https://docs.railway.com/builds/build-configuration ; https://docs.railway.com/volumes/reference
