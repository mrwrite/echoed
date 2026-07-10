# Visual Direction

## Direction: Warm Archive Learning Platform

EchoEd should feel like a living learning archive: warm paper surfaces, deep ink text, grounded green action color, gold for earned/progress moments, clay/rose for caution, and restrained blue for links/information.

## Brand Cues

- Current repository mark: text "EE" in shell components.
- Existing mission assets: Africa/world maps and storybook images.
- No standalone logo file was found in the repository search; do not replace the mark until the real logo asset is supplied.

## Palette Roles

- Ink: primary reading text and page titles.
- Archive paper: page background and content surfaces.
- Palm green: primary action and active navigation.
- Gold: achievement, progress, highlights.
- Clay: warning and historical annotation.
- River blue: links, informational states, maps.
- Berry red: destructive/error states.

## Typography

- Use a readable sans family for app UI. Existing assets include `CalSans-Regular.ttf`; current CSS references Inter/Poppins/Playfair but repo font availability should be rationalized during implementation.
- Proposed: Cal Sans for display/brand headings where licensed locally; system sans for body unless Inter is bundled.
- Avoid viewport-scaled body text. Use stable scale tokens.

## Imagery

- Use real historical images, maps, storybook images, and learner artifacts when they directly support content.
- Historical images require captions, source/provenance, date/context where known, and respectful cropping.
- Avoid dark blurred generic background images when learners need inspection.

## Layout

- App surfaces should be full-width bands and constrained content, not cards nested inside cards.
- Use cards for repeated items, dialogs, and framed tools.
- Data-heavy staff surfaces should be calm and dense; student surfaces should be spacious and action-led.

## Motion

- Motion should orient, not entertain.
- Use short fades/slides for state changes.
- Disable nonessential animation under reduced motion.

## Dark Mode

Dark mode is feasible later, but not recommended for the first overhaul because historical imagery, maps, and K-5 reading benefit from a stable light-first contrast system.
