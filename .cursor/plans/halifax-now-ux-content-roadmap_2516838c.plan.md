---
name: halifax-now-ux-content-roadmap
overview: Design a UX and content roadmap for Halifax Now that builds on the existing GSD technical work and Claude roadmaps, with a strong focus on UI/UX and content for the upcoming summer season.
todos:
  - id: gather-roadmaps
    content: Gather GSD planning docs and existing Claude roadmaps/notes into a single short Direction Brief for Halifax Now.
    status: in_progress
  - id: define-ux-principles-ia
    content: Define UX principles and finalize navigation/IA for Tonight, This Weekend, All Events, categories, and neighbourhoods.
    status: pending
  - id: design-cards-and-detail
    content: Design standard event cards and detail page layouts (desktop + mobile) and align TEC templates/CSS to match.
    status: pending
  - id: summer-content-strategy
    content: Plan and outline summer content themes and guide pages (festivals, patios, family, free events, neighbourhood guides).
    status: pending
  - id: align-pipeline-with-ux
    content: Tighten category mapping and venue naming rules in the scraper pipeline so imported events support the new UX cleanly.
    status: pending
isProject: false
---

## Halifax Now – UX & Content Roadmap

### Goals

- Create a clear, opinionated plan for Halifax Now’s **UI/UX** and **content experience** on top of the working scraper pipeline and calendar.
- Align with your existing GSD plans and Claude roadmaps, while focusing especially on: 
  - Improving the **front-end experience** (cards, filters, navigation, mobile).
  - Designing a **content strategy** (guides, themes, seasonal campaigns) ahead of summer.

---

### 1. Consolidate Existing Roadmaps & Constraints

- **1.1 Collect planning artifacts**
  - Review GSD artifacts in `.planning/` (PROJECT, ROADMAP, phase CONTEXT/PLAN/SUMMARY files) to understand what’s already promised for v1/v2.
  - Review any separate Claude roadmap / notes you have (even if they’re informal) and identify overlapping ideas.
- **1.2 Extract a single source of truth for direction**
  - From those docs, pull out:
    - Confirmed phases/features already implemented (pipeline, TEC setup, calendar pages).
    - Planned but not yet started UX/content work (e.g. guides, neighbourhood pages, happy hour, SEO).
  - Summarize into a short “Direction Brief” with:
    - Who Halifax Now is for.
    - What the site promises users.
    - Which big bets matter for the next 6–12 months.

---

### 2. Define UX Principles & IA (Information Architecture)

- **2.1 UX principles tailored to Halifax Now**
  - Define 4–6 principles that will guide all UI decisions, for example:
    - "Tonight first": always make it trivial to find what’s on tonight.
    - "Glanceable": cards and lists should be scannable in 2–3 seconds.
    - "Neighbourhood‑aware": make it easy to browse by area.
    - "No dead ends": every event page suggests related events.
- **2.2 Core navigation and IA structure**
  - Lock in the main entry points in the nav:
    - `Tonight`, `This Weekend`, `All Events`, `Categories`, `Neighbourhoods` (and later: `Guides`, `Happy Hour`).
  - Design a simple sitemap showing:
    - Calendar views (list, month, photo).
    - Category hubs (e.g. `Live Music`, `Comedy`, `Family & Kids`).
    - Neighbourhood hubs (e.g. `Downtown`, `North End`, `Dartmouth`).
    - Future guide content (e.g. `Summer Festivals`, `Patios`, `Rainy Day Ideas`).
- **2.3 Validate with your roadmap**
  - Check this IA against your existing GSD roadmap and Claude roadmap so we don’t conflict with other planned phases (e.g. neighbourhood guides, happy hour section).

---

### 3. Event Card & Detail Page UX (Summer‑Ready)

- **3.1 Standardize card layout**
  - Specify exactly what each card shows and in what order:
    - Category label, title, date/time, venue + neighbourhood, quick price indicator, 1–2 line description.
  - Define two card variants:
    - **Compact list card** for `/events`, `/tonight`, `/this-weekend`.
    - **Featured card** for guides/homepage spots (larger image, more emphasis).
- **3.2 Design event detail layout**
  - Above the fold: title, date/time, venue (link), category, price, primary CTA ("Get Tickets" or source link).
  - Below the fold: description, photos, map, tags, related events (by venue / category / date).
  - Decide where to show **source attribution** (e.g. "via Ticketmaster" or venue link) in a subtle but clear way.
- **3.3 Mobile-first checks**
  - Ensure card and detail layouts work for small screens:
    - Single-column cards, comfortable tap targets.
    - Filters accessible via a simple toggle or sticky bar.

---

### 4. Filters, Search, and Date-Specific Views

