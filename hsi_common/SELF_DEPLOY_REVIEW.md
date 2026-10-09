# HSI guarded self-deployment: stage 1 (review-only)

## Capability boundary

This PR adds *observation and review preparation*, **not** self-modifying
production software. All source reads are from the pinned
\`hsi-three-system-v1\` branches in the three system repositories.

The monitor compares SHA-256 digests of the HSI \`core.py\`, \`server.py\`,
and \`test_core.py\` files without running fetched source. It reports:

| Status | Meaning |
| --- | --- |
| \`IN_SYNC\` | All three copies were readable and their scoped bytes match |
| \`REVIEW_REQUIRED\` | All three copies were readable and scoped source drift exists |
| \`HOLD_FETCH_ERROR\` | At least one source was inaccessible; no assurance of agreement |
| \`HOLD_FORMAL_GATE\` | The finite HSI certificate gate failed; no assurance |

A formal \`closed=1\` certificate only tests the finite conditions of
\`HSI-3SYS/1.0\`. It is **not** a security proof, an optimizer, a deployment
authorization, or a statement about program halting.

## Required access to private Trader-42 repository

The workflow's built-in \`GITHUB_TOKEN\` is normally scoped to the current
UTM repository. If \`letsgo0226/Trader_42.sh\` is private, the monitor
cannot read it merely because the UTM workflow has a token. A 404/403
must HOLD; it must not be interpreted as agreement.

An administrator may configure a **separate, narrowly scoped, read-only**
credential, named \`HSI_AUDIT_READ_TOKEN\`, as an Actions repository secret
in UTM.sh. A suitable fine-grained token must be restricted to
\`Trader_42.sh\` with only **Contents: Read** permission, or use an
equivalent read-only GitHub App installation credential.

- Never paste a token into a chat, workflow source, log, issue, or PR.
- The separate credential is sent **only** to the Trader-42 contents API.
- Do **not** grant Actions Railway administration or exchange order authority.
- Without this read permission, the CI audit intentionally fails closed.

## GitHub's protections remain authoritative

The workflow uses two jobs:
1. **Audit**: read-only by default; tests and compares sources, then uploads
   a report artifact. Any incomplete source evidence fails closed.
2. **Propose**: only on confirmed drift, and only for non-PR triggers;
   its scoped write permissions may create/update a *draft PR containing
   only the JSON/Markdown audit report*. It does not push any code fixes.

GitHub Actions must be configured to allow workflow-created PRs for stage 1
report PR creation to work. The \`schedule\` event only runs a workflow
present on the repository's **default branch**. While this workflow is only
in a draft PR or feature branch, it is not an active daily scheduled job.

Do not merge this draft merely to bypass an audit failure. First verify
the private-repo read-only access, source scope, and relevant branch policies.

## Stage 2+ proposal (not implemented here)

\`\`\`text
Observe -> Compare -> Candidate Patch -> Isolated Tests
 -> HSI Bounded Invariant Gate -> Security/Resource Review
 -> Human-Authorized GitHub PR -> Authorized Cloud Apply
 -> Health Check -> Evidence Review / Rollback
\`\`\`

Possible future automated actions must be explicit allowlisted operations
with time/resource budgets, protected environments, owner approval,
and rollback. Production trade arming, adding privileges, and changing
billing plans are excluded from unattended auto-apply.

Never equate \`IN_SYNC\` with \`SAFE\`; synchronized bugs are still bugs.
