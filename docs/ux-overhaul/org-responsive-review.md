# Organization Administration Responsive Review

Date: 2026-07-14

Organization layouts use the shared shell plus responsive record, metric, form, and action grids. At 1440px and 1280px, overview metrics and operational lists use available horizontal space without turning the page into a chart dashboard. At 768px, filters and summaries collapse into stable stacked regions. At 390px, records, forms, action groups, and detail metadata become single-column and retain readable labels and 44px controls.

Long organization names, usernames, invitation addresses, course titles, role labels, and class names wrap instead of widening the viewport. Class detail remains a separate page on mobile. The confirmation dialog uses the shared mobile treatment, and the settings form remains usable with a virtual keyboard.

Playwright includes a 390px horizontal-overflow assertion and primary navigation checks. Build and static review cover the remaining target widths; screenshot baselines remain deferred to the cross-role visual-regression task.
