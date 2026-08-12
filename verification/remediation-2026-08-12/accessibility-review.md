# Accessibility review — Yammerknit

Receipt: `YAMMERKNIT-A11Y-ad64ec3-8eafd063-20260812`

- Bound commit: `ad64ec3fba2313b7bd0d452cbf07afef08cecd38`
- Bound fingerprint: `8eafd06326db83a40f5b22aa30623fd03c3292e7958812b22a53f0fe168bf9d5`
- Result: `PASS — STATIC/SOURCE REVIEW`; GUI browser, accessibility-tree, screen-reader, zoom, and live keyboard behavior remain `NOT TESTED`

Every Pages route declares `lang=en`, has one page-level H1, ordered headings, landmarks, labeled primary navigation, skip link, visible focus treatment, and footer. Narrow navigation remains horizontally reachable. Images have role-appropriate alternative text or decorative treatment and declared dimensions. Reduced-motion handling exists; responsive layouts preserve content; long code/URL content is wrap- or scroll-contained; custom 404 recovery preserves useful routes.

Measured contrast spans 6.768:1 to 18.9:1 across quiet copy, prose, accents, buttons, callouts, and focus. Seven local site tests pass structure, reduced motion, links/fragments, share metadata, required assets, and role wiring.

Static review does not establish formal accessibility conformance or deployed user-agent behavior. Any governed-file change invalidates this receipt.
