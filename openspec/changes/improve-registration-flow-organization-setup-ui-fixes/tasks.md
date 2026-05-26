## 1. Registration And Onboarding Flow

- [x] 1.1 Refine the registration form state so organization setup intent is explicitly captured, validated, and normalized before storing pending onboarding data.
- [x] 1.2 Update registration copy and submission behavior so users understand whether organization setup will happen immediately after sign-in or be skipped.
- [x] 1.3 Consolidate the onboarding-required decision used by login and the home session guard so pending setup, zero-org, and personal-only states route consistently.
- [x] 1.4 Update the organization onboarding screen to prefill saved registration intent, preserve values on failure, and complete active-organization bootstrap after successful creation.

## 2. Shell Contrast And Layout Fixes

- [x] 2.1 Adjust registration and onboarding visual tokens or utility classes to improve contrast for helper text, warnings, errors, and disabled/loading states.
- [x] 2.2 Rework the sidebar and home shell layout contract so expanded and collapsed widths keep content aligned without overlap on first paint and during transitions.
- [x] 2.3 Verify compact sidebar navigation remains usable and legible when labels are hidden and nav content loads after permissions bootstrap.

## 3. Verification

- [x] 3.1 Extend or add frontend tests for registration intent handling, onboarding redirects, and organization creation success and failure states.
- [x] 3.2 Extend or add UI-focused tests for sidebar collapsed and expanded layout behavior and registration/onboarding state rendering.
- [x] 3.3 Run the relevant frontend test suite and any targeted checks needed to confirm the change is ready for implementation review.
