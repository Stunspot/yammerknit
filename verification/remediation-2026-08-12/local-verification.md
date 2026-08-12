# Local verification - Yammerknit

Bound content commit: `ad64ec3fba2313b7bd0d452cbf07afef08cecd38`
Bound fingerprint: `8eafd06326db83a40f5b22aa30623fd03c3292e7958812b22a53f0fe168bf9d5`

## Fresh final results

- Product tests: 15 passed.
- Release-custody tests: 6 passed, including exact 36-file outer-customer-ZIP versus extracted-mirror byte parity.
- Documentation site tests: 7 passed, including all local routes, assets, links, fragment IDs, share metadata, and distinct visual roles.
- Release audit: 0 errors, 0 warnings; frozen tree hash remains `bdc480...` after timestamp-only audit refresh.
- TestForge line-ending policy: PASS against the exact Git index; no indexed text path contains CR bytes.
- `git diff --check`: PASS.
- Frozen customer archive remains unchanged at the published checksum. The restored extracted persona is the archive's exact 4,287-byte CRLF payload (`5406776d...`); current source is the semantically equivalent 4,256-byte LF payload (`ed6eeb11...`).
- Local Codex inventory: `yammerknit@personal` is installed and enabled at version 0.1.0. This proves installation/discovery state, not a fresh-host install or current-candidate invocation.
- External links: 18 unique targets were exercised. Existing public dependencies returned 200. The new `CONTRIBUTING.md` remote blob route remains 404 only because commit `ad64ec3...` is unpublished.

## Remote read-only observation - 2026-08-12 America/Chicago

- Remote `main`: `e3868618258dd0710110dec40300a484c9e478fd`.
- Live Pages routes `index`, `get-started`, `use`, `data`, `troubleshooting`, and `validation`: HTTP 200, but they are the superseded site and lack the candidate hero and marketplace guidance.
- Candidate Pages hero: HTTP 404 at both plausible live paths.
- Live old secondary hero SHA-256: `ed8516222c0822cbe6d0d4f57013207437f259e124a9dea2fbae4717019c4de1`.
- Live social card SHA-256: `f5efc4cf11b62b67a9141872ea2319c752ea6db5b8227a2d01345e220a4734fa`.
- Pages configuration reports `https://stunspot.github.io/yammerknit/`; GitHub repository Open Graph configuration is null.

No deployed-candidate or repository-social-preview result is inferred from these observations.
