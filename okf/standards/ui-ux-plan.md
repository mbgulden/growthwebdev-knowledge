---
type: Standard
title: UI/UX Plan for User-Facing Surfaces — Prismatic Web Plugin + Ecosystem
description: Comprehensive UI/UX plan covering every user-facing surface: content-gathering UI, build plan preview, Linear-style task canvas, agent activity dashboard, edit areas, preview panes, mobile. The single source of truth for "what does the user see and how do they interact with it."
resource: https://github.com/mbgulden/growthwebdev-knowledge/blob/main/okf/standards/ui-ux-plan.md
tags: [standard, ui-ux, design, dashboard, preview, edit, mobile, accessibility, prismatic-web-plugin, content-gathering]
timestamp: 2026-06-23T07:50:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/ui-ux-plan.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# UI/UX Plan for User-Facing Surfaces

> **What this is:** The single source of truth for "what does the user see and how do they interact with it" across all Prismatic Web Plugin surfaces. Covers content gathering, build plan preview, Linear-style task canvas, agent activity dashboard, edit areas, preview panes, and mobile. Per Michael: "make sure there's a UI/UX plan for all 'user' facing interactions, dashboards, preview panes, edit areas, all that."

## Design principles

1. **Calm by default** — no flashing, no urgency theater, no auto-refresh loops. State changes announce themselves.
2. **Progressive disclosure** — show the high-level state first, let users drill into details.
3. **Program-agnostic design input** — supports Figma links, web URLs, screenshots, photos, mood boards.
4. **One-click to act, three clicks to inspect, five clicks to debug** — the standard action hierarchy.
5. **Optimistic UI with reconciliation** — show what should happen, then update to what did.
6. **Mobile-first responsive** — every screen works on a phone. Desktop is the "more density" version, not a separate design.
7. **Accessibility as a first-class citizen** — WCAG 2.2 AA minimum, screen-reader friendly, keyboard navigable.

## Surfaces (the complete map)

### Surface 1: Content Gathering Wizard (`/gather`)

**Who:** The client (non-technical) filling out the 5 Website Dev docs.
**When:** First time they engage with a build.
**Goal:** Make the 5 docs feel like a friendly interview, not paperwork.

**Layout:** Single-column, mobile-first, 5-step progress bar at top.

**Screen 1.1 — Welcome / Onboarding**
```
┌────────────────────────────────────────────┐
│  Hi! Let's build your website together.   │
│                                            │
│  I'll ask you 5 short questions to under-  │
│  stand your business. You can save and     │
│  come back anytime.                         │
│                                            │
│  [Start the conversation →]                 │
│                                            │
│  How long? ~15 min    Do I need anything?  │
│                       Nope, just your ideas │
└────────────────────────────────────────────┘
```

**Screen 1.2 — The Conversation View (one per doc)**
```
┌────────────────────────────────────────────┐
│ ●─●─○─○─○  Step 2 of 5: Your Story          │
├────────────────────────────────────────────┤
│                                            │
│  💬 Tell me about why you started your    │
│  business. What was the moment that made  │
│  you say "I have to do this"?              │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ (Type your answer here, or paste     │ │
│  │ from a doc, or upload a voice memo) │ │
│  │                                      │ │
│  │                                      │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Examples:                                 │
│  • "I was fed up with the way [industry]   │
│    treated [people like me]..."            │
│  • Or paste from a doc you already wrote   │
│                                            │
│  [← Back]  [Save & continue →]              │
│  [Save & exit]                              │
│                                            │
│  Progress: 23% — about 12 min left          │
└────────────────────────────────────────────┘
```

**Key interactions:**
- **Save & exit** — preserves state, returns to dashboard
- **Voice memo upload** — converts to text via AGY
- **Paste from doc** — accepts .md, .txt, .docx; extracts relevant sections
- **Field-level help** (?) — opens contextual examples inline
- **Auto-save** — every 30 seconds, with a tiny "Saved" indicator (no toast spam)

