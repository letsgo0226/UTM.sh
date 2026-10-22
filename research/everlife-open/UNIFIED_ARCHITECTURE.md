# One logical machine, many bounded virtual workloads

Concept: a **single deterministic, logical-time round-robin interpreter** multiplexes multiple G257/ATGC addressed BF8 virtual programs, using finite quotas, integrity hash chain, and a reproducible public manifest.

- A single *logical* Turing machine can emulate any finite catalog of finite programs in principle, subject to storage/time.
- A finite machine does not simultaneously compute infinitely many programs or guarantee availability forever.
- Unbounded enumeration *over time* does not make each stage unlimited; it cannot defeat Railway quotas, platform outages, cost, or the undecidable halting problem.
- A finite bounded non-halting observation must report `BOUNDED_STEPS`/`BOUNDED_GLOBAL`, not mathematically prove a program never halts.
- Here "sync" means deterministic **logical-clock scheduling** and a hash-linked event trace. It is not live cross-host synchronization.
- GitHub Action runs create reproducible JSON evidence. A real-time system would require authenticated webhooks/event queues, durable replicated checkpoints, lease/leader election, idempotent events and recovery plans, plus operational monitoring.
- Every catalog entry currently has `external_apply_enabled=false`. Actual GitHub/Railway changes must continue through `UTM-Guarded-Deployment-Gateway/1.0` plus authenticated, human-approved external apply.
- The service labeled `trader-paper-audit` is a symbolic no-broker workload. No trading actions are allowed.
- The Everlife/One Health program performs no biomedical calculation, dosing or animal experiment; cross-species validation has not occurred. The seventh finite virtual job `diet-cognition-odor` is a synthetic indicator for a **public, nonpersonal protocol only**. It does not observe real diet, cognitive performance, body odor, or patients. The withdrawal-like hypothesis must not be read as validated meat addiction.
- Keep future service workloads as bounded tasks with approved resource envelopes, not long-running unbounded loops. Preserve source/provenance and **authorized shutdown** for any AI-continuity system.

Run: `sh unified.sh` in this directory; output `public/unified-run.json`. Use `python3 -m unittest -v test_resource_guard.py test_unified_machine.py` for verification.

Related: `RESOURCE_LIMITS.md`, `resource_guard.py`, `registry.py`, and `RAILWAY_DEPLOY.md`.
