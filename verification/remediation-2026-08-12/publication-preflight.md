# Public publication preflight — Yammerknit

Official GitHub billing documentation observed 2026-08-12 states standard GitHub-hosted runners are free in public repositories. Yammerknit is public; exhausted private-repository allowance is not this repository’s billing boundary.

Complete protected-publication graph:

- feature-branch push: 1 `line-ending-policy` job;
- pull request: 1 `line-ending-policy` job;
- merge to `main`: 1 `line-ending-policy` job plus 1 Pages deployment;
- total maximum: 4 public standard-runner jobs, zero automatic retries, zero billable minutes.

The active main ruleset requires `line-ending-policy`; publication needs no bypass or ruleset weakening.

Official sources:
- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
