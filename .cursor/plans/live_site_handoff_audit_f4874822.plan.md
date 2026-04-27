---
name: Live Site Handoff Audit
overview: Audit the live Halifax Now site against the developer handoff and identify parity gaps by severity, with a prioritized remediation path.
todos:
  - id: compare-routes
    content: Map all live routes/templates against §07 required routes and identify mismatches
    status: completed
  - id: validate-data-contract
    content: Diff `/wp-json/hfx/v1/events` payload vs §08 contract and flag missing/incorrect fields
    status: completed
  - id: verify-components
    content: Check page/component parity for Homepage, Browse, Event Detail, Venue, Map, and Submit
    status: completed
  - id: produce-priority-fixes
    content: Prioritize remediation tasks by P0-P3 severity and implementation order
    status: completed
isProject: false
---

# Halifax Now Live-Site Audit Plan

## Scope
- Compare handoff requirements in [`/Users/katespurr/Downloads/Halifax-Now Developer Handoff.html`](/Users/katespurr/Downloads/Halifax-Now%20Developer%20Handoff.html) against live behavior on `https://www.halifax-now.ca`.
- Validate route parity, component parity, API/data-contract parity, and technical implementation details (map stack, filter logic, responsive behavior, submit flow).

## Evidence Sources
- Captured homepage raw HTML: [`agent-tools/ffa32467-b981-41dd-9462-b74a376846d0.txt`](agent-tools/ffa32467-b981-41dd-9462-b74a376846d0.txt)
- Captured events page raw HTML: [`agent-tools/8f959ddc-57eb-433f-943e-0fbef0f87b1f.txt`](agent-tools/8f959ddc-57eb-433f-943e-0fbef0f87b1f.txt)
- Captured map page raw HTML: [`agent-tools/ae1871a8-4934-4dd3-9649-3698ce414028.txt`](agent-tools/ae1871a8-4934-4dd3-9649-3698ce414028.txt)
- Captured submit page raw HTML: [`agent-tools/1c1d9929-98d4-4aab-bb77-fd7bc8df5995.txt`](agent-tools/1c1d9929-98d4-4aab-bb77-fd7bc8df5995.txt)
- Captured theme CSS: [`agent-tools/3e3e9797-052b-45d4-8237-4465d3dfab9a.txt`](agent-tools/3e3e9797-052b-45d4-8237-4465d3dfab9a.txt)

## Audit Output
- Deliver a scored report (0-4 per dimension) across:
  - Accessibility
  - Performance
  - Responsive design
  - Theming
  - Spec parity / anti-patterns
- List P0-P3 findings with impact and precise evidence references.
- Provide a prioritized remediation sequence focused on restoring handoff parity.

## Remediation Priorities (from observed gaps)
1. Replace plugin-driven `/events` and single event/venue templates with the handoff-defined Broadsheet route/component system.
2. Correct data pipeline issues (epoch date regressions and incomplete filter dimensions).
3. Rebuild map implementation to Leaflet + CartoDB with coordinate-backed markers and popup cards.
4. Expand submit form and moderation metadata capture to match category/neighborhood/mood requirements.
5. Run a post-fix parity re-audit against the handoff checklist.