# Yammerknit documentation and accessibility review

## Decision

`REVIEW_PASS`. The public site and packaged customer journey are coherent and
accessible within the tested surface. GitHub Pages deployment, the canonical
URL, all maintained routes, site metadata, the sharecard, the custom recovery
page, and GitHub's repository social preview were independently read back after
publication.

## Artifact, users, and benchmark

- Artifact: Yammerknit 0.1.0 public HTML documentation, repository start
  surface, packaged Markdown journey, hero illustration, and sharecard.
- Users: Codex, Claude, and other capable-agent users installing or operating
  Yammerknit; operators preparing sources for later vector-RAG ingestion.
- Access methods reviewed: desktop and 390-pixel mobile visual rendering,
  keyboard-first entry, static HTML semantics, Markdown structure, and direct
  HTTP routes.
- Benchmark: WCAG 2.2 AA authoring practices where applicable. This is not a
  formal conformance assessment.

## Evidence inspected

- All maintained public HTML and customer Markdown.
- Local-link and image resolution across seven HTML routes.
- One title and H1 per page, declared language, skip-link target, image alt
  attributes, canonical URLs, Open Graph metadata, Twitter card metadata,
  visible focus treatment, and reduced-motion handling.
- Sharecard dimensions of 1280 by 640 pixels and file size below GitHub's
  one-megabyte repository-preview limit.
- Playwright with system Microsoft Edge at 1440 by 1000 and 390 by 844 pixels.
- Visual inspection of the generated artwork, sharecard, desktop page, and
  actual 390-pixel mobile page.
- Customer release reconstruction and local-link traversal after the repository
  and packaged-kit path divergence was repaired.

## Findings and repairs

1. `START-HERE.md` originally linked to a nonexistent root `docs/` Markdown
   directory. The repository now points to `customer-docs/`; the release
   builder rewrites that prefix to the packaged `docs/` directory.
2. The README's initial local sharecard path would have broken inside the
   customer kit. It now uses the eventual absolute Pages asset URL.
3. The initial CSS verifier treated `outline: 0.2rem` as `outline: 0`. Its
   oracle now distinguishes a real focus reset from a valid width.
4. The first browser attempt reached an unrelated service already bound to the
   chosen port. The review was rerun against a verified absolute document root
   on a separate port.
5. The first mobile test supplied an ignored Playwright option and therefore
   rendered desktop width. The test now asserts the browser's observed client
   width equals the requested viewport, and the corrected 390-pixel screenshot
   was visually inspected.

## Retest result

- Hesperos Markdown lint: passed.
- Documentation site unit checks: 5 passed.
- Release topology and link checks: 5 passed.
- Existing Yammerknit unit checks: 15 passed.
- Browser review: passed at 1440 and 390 pixels with zero horizontal overflow;
  all local images loaded; the skip link was the first visible keyboard target;
  all six secondary routes returned HTTP 200.
- GitHub Actions run
  [`30561985966`](https://github.com/Stunspot/yammerknit/actions/runs/30561985966)
  completed successfully for commit `718d8e45b7389cbd9e310a9d9f07198da62aa997`.
- Live readback on 2026-07-30: the canonical page and five maintained secondary
  routes returned HTTP 200; the custom recovery page returned HTTP 404 with
  Yammerknit's own content.
- The full Playwright review passed again against the live Pages site at 1440
  and 390 pixels; the resulting screenshots were visually inspected.
- The live 1280 by 640 sharecard returned HTTP 200 as `image/png`, and GitHub's
  repository Open Graph image returned the same 254,294-byte image with the
  same SHA-256 digest.

## Claim limit

The review does not establish formal WCAG conformance, screen-reader usability,
representative-user success, or behavior on every browser. The in-app browser
channel could not start because its host executable binding was absent;
Playwright with the installed Microsoft Edge browser supplied the rendered
local and live-site evidence instead.