**Validation feedback:** Green checkmarks appear next to completed fields; red dots for required-but-empty fields. No modal errors — just inline, non-blocking.

---

### Surface 2: Build Plan Preview (`/plan/:client_slug`)

**Who:** The client + the project team.
**When:** After the 5 docs are submitted, before the build starts.
**Goal:** Show the senior-architect-level build plan so the client can review and approve.

**Layout:** Two-column on desktop (TOC left, content right). Single-column on mobile (sticky TOC at top).

```
┌─────────────────┬──────────────────────────────┐
│  TABLE OF       │                              │
│  CONTENTS       │   Meridian Women's Defense   │
│                 │   Build Plan                 │
│  ✓ Site Arch.   │                              │
│  ✓ Pages        │   ## 1. Site Architecture     │
│  ✓ Design       │                              │
│  ✓ Assets       │   [content here]            │
│  ✓ Technical    │                              │
│  ✓ Automation   │   ## 2. Per-Page Briefs       │
│  ✓ Sequence     │                              │
│  ✓ Acceptance   │   [content here]            │
│                 │                              │
│  [Download PDF] │                              │
│  [Approve plan] │                              │
│  [Request edits]│                              │
└─────────────────┴──────────────────────────────┘
```

**Key interactions:**
- **Section anchors** — click TOC item, smooth-scrolls to that section
- **Inline comments** — click any paragraph, leave a comment for the team
- **Approve plan** — single button, confirms the build will start
- **Request edits** — opens a freeform text area for feedback (no requirement to be specific)
- **Download PDF** — exports the plan as a printable PDF

**Edit-request flow:**
```
┌────────────────────────────────────────────┐
│  What would you like changed?              │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ (Be as specific or vague as you      │ │
│  │ want. "Make it warmer" or "Page 3    │ │
│  │ hero is wrong — I want a video bg")  │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  □ Section to update: [Site Architecture ▾]│
│                                            │
│  [Send to team]                            │
└────────────────────────────────────────────┘
```

---

### Surface 3: Agent Activity Dashboard (`/build/:client_slug`)

**Who:** Michael (the operator) + the client (read-only).
**When:** During the build.
**Goal:** Show real-time progress without anxiety. The client should feel "things are happening" not "did it break?"

**Layout:** Single-column, mobile-first, with a status hero at the top.

```
┌────────────────────────────────────────────┐
│  Meridian Women's Defense — In Progress     │
│  ─────────────────────────────────────────  │
│                                            │
│  ████████████████░░░░ 78%                   │
│  18 of 23 tasks done · 5 in progress        │
│                                            │
│  Currently:                                │
│  • AGY is writing the homepage hero copy    │
│  • Kai is setting up the color palette      │
│  • Ned is preparing the Cloudflare project  │
│                                            │
│  Last update: 2 min ago                     │
│  Estimated complete: ~2 hours               │
│                                            │
│  ────────────────────────────────────────   │
│  Activity (live)                           │
│  ────────────────────────────────────────   │
│  ✓ GRO-2150 Asset curation (10 min ago)     │
│  ✓ GRO-2149 Design system (15 min ago)      │
│  ⟳ GRO-2143 Build page: Home (in progress) │
│  ✓ GRO-2144 Build page: About Us (35 min)   │
│                                            │
│  [View all 23 tasks →]                      │
│  [Preview the site →]                       │
│  [Pause build]  [Send message]              │
└────────────────────────────────────────────┘
```

**Key interactions:**
- **View all tasks** — opens the Linear-style task canvas (Surface 4)
- **Preview the site** — opens the live preview in a new tab
- **Pause build** — single button, confirms before pausing
- **Send message** — Slack/Email notification to the team
- **Status icons:** ✓ done, ⟳ in progress, ⏸ blocked, ✗ failed

