# Accessibility review - Yammerknit

Receipt: `YAMMERKNIT-A11Y-ad64ec3-8eafd063-20260812`

- Bound commit: `ad64ec3fba2313b7bd0d452cbf07afef08cecd38`
- Bound fingerprint: `8eafd06326db83a40f5b22aa30623fd03c3292e7958812b22a53f0fe168bf9d5`
- Result: `PASS - STATIC AND SOURCE REVIEW`; deployed-candidate browser, accessibility-tree, screen-reader, and live keyboard behavior are NOT TESTED because the candidate is not published and browser/GUI control is excluded by instruction

## Checks and evidence

- Structure: every Pages route declares `lang=en`, has one page-level H1, ordered headings, landmark structure, a labeled primary navigation, and a footer.
- Keyboard path: native links and controls remain keyboard-operable; skip links and visible focus treatment are present; narrow navigation remains horizontally reachable rather than disappearing.
- Images: each image has role-appropriate alternative text or decorative treatment. Width/height declarations reserve layout space. The three presentation roles are separate files and are not text-dependent except the deliberately textual social card.
- Motion: no essential animation or interaction; reduced-motion handling is present.
- Reflow: responsive layouts collapse without removing content or navigation; long code/URL content is wrap- or scroll-contained.
- Recovery: the custom 404 retains product identity and routes visitors to start, use, troubleshooting, and evidence.
- Contrast calculations: ink/navy surfaces 17.9-18.9:1; muted copy 9.3-11:1; quiet copy 6.768:1; cyan accent 11.98:1; button treatments 9.1-12.1:1; callout copy 14.78:1; prose 13.3:1; amber focus 11.21:1.
- Local automated checks: seven site tests passed, including accessible structure, reduced motion, local link and fragment resolution, social metadata, required assets, and distinct visual-role wiring.

## Limitations

Static review does not establish deployed browser rendering, zoom behavior, assistive-technology output, or live focus order. Those checks remain publication-dependent and are not converted into optimism.

Any governed-file change invalidates this receipt.