- **4.1 Filter design**
  - Confirm the minimum filter set for `/events`, `/tonight`, `/this-weekend`:
    - Category, Date Range, Neighbourhood, Venue, and optionally Price band (Free, <$20, $20–$50, 50+).
  - Document behaviour for combining filters and resetting them.
- **4.2 “Tonight” and “This Weekend” UX**
  - Lock in business rules:
    - Tonight = all events today (already implemented via shortcode) but decide whether to emphasize evening events visually.
    - This Weekend = Fri–Sun (already handled by `[hfxnow_this_weekend]`) — document this so content and marketing are aligned.
  - Design pleasant **empty states** for quiet nights (show a message plus a few upcoming highlights instead of a blank list).
- **4.3 Search improvements**
  - For now, rely on TEC’s built-in search plus filters; in a later phase, consider a custom search experience that:
    - Searches by title, venue, neighbourhood, and tags.
    - Surfaces popular queries ("brunch", "drag", "kids").

---

### 5. Visual Design System (Lightweight but Reusable)

- **5.1 Design tokens**
  - Define a small set of design tokens you can apply via CSS:
    - Color palette (brand, accent, neutrals).
    - Typography scale (H1–H4, body, labels).
    - Spacing units (e.g. 4/8/16/24 px).
  - Document these in a simple `DESIGN.md` or similar for future reference.
- **5.2 Core components**
  - Specify styles for:
    - Buttons (primary, secondary, text).
    - Category chips / filters.
    - Event cards, badges ("Free", "Sold Out").
  - Keep this minimal but consistent so any new CSS you add later slots into the system instead of being ad‑hoc.

---

### 6. Content Strategy for Summer

- **6.1 Define priority themes for summer**
  - Decide the 3–5 most important seasonal content clusters, for example:
    - Summer festivals & outdoor concerts.
    - Patios, rooftop bars, waterfront events.
    - Family & kids summer activities.
    - Free and low-cost events.
    - Neighbourhood‑specific summer guides.
- **6.2 Plan guide pages and landing pages**
  - For each theme, design:
    - A simple landing page (guide) that mixes:
      - Curated events from your pipeline.
      - Short editorial intros, tips, and links.
    - Internal linking from guides to event detail pages and vice versa.
  - Map these to existing or new GSD phases (e.g. a "Guides" phase in `.planning/phases`).
- **6.3 Editorial cadence and workflow**
  - Decide a sustainable cadence (e.g. one new guide or major update every 2–3 weeks through the summer).
  - Define a simple checklist for creating/updating a guide:
    - Choose theme & time window.
    - Run pipeline, import new events.
    - Curate 10–30 standout events for the guide.
    - Write intro + 2–3 tips.
    - Publish and promote (newsletter, social, etc.).

---

### 7. Data & Pipeline Alignment with UX

- **7.1 Category mapping clean-up**
  - Expand `CATEGORY_MAP` in `category_mapping.py` to cover all major upstream strings you care about (Sports / Soccer / Soccer, LGBTQ+, Karaoke, etc.), mapping them into your 17 canonical categories.
  - Keep a small, human-readable table of mappings for future maintenance.
- **7.2 Venue naming rules**
  - Finalize rules for how scrapers write `Event Venue Name` so they always match canonical TEC venues (and never embed address data in the name).
  - If new venues appear, fold them into your venue CSV + TEC venue importer before using them heavily in events.
- **7.3 Operational runbook**
  - Write a short runbook for yourself describing:
    - How often to run `./run_all_with_audit_v2.command`.
    - How to import `ready_to_import_v2/ready_to_import_from_audit_UNIQUE_YYYY-MM-DD.csv` into staging and then live.
    - Spot-check steps (categories, venues, a few detail pages).

---

### 8. Metrics & Iteration Loop

- **8.1 Define key metrics**
  - For UX:
    - Views of `/tonight` and `/this-weekend`.
    - Clicks from event cards to external ticket/venue sites.
  - For content:
    - Views and time on guide pages.
    - Distribution of events across key categories (Live Music, Comedy, etc.).
- **8.2 Simple feedback mechanism**
  - Add one low-friction way for users to give feedback (e.g. a small link: "Missing something? Tell us.").
- **8.3 Monthly review ritual**
  - Once a month, review:
    - Metrics.
    - Category/venue anomalies.
    - UX friction points.
  - Decide 1–2 changes to ship the following month, keeping scope small but consistent.

---

### How this fits your existing GSD roadmap

- Use this plan as a **front-end/content layer** on top of your existing pipeline/stabilization phases.
- Translate major chunks (e.g. "Guides & Summer Content", "Category/venue mapping clean-up", "Visual design system") into new or updated phases in `.planning/ROADMAP.md` so that the GSD agents (and you) can treat them as first-class work items.
- Continue using staging as your proving ground for all UX/content experiments, then promote those changes to live once they feel right.