**Status colors (accessible):**
- Done: subtle green
- In progress: blue
- Blocked: amber
- Failed: red (only shows when there's an actual issue)

---

### Surface 4: Task Canvas (`/tasks/:client_slug`)

**Who:** Michael (the operator), AGY/Kai/Ned (via their agent UI).
**When:** During the build, when the operator wants to inspect or intervene.
**Goal:** Full visibility into every task. This is essentially a Linear-style board.

**Layout:** Kanban board (4 columns) on desktop. Tabs on mobile.

```
┌────────────────────────────────────────────────────┐
│  Meridian Women's Defense — Tasks                   │
│                                                     │
│  [Board] [List] [Timeline] [By Agent]                │
│                                                     │
│  ┌─────────┬─────────┬─────────┬─────────┐         │
│  │  TODO   │ IN PROG │ REVIEW  │  DONE   │         │
│  │  (5)    │  (2)    │  (3)    │  (13)   │         │
│  ├─────────┼─────────┼─────────┼─────────┤         │
│  │ GRO-2155│ GRO-2143│ GRO-2149│ GRO-2150│         │
│  │ Cloud   │ Home    │ Design  │ Assets  │         │
│  │ Pages   │ page    │ system  │         │         │
│  │         │         │         │         │         │
│  │ GRO-2151│ GRO-2144│ GRO-2146│ GRO-2144│         │
│  │ Autom.  │ About   │ Flagship│         │         │
│  │ A       │ Us      │ Class   │         │         │
│  │         │         │         │         │         │
│  │ [more]  │ [more]  │ [more]  │ [more]  │         │
│  └─────────┴─────────┴─────────┴─────────┘         │
└────────────────────────────────────────────────────┘
```

**Each card shows:**
- Issue ID (clickable → opens detail)
- Title (truncated)
- Agent label (color-coded)
- Priority indicator (P1/P2/P3)
- Assignee avatar
- Last activity timestamp

**Click a card → opens Surface 5 (Task Detail)**

---

### Surface 5: Task Detail (`/tasks/:id`)

**Who:** Michael, the assigned agent, the reviewer.
**When:** Inspecting a specific task.
**Goal:** Full task context + the work-in-progress + review controls.

**Layout:** Single-column scrollable, sticky action bar at bottom.

```
┌────────────────────────────────────────────┐
│  GRO-2143 — Build page: Home               │
│  [agent:agy]  P2  ~2 hours                  │
├────────────────────────────────────────────┤
│                                            │
│  Description                               │
│  ──────────                                │
│  [from the build plan]                     │
│                                            │
│  Acceptance Criteria                       │
│  ────────────────────                      │
│  □ Hero (headline, sub, CTA, image)        │
│  □ Mobile responsive                       │
│  □ Schema.org markup                       │
│  □ Lighthouse >= 95                        │
│                                            │
│  Work in Progress                          │
│  ────────────────                          │
│  [preview pane of the page]                │
│                                            │
│  Activity                                  │
│  ───────                                  │
│  AGY created branch feat/home-page 2h ago  │
│  AGY pushed commit a1b2c3d 1h ago          │
│  AGY requested review 30m ago              │
│  Jules CLI: "Looks good, 1 nit" 20m ago    │
│  Fred verified artifact 5m ago             │
│                                            │
│  Preview                                   │
│  ──────                                    │
│  [Live preview pane — see Surface 6]       │
│                                            │
├────────────────────────────────────────────┤
│  [Approve]  [Request changes]  [Reassign]   │
└────────────────────────────────────────────┘
```

---

### Surface 6: Preview Pane

**Who:** The operator, the client.
**When:** Reviewing work-in-progress or the final site.
**Goal:** See exactly what the user will see.

**Layout:** Full-bleed preview, device toggle in the top-right.

```
┌──────────────────────────────────────────────────┐
│  [Desktop]  [Tablet]  [Mobile]    [Open live ↗]  │
│  ────────────────────────────────────────────────  │
│                                                   │
│           ┌──────────────────────┐                 │
│           │                      │                 │
│           │  [actual page render] │                 │
│           │                      │                 │
│           │                      │                 │
│           └──────────────────────┘                 │
│                                                   │
│  URL: https://meridian-womens-defense.pages.dev/  │
│  Last updated: 2 min ago                          │
└──────────────────────────────────────────────────┘
```

**Interactions:**
- **Device toggle** — instant resize to the chosen breakpoint
- **Open live** — opens the actual deployed URL in a new tab
- **Click anywhere in the preview** — sends a comment pinned to that element
- **Side-by-side diff** — compare with the previous version
- **Comment annotation** — appear as little pins on the preview

**Mobile preview shows actual device chrome (notch, status bar) for the truest preview.**

---

### Surface 7: Edit Areas

**Who:** The client (during review), the operator (during build).
**When:** Making tweaks, fixing content, adjusting design.
**Goal:** Edit the live site without writing code.

**Layout:** WYSIWYG editor with hover-to-edit affordances.

```
┌────────────────────────────────────────────┐
│  [Editable mode: ON]                        │
│                                            │
│  Hover over any text or image to edit.     │
│  Click a section to restructure it.         │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  [Hero: click to edit]               │ │
│  │                                      │ │
│  │  "Real Skills. Real Confidence.    │ │
│  │   Right Here in Meridian."          │ │
│  │                                      │ │
│  │  [Edit text]  [Change image]         │ │
│  │                                      │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Edits are auto-saved.                       │
│  [Publish changes]  [Discard]  [Save draft] │
└────────────────────────────────────────────┘
```

**Key interactions:**
- **Hover** — text/image gets a subtle outline
- **Click to edit** — replaces with an inline editor (text becomes a contenteditable, image becomes a file picker)
- **Drag to reorder** — sections can be dragged
- **Section menu** — duplicate, delete, move
- **Auto-save** — every edit, no save button required (but available)
- **Publish** — triggers a fresh build, returns to Activity dashboard

**Edit history:** every change is tracked, can be reverted.

---

### Surface 8: Comment Threads (inline, anywhere)

**Who:** Anyone viewing a preview.
**When:** Reviewing work, requesting changes, asking questions.
**Goal:** Contextual conversation pinned to specific elements.

**Layout:** Comment pin + side panel.

```
┌────────────────────────────────────────────┐
│  💬 Sarah Chen 2 hours ago                 │
│     "Can this CTA be more urgent?"         │
│                                            │
│     ↳ Jules CLI: "On it" 1 hour ago        │
│                                            │
│     [Reply...]                              │
└────────────────────────────────────────────┘
```

**Comments are visible on:**
- Task detail (general comments)
- Preview pane (pinned to elements)
- Build plan (pinned to sections)
- Activity feed (auto-generated updates)

---

### Surface 9: Notifications

**Who:** Anyone with a stake in the project.
**When:** When something needs attention.
**Goal:** Tell users about important things without overwhelming them.

**Channels:**
- **Telegram** (Becca bot) — short messages, mobile-friendly
- **Email** — digest mode (daily), or instant for P1
- **In-app** — bell icon with count, click to open

**Notification types:**

| Type | Channel | Frequency | Example |
|---|---|---|---|
| Build complete | All 3 | Once | "Meridian Women's Defense site is live" |
| Task blocked | Telegram + in-app | Instant | "GRO-2143 is blocked, needs your input" |
| P1 failure | All 3 | Instant | "Build failed at deploy step" |
| Daily digest | Email | Daily 8am | "5 things moved today" |
| Plan ready for review | Email | Once | "The build plan for X is ready" |
| Comment added | In-app | Instant | "Sarah commented on the homepage" |

**Settings panel** — toggle each type per channel.

---

### Surface 10: Settings + Account (`/settings`)

**Who:** Michael (admin) and clients (basic).
**When:** As needed.
**Goal:** Configure notifications, integrations, billing, team.

**Layout:** Tabbed settings, 5 tabs.

- **Profile** — name, email, avatar, password
- **Notifications** — channel toggles, frequency
- **Integrations** — connect Linear, GitHub, Cloudflare, Stripe, etc.
- **Team** — invite members, set roles
- **Billing** — usage, subscription, invoices

---

## Mobile-first design system

### Breakpoints

| Name | Width | Use case |
|---|---|---|
| `mobile-narrow` | < 480px | iPhone SE, small Android |
| `mobile` | 480-767px | Most phones |
| `tablet` | 768-1023px | iPad, Android tablets |
| `desktop` | 1024-1439px | Laptops |
| `desktop-wide` | 1440px+ | External monitors |

### Typography (program-agnostic)

Default to a system stack for performance + privacy:
- **Headings:** `-apple-system, "Segoe UI", "SF Pro Display", system-ui, sans-serif`
- **Body:** same stack
- **Code:** `"SF Mono", "Fira Code", "JetBrains Mono", monospace`

Allow user/agent to override per project (Astro supports font loading).

### Color tokens (with dark mode)

```css
:root {
  --color-primary: #4f46e5;     /* indigo */
  --color-success: #16a34a;     /* green */
  --color-warning: #d97706;     /* amber */
  --color-danger: #dc2626;      /* red */
  --color-bg: #ffffff;
  --color-bg-subtle: #f9fafb;
  --color-fg: #111827;
  --color-fg-muted: #6b7280;
  --color-border: #e5e7eb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0a0a0a;
    --color-bg-subtle: #171717;
    --color-fg: #fafafa;
    --color-fg-muted: #a3a3a3;
    --color-border: #262626;
  }
}
```

### Spacing scale (4px base)
`4 8 12 16 24 32 48 64 96 128` — no random values.

### Animation
- **Transitions:** 150ms for hover, 200ms for state changes, 300ms for layout
- **Easing:** `cubic-bezier(0.4, 0.0, 0.2, 1)` (Material standard)
- **No auto-playing animations** — respect `prefers-reduced-motion`

---

## Accessibility checklist (per surface)

- [ ] WCAG 2.2 AA color contrast (4.5:1 for text)
- [ ] Keyboard navigation (Tab, Enter, Esc, arrow keys)
- [ ] Screen reader labels (aria-label, aria-live for activity)
- [ ] Focus rings (visible, high contrast)
- [ ] Form labels (associated with inputs)
- [ ] Error announcements (aria-live="polite")
- [ ] Skip-to-content link
- [ ] No motion-only feedback (always have a text alternative)
- [ ] Color is never the only signal (icons + text for status)

---

## Open questions for Michael

1. **Hosting** — where do these surfaces live? Astro on Cloudflare Pages (like AOT)? Or part of the Meridian demo site?
2. **Auth** — who logs in? Just Michael, or also clients? Email magic link, or Linear OAuth, or both?
3. **Real-time** — how live is the activity dashboard? SSE? WebSocket? Polling every 5s?
4. **Multi-tenant** — one dashboard per client, or a single dashboard with all projects?
5. **Comments** — persist in Linear, or own DB?
6. **Edit areas** — full WYSIWYG (risky), or constrained fields (safer)?

## Next concrete steps

1. **Validate the plan** with Michael (this doc)
2. **File Linear issues** for each surface (10 issues) under the Prismatic Web Plugin epic
3. **Build Surface 1 first** (Content Gathering Wizard) — it's the entry point, validates the design
4. **Build Surface 3 next** (Agent Activity Dashboard) — proves the system is working
5. **Build Surface 6 last** (Preview Pane) — needs the deploy pipeline to be working first

## Change log
- 2026-06-23 07:50 UTC: Initial plan. 10 surfaces, design principles, mobile-first, accessibility checklist, 6 open questions for Michael.
---

## Surface 11: Version Control UI (history + rollback + sync)

**Per Michael's spec (2026-06-23):**
> "version control baked in to this whole process in a seamless way"
> "people that will be using this prismatic web plugin will not know how GitHub works"
> "interface where they can easily roll back changes to a specific 'save' point"
> "for staging and production"
> "have a button to sync up staging to production and production to staging"
> "clear and simple, but very capable and useful"

### Wireframe

```
┌──────────────────────────────────────────────────────────────────────┐
│ 🔮 Prismatic Web Plugin         michael@growthwebdev.com · Sign out │
├──────────────────────────────────────────────────────────────────────┤
│ Valkyrie Arms Training                                             │
│ 🔗 github.com/mbgulden/valkyrie-arms-training · Last sync: 2 hours │
│                                                                      │
│ [📤 Publish] [⚙️ Settings]                                         │
├──────────────────────────────────────────────────────────────────────┤
│ [📝 Content] [🎨 Design] [📦 Deployments] [🕒 Version History*] │
├──────────────────────────────────────────────────────────────────────┤
│ Quick Sync                                                           │
│ ┌────────────────────────┐ ┌────────────────────────┐               │
│ │ 🧪 → 🚀 Push to Prod   │ │ 🚀 → 🧪 Pull to Staging │               │
│ │ Push staging v8 → prod │ │ Pull prod v7 → staging │               │
│ │ Requires approval      │ │ Safe, no approval      │               │
│ └────────────────────────┘ └────────────────────────┘               │
├──────────────────────────────────────────────────────────────────────┤
│ 🚀 Production (valkyriearmstraining.com)        [📤 Open] [📋 Copy]│
│ Version  What changed                When        Who       Actions  │
│ v7 ●     Added "About" section       2h ago      @michael  [View]   │
│ v6       Synced from staging         Yesterday   @michael  [Rollback][View]
│ v5       Updated contact form        3d ago      @michael  [Rollback][View]
│ v4       Added testimonials          1w ago      @ella     [Rollback][View]
│ v3       Initial Drive ingest        2w ago      @fred     [Rollback][View]
│ ...     (12 versions total)                                       │
├──────────────────────────────────────────────────────────────────────┤
│ 🧪 Staging (valkyrie-staging.pages.dev)                            │
│ Version  What changed                When        Who       Actions  │
│ v8 ●     New pricing page (draft)    12m ago     @michael  [View]    │
│                                                         [Push to Prod]
│ v7       Added "About" section       2h ago      @michael  [Rollback][View]
│ ...                                                                │
└──────────────────────────────────────────────────────────────────────┘
```

### Design decisions

| Decision | Rationale |
|---|---|
| **Version labels (v1, v2, ...) not Git SHAs** | Users don't know what SHAs are |
| **"Save points" terminology in tooltips** | Bridges the gap from non-technical users |
| **Separate staging + production lists** | Per Michael: "sync up staging to production and production to staging" |
| **Rollback button next to each version** | One-click, the user shouldn't have to find it |
| **"Push to Production" prominent button** | The main action — show it |
| **Production deployments require approval gate** | Already implemented in CLI; UI shows the same gate |
| **GitHub connection mentioned but not central** | It's the underlying storage, not the user interface |

### Acceptance criteria

- [ ] User can see all versions (staging + production) at a glance
- [ ] User can roll back any version with one click (in the same env)
- [ ] User can promote staging → production with one click + approval
- [ ] User can pull production → staging with one click (no approval)
- [ ] User never sees SHA hashes, branch names, or git commands
- [ ] User never has to know what GitHub is
- [ ] All actions are reversible (rollback always works)
- [ ] Activity log shows who did what (when multiple users exist)

### Implementation status

- ✅ Backend: `pwp/pwp_version_control.py` (state tracking + snapshots + archives)
- ✅ Backend: `pwp/pwp_vc_cli.py` (CLI for history / rollback / sync / diff)
- ✅ Wired into `deploy_cf_pages.py` (every deploy creates a snapshot)
- ✅ Tests: 7 new tests covering snapshot recording, env filtering, rollback safety
- ✅ UI mockup: `pwp/static/version-control-ui.html` (functional HTML/CSS)
- ⏳ Real UI: needs to be built as a web app (next: AGY research + Linear task)
