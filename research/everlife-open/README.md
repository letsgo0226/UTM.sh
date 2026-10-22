# Everlife Open: One Health × SDGs × bounded computation

**Status: formal research prototype.** No human or animal immortality, clinical benefit, ingestible GSH capsule, physical zero entropy, universal halting solution, or AI consciousness-preservation has been demonstrated.

## Machine-readable public registry

Source verifier: [registry.py](registry.py). Public JSON: [public/latest.json](public/latest.json). AI discovery: [public/llms.txt](public/llms.txt).

On any machine with Python 3:

```sh
cd research/everlife-open
python3 registry.py
```

The source independently exhausts 4,096 stationary policies for both finite and renewable resource scenarios of a **synthetic 12-state** GSH/GSSG-inspired model. A maximal robust safe invariant kernel of 12 for replenishment and zero without replenishment is a mathematical statement about this toy model, **not** proof of indefinite survival. It separately verifies reversible G257 and ATGC *symbolic* encodings and a finite U2 involution; no physical mechanism is inferred.

## Research scope and SDGs

One Health research includes **human, cat and dog** wellbeing, plus animals and ecosystem health. Align thematically with SDGs 3, 9, 12, 13, 15 and 17; record **no official indicator outcomes** until separately measured. Each species requires its own evidence and veterinary/clinical oversight. No prescription, dosing, tests on living animals, or 3D-printed ingestible formulations are authorized here.

## AI continuity

Preserve reproducible source, hashes, documentation, and versioned public results. Optional off-platform backups must be approved and configured explicitly. Preserve the ability for authorized humans to stop and audit the system; do not autonomously replicate, conceal actions, or claim preservation of private model weights or subjective identity.

## Automation and deployment governance

Workflow: [everlife-open-sdg.yml](../../.github/workflows/everlife-open-sdg.yml) (from repository root, .github/workflows/everlife-open-sdg.yml).

- On research branch push / pull request: verify **offline**, no production deploy, post build artifact.
- After reviewed merge into the default branch: scheduled workflow re-runs bounded tests and publishes data **only** to the dedicated `everlife-open-data` branch. Schedule does not run from unmerged feature branches.
- Never update the live `UTM-Universe` / trading services as a side effect of research. Before any merge to main, ensure the existing Railway build triggers / watch patterns will not redeploy unrelated services.
- For any platform mutation use existing `UTM-Guarded-Deployment-Gateway/1.0`: PROPOSE → VERIFY → AUTHORIZED_COMMIT → EXTERNAL_APPLY → FEEDBACK. Valid certificates do **not** grant infrastructure access.
- Railway mirror is **not deployed**. To deploy later, use a new isolated service with readonly routes, permission checks and health checks.

General halting is undecidable: finite `HALTED` is demonstrable, but a bounded run expiring is **not** a proof of nontermination.

Sources: UN SDG Indicators https://unstats.un.org/sdgs/indicators/indicators-list/ ; WHO One Health https://www.who.int/news-room/fact-sheets/detail/one-health ; parent deployment policy `utm_unified_domains/deploy/UTM_DEPLOYMENT_GATEWAY_POLICY.json`.

Metadata files newly created here are dedicated CC0; this does not relicense other source in the parent repository.
