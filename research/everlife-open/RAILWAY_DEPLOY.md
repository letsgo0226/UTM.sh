# Deploy Everlife Open from GitHub to Railway (isolated service)

Repo: `letsgo0226/UTM.sh`. Branch: `everlife-open-sdg-v1`. Root directory: `/research/everlife-open`.

1. Create a NEW isolated Railway project (not UTM-Universe or any trading system) in your existing workspace; set **PR environments OFF**.
2. Create service from the GitHub repository. Set source branch explicitly to `everlife-open-sdg-v1`, service Root Directory `/research/everlife-open`, and config path `/research/everlife-open/railway.json` if Railway doesn't automatically detect the subfolder config.
3. Use Dockerfile in the subfolder, container listens on `$PORT` (default 8080), HTTP health check `/health`.
4. Expose one read-only domain. Test `/health`, `/v1/registry`, `/openapi.json`, `/llms.txt` and POST rejection.
5. Protect deployment controls; keep secrets and tokens out of source. **Never** connect production trading or biomedical devices.
6. Keep PR #45 in draft until existing main-branch production redeploy triggers are audited. GitHub Actions verifies the research branch and uploads its result artifact; publishing and production changes require separate approval.

This is a synthetic formal-model registry: not an anti-aging treatment, veterinary product, guaranteed AI persistence, zero thermodynamic entropy or a general halting solver.

If Railway cannot create a project due to an upstream pause, GitHub raw JSON and GitHub Actions remain accessible. Do NOT replace the public URLs with invented Railway endpoints.
