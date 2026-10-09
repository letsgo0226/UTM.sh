# HSI guarded self-deployment: stages 1–2 (review-only)

## Capability boundary

This review branch adds source observation, bounded candidate **metadata** and
review preparation. It does **not** autonomously change deployed software.

- Stage 1: fetch bytes for exactly three files from three pinned
  `hsi-three-system-v1` branches and compare SHA-256.
- Stage 2: when the full audit supports a mismatch, propose a human-reviewed
  source-parity plan against the pinned UTM copy. The planner reads only the
  proposed UTM source, checks UTF-8/Python syntax and digest continuity, and
  emits hashes/references. It **never exports private Trader-42 source bytes**.
- Separate credential-free mock unit tests exercise the planner's fail-closed
  behavior. Python syntax checks are not behavioral compatibility tests.
- Stage 3 (not implemented): review the real candidate code/diff privately,
  perform independent behavioral/security tests in isolation, obtain
  authorization, deploy via an authenticated adapter, then health-check/rollback.

## Stage 1 audit decisions

| Decision | Meaning |
| --- | --- |
| `IN_SYNC` | All three pinned copies were readable and byte-identical in scope |
| `REVIEW_REQUIRED` | All three copies were readable and scoped source drift exists |
| `HOLD_FETCH_ERROR` | At least one copy was inaccessible |
| `HOLD_FORMAL_GATE` | The HSI finite-state gate did not close |

`closed=1` proves neither code correctness nor permission to deploy.

## Stage 2 candidate decisions

| Decision | Meaning |
| --- | --- |
| `CANDIDATES_READY_FOR_REVIEW` | Bounded replacement metadata produced for review |
| `NO_CHANGE` | The scoped audit does not contain a mismatch |
| `HOLD` | Missing, stale, invalid, oversized or contradictory evidence |

Every candidate specifies the current target SHA-256, proposed UTM SHA-256,
file path and source branch. Reviewers must inspect the actual destination
diff and determine whether using the UTM copy is appropriate. **No code fix is
automatically applied.**

The candidate plan does not include private source bytes, an executable patch,
an exchange instruction or a platform authorization.

## Private Trader-42 access

The workflow's ordinary `GITHUB_TOKEN` cannot be assumed to read
`letsgo0226/Trader_42.sh`; private repositories commonly return HTTP
403/404 to another repo's Actions token. Do not bypass this isolation.

To allow the **stage-1 audit** to read that repository, an administrator may
set a fine-grained read-only credential `HSI_AUDIT_READ_TOKEN` in UTM.sh
Actions secrets with **only Trader_42.sh: Contents Read**, or use equivalent
read-only GitHub App permissions.

- Do not paste secret values into any chat, workflow file, issue or PR.
- The additional credential is sent only to the allowlisted Trader-42 source.
- Missing access is a HOLD, not a claim of synchronization.
- No Railway tokens, GitHub administration scopes, financial exchange API
  keys or deployment credentials are requested.

## GitHub Actions layout

1. **Audit** runs credential-free unit tests, performs source reads, and (on
   verified drift only) produces stage-2 candidate records. A missing input or
   mismatch in supporting evidence fails the job closed.
2. **Propose** is allowed only on a confirmed drift and non-PR events, and may
   create a *draft report-only PR* using scoped GitHub permissions. The
   proposal consists of hashes/review metadata, not private code or a fix.
3. Nothing in this workflow can merge, launch a trading order, or call a
   Railway mutation API. Deployment is deliberately out-of-scope.

GitHub Actions must explicitly allow workflow-created pull requests for the
report-only PR job to function. Daily schedules work only after a workflow
lands on the repository's default branch. **This draft PR is not a live daily
scheduled monitor until separately reviewed and merged.**

## Remaining safe-deployment milestones

- Independently test candidate behavior, not merely Python syntax.
- Review the actual target changes within the destination repository.
- Require a fresh target revision and explicit owner authorization.
- Apply only through protected branches/environments with proper GitHub and
  Railway credentials, keeping trading/live arming and billing excluded from
  unattended updates.
- Confirm new deployment health, persistence and rollback evidence.

`IN_SYNC` must not be interpreted as `SAFE`. A shared bug can exist in all
three source copies. Neither a formal certificate nor a platform SUCCESS
status establishes correctness of arbitrary future updates.
