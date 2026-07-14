# UI/UX Guidelines

## Purpose

To define the visual language, interaction patterns, accessibility standards, and usability principles that ensure a consistent, inclusive, and delightful experience across the AI‑Powered Job Finder platform.

## Contents

- Design Principles
- Visual Language
- Layout & Grid
- Typography
- Color System
- Icons & Imagery
- Components Library
- Navigation & Information Architecture
- Forms & Input Controls
- Data Presentation (Tables, Cards, Lists)
- Feedback & Messaging
- Accessibility (a11y)
- Internationalization (i18n)
- Motion & Animation
- Usability Testing & Iteration
- Implementation Notes (Tailwind, shadcn/ui)
- Content Guidelines

## Design Principles

1. **User‑Centred** – Every decision starts from the job seeker’s goals: find relevant jobs, showcase qualifications, apply with confidence.
2. **Clarity Over Cleverness** – Information hierarchy is obvious; jargon is avoided.
3. **Efficiency** – Minimize steps; provide smart defaults (e.g., location, date ranges).
4. **Trust & Transparency** – Show data sources, match explanations, and privacy notices.
5. **Inclusivity** – Design for diverse abilities, languages, and devices.
6. **Feedback‑Driven** – Use micro‑interactions, loading states, and clear error messages.
7. **Consistency** – Reuse patterns, tokens, and components across the product.

## Visual Language

- **Foundation**: The design system is built on a **token‑based** approach (spacing, radius, shadow, color, typography) implemented via Tailwind CSS and extended with a custom plugin.
- **Primitives**: Leverages **shadcn/ui** (Radix UI primitives) for accessible, unstyled components (buttons, dialogs, dropdowns, etc.).
- **State Colors**:
  - `primary`: #2563EB (blue‑600) – used for primary actions.
  - `secondary`: #64748B (slate‑500) – for tertiary actions.
  - `success`: #10B981 (emerald‑500).
  - `warning`: #F59E0B (amber‑500).
  - `danger`: #EF4444 (red‑500).
  - `info`: #3B82F6 (blue‑500).
- **Neutrals**: Slate palette (`slate-50` to `slate-900`) for backgrounds, text, borders.
- **Semantic Usage**:
  - Backgrounds: `bg-white` / `bg-slate-50`.
  - Surface elevation: `bg-white` + `shadow-sm` → `shadow-md` for cards, modals.
  - Text: `text-slate-900` for primary, `text-slate-600` for secondary, `text-slate-400` for muted.
  - Links: `text-primary hover:underline`.
- **Border Radius**: `rounded-sm` (0.125rem), `rounded` (0.25rem), `rounded-lg` (0.5rem), `rounded-xl` (0.75rem).
- **Spacing**: 4px grid (multiples of 0.25rem). Base unit `space = 1rem`.

## Layout & Grid

- **Container**: Max width `1200px` (`max-w-7xl`) with horizontal padding `px-4` (mobile) → `px-8` (lg).
- **Columns**: 12‑column flexible grid (via CSS grid or Tailwind `grid-cols-12`). Common patterns:
  - **Sidebar + Content**: `lg:grid-cols-3 9` (25% sidebar, 75% main).
  - **Card Grid**: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6`.
- **Breakpoints** (Tailwind defaults):
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px
  - `xl`: 1280px
  - `2xl`: 1536px
- **Mobile‑First**: All styles start at `base` and add `sm:`, `md:`, etc. overrides.
- **Whitespace**: Liberal use of whitespace to reduce cognitive load; sections separated by `my-12` (mobile) → `my-16` (lg).

## Typography

- **Font Family**: `Inter` (system fallback: sans-serif). Loaded via Google Fonts or self‑hosted.
- **Weight Scale**:
  - `light`: 300
  - `regular`: 400
  - `medium`: 500
  - `semibold`: 600
  - `bold`: 700
  - `extrabold`: 800
- **Sizes** (rem):
  - `xs`: 0.75rem (12px)
  - `sm`: 0.875rem (14px)
  - `base`: 1rem (16px)
  - `lg`: 1.125rem (18px)
  - `xl`: 1.25rem (20px)
  - `2xl`: 1.5rem (24px)
  - `3xl`: 1.875rem (30px)
  - `4xl`: 2.25rem (36px)
  - `5xl`: 3rem (48px)
  - `6xl`: 3.75rem (60px)
- **Line Height**: `leading-relaxed` (1.625) for body, `leading-snug` (1.25) for headings.
- **Letter Spacing**: `tracking-normal` for body; `tracking-tight` for headings.
- **Usage**:
  - Headings: `font-bold` + size appropriate to hierarchy.
  - Body: `font-regular` leading-relaxed.
  - Captions/footnotes: `text-sm` `text-slate-500`.
  - Mono (code): `font-mono` `text-sm`.

## Color System

- **Palette Source**: Tailwind CSS `slate`, `blue`, `emerald`, `amber`, `red`, `amber` etc., with custom shades if needed.
- **Usage Guidelines**:
  - **Primary Actions**: `bg-primary text-white hover:bg-primary/90`.
  - **Secondary Actions**: `bg-white border border-primary hover:bg-primary/50`.
  - **Danger**: `bg-danger text-white hover:bg-danger/90`.
  - **Backgrounds**:
    - Page: `bg-slate-50`.
    - Cards: `bg-white`.
    - Elevated sections: `bg-white shadow-sm`.
  - **Text on Color**: Ensure WCAG AA contrast (≥4.5:1). Use `text-white` on primary/secondary/danger backgrounds; `text-slate-900` on light backgrounds.
  - **Status Indicators**:
    - Success: `bg-green-100 text-green-800`.
    - Warning: `bg-amber-100 text-amber-800`.
    - Error: `bg-red-100 text-red-800`.
    - Info: `blue-100 text-blue-800`.

## Icons & Imagery

- **Icon Set**: **Heroicons** (outline) for UI; **Heroicons solid** for emphasized states.
- **Size**: 20x20px (`h-5 w-5`) for inline; 24x24 (`h-6 w-6`) for toolbar.
- **Color**: Inherit `text-current`; apply `text-primary` or `text-slate-600` as needed.
- **Illustrations**: Use a consistent line‑art style (e.g., unDraw or custom) with primary color accent.
- **Images**:
  - Optimize via `next/image` (automatic WebP, lazy‑load, priority for above‑fold).
  - Alt text mandatory for informative images; decorative images use `alt=""`.
  - Max width: `max-w-full height-auto`.

## Components Library

We rely on **shadcn/ui** for the following primitives (customized via our tailwind config):

| Component | Usage Example | Customization |
|-----------|----------------|---------------|
| Button | `<button className="btn-primary">Save</button>` | Variants: `primary`, `secondary`, `ghost`, `danger`. |
| Input | `<input className="input" placeholder="Search…" />` | With label, error state (`input-error`). |
| Textarea | Same as input, multi‑line. |
| Select | `<SelectDropdown>` (custom combobox). |
| Checkbox / Radio | Standard. |
| Toggle Switch | `Checkbox` styled as switch. |
| Dialog | `Dialog` from `@radix-ui/react-dialog`. |
| Popover | For tooltips, menus. |
| Toaster | Brief transient notifications (top‑right). |
| Breadcrumb | For navigation depth (e.g., Dashboard > Jobs > Details). |
| Pagination | Simple prev/next + page numbers. |
| Table | `DataTable` with sorting, pagination, row actions. |
| Card | `Card` with header, body, footer variants. |
| Avatar | `Avatar` with fallback to initials. |
| Badge | Small status pill. |
| Progress Bar | For upload/completion. |
| Skeleton Loader | Placeholder while data loads. |
| Modal | Same as Dialog, with scrollable body if needed. |
| Sidebar | `Drawer` (collapsible) for navigation on mobile. |
| Navbar | Top bar with logo, user menu, search. |

All components inherit design tokens (spacing, radius, colors) from the theme.

## Navigation & Information Architecture

- **Top Navigation (Desktop)**:
  - Left: Logo (link to home).
  - Center: Search bar (prominent, placeholder: “Search jobs, titles, companies…”).
  - Right: User avatar + dropdown (profile, settings, sign out).
- **Sidebar (Desktop ≥ lg)**:
  - Collapsible (`<Drawer>` from radix).
  - Sections: Dashboard, Jobs, Applications, Messages, Profile, Admin (if applicable).
  - Icons + text labels.
  - Active route highlighted with `bg-primary/10 border-l-2 border-primary`.
- **Mobile Navigation**:
  - Bottom tab bar (optional) or hamburger menu opening a full‑screen drawer.
  - Essential tabs: Home (Jobs), Applications, Profile.
- **Routing**:
  - `/` – Home (job search + filters).
  - `/jobs/[id]` – Job detail.
  - `/resumes` – Upload / manage resumes.
  - `/applications` – Kanban board.
  - `/messages` – Inbox / notifications.
  - `/profile` – Edit profile.
  - `/settings` – Preferences, notifications, integrations.
  - `/admin` – Restricted to admins.
- **Breadcrumbs**: Shown on deep pages (e.g., Jobs > Job ID > Apply).
- **Deep Links**: Supported for email notifications (e.g., `/jobs/abc123?from=email`).

## Forms & Input Controls

- **Layout**: Vertical stack; label above input; helper text beneath; error message below helper.
- **Validation**:
  - Real‑time on blur; inline error with `input-error` class (`border-danger`).
  - Show summary on submit if multiple errors.
- **Input Types**:
  - `email`, `tel`, `url`, `number`, `date`, `password`.
  - Use `<input type="password">` with toggle‑visibility icon.
- **Select & Combobox**:
  - Autocomplete for large lists (e.g., skills, companies) using `downshift` or `react-select` styled via tailwind.
- **File Upload**:
  - Drag‑and‑drop area with preview (image/pdf).
  - Show file name, size, remove button.
  - Indicate allowed types (`accept=".pdf,.docx"`).
- **Button States**:
  - Default: enabled.
  - Loading: `btn-loading` (spinner inside, disable click).
  - Disabled: `btn-disabled` (`opacity-50 cursor-not-allowed`).
- **Grouped Actions**:
  - Primary action on the right; secondary/cancel on the left.
  - Use `flex justify-end space-x-3` for button groups.
- **Accessibility**:
  - Associate `<label>` with `for` attribute to input `id`.
  - Use `aria-describedby` for error messages.
  - Ensure keyboard navigable (Tab order logical).
  - Avoid reliance on color alone for state.

## Data Presentation (Tables, Cards, Lists)

- **Tables**:
  - Use `datagrid` component (based on TanStack Table) with:
    - Sortable headers (click to toggle asc/desc).
    - Pagination (top‑right) with page size selector.
    - Column resizing (optional).
    - Row actions menu (⋮) → edit/delete etc.
    - Empty state: friendly illustration + hint.
  - Alternate row colors: `bg-white` / `bg-slate-50`.
  - Header background: `bg-slate-50` `font-semibold`.
- **Cards**:
  - Standard job card:
    - Left: logo/company icon (40x40).
    - Middle: title (font-semibold), company, location badges.
    - Right: match score badge (circular progress or pill) + apply button.
    - Footer: posted date, salary range (if available).
  - Hover lifts slightly (`shadow-md → shadow-lg`).
  - Clickable entire card (except action buttons) navigates to detail.
- **Lists**:
  - Simple vertical list with divider (`border-t`) between items.
  - Avatar + two‑line text (primary + secondary).
  - Swipe‑to‑delete on mobile (if applicable).
- **Empty & Error States**:
  - Illustration (optional) + concise headline + helpful CTA.
  - Avoid vague “No results” – suggest adjusting filters or expanding search radius.

## Feedback & Messaging

- **Toast Notifications**:
  - Position: `top-right` (desktop), `bottom-center` (mobile).
  - Auto‑dismiss after 5 s (user can swipe/close).
  - Types: success, info, warning, error (matching color semantics).
- **Inline Validation**:
  - Show error message directly under field; highlight input border.
- **Loading States**:
  - Buttons: show spinner inside, disable click.
  - Pages: full‑screen skeleton layout or section‑specific placeholders.
  - Pull‑to‑refresh (mobile) with spinner.
- **Dialogs & Modals**:
  - Backdrop click to close (unless critical).
  - Escape key closes.
  - Focus trap inside dialog; return focus to trigger after close.
- **Confirmation Prompts**:
  - Use modal with destructive action button `btn-danger`.
- **Help & Tooltips**:
  - Appear on hover/focus; delayed 150ms; avoid covering actionable area.
  - Keep text short (< 120 characters).
  - Use `tooltip` from `@radix-ui/react-tooltip` or custom.

## Accessibility (a11y)

- **WCAG 2.1 AA** is the target.
- **Keyboard Navigation**:
  - All interactive elements reachable via Tab.
  - Logical tab order (header → main → footer).
  - Visible focus outline: `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-300`.
- **Screen Reader**:
  - Use semantic HTML (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`).
  - ARIA labels where visual label is absent (icon buttons).
  - Live regions for status updates (`aria-live="polite"` for toast, `assertive` for validation errors).
  - Avoid `role="presentation"` on meaningful elements.
- **Color Contrast**:
  - Test all text/background combos with contrast checker.
  - Ensure non‑color cues (icons, shape, text) supplement color‑only indicators.
- **Resize Text**:
  - Layout must remain usable at 200% zoom (no loss of content or functionality).
  - Use relative units (`rem`, `em`), avoid fixed `px` heights where content may grow.
- **Motion Sensitivity**:
  - Respect `prefers-reduced-motion`: disable or reduce animations.
  - Use `motion-safe:` and `motion-reduce:` modifiers.
- **Language & Direction**:
  - Support `ltr` and `rtl` via `dir` attribute on `<html>`.
  - Mirror layout appropriately (flex‑row‑reverse, etc.).
- **Accessibility Testing**:
  - Automated: `axe-core` in CI.
  - Manual: keyboard-only navigation, screen reader (NVDA/VoiceOver) weekly.

## Internationalisation (i18n)

- **Framework**: `next-i18next` or similar.
- **File Structure**: `locales/{lang}/common.json`.
- **Supported Languages**: Initially English (`en`); Spanish (`es`) and French (`fr`) planned.
- **Direction**: Detect `rtl` locales (Arabic, Hebrew) and apply appropriate CSS (`[dir="rtl"]`).
- **Date/Time Formatting**: Use `Intl.DateTimeFormat` with user locale.
- **Number & Currency**: Use `Intl.NumberFormat`.
- **Placeholder Text**: Translated; avoid concatenation.
- **Right‑to‑Left Adjustments**:
  - Flip horizontal margins/paddings.
  - Mirror icon direction (use `transform rotateY(180px)` if needed).
  - Ensure dropdowns open correctly.

## Motion & Animation

- **Principles**:
  - Purposeful: draw attention to state change, provide feedback.
  - Brief: ≤ 150 ms for most transitions.
  - Easing: `cubic-bezier(0.4, 0, 0.2, 1)` (default) for ease‑in‑out; `cubic-bezier(0.16, 1, 0.3, 1)` for ease‑out (entrance); `cubic-bezier(0.4, 0, 0.6, 1)` for ease‑in (exit).
- **Types**:
  - **Fade**: `opacity` transition.
  - **Slide**: `transform translateX/Y`.
  - **Scale**: `transform scale`.
  - **Shimmer**: Loading placeholders.
- **Implementation**:
  - Use Tailwind transition utilities: `transition-opacity duration-150`.
  - For complex motion, use `framer-motion` or CSS animations keyed via `data-state`.
  - Respect `prefers-reduced-motion` via `@media (prefers-reduced-motion: reduce) { * { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; } }`.
- **Loading Skeletons**:
  - Animated gradient (`animate-pulse`) on placeholder boxes.
- **Page Transitions**:
  - Optional fade between routes (using Next.js route transitions).
- **Micro‑interactions**:
  - Button press: scale down 2%.
  - Card hover: lift + shadow increase.
  - Input focus: ring glow.

## Usability Testing & Iteration

- **Methods**:
  - Remote moderated testing (via Lookback/Zoom) with job seekers.
  - Unmoderated tests (UserTesting.com) for specific flows.
  - Heatmaps & click tracking (Hotjar, Microsoft Clarity) on production.
- **Metrics**:
  - Task Success Rate (%).
  - Time on Task.
  - System Usability Scale (SUS) target ≥ 80.
  - Net Promoter Score (NPS) trend.
- **Iteration Cadence**:
  - Bi‑weekly design review.
  - Monthly release of UX improvements.
  - Continuous collection of in‑app feedback (thumb up/down, comment box).
- **Design Reviews**:
  - Include product, engineering, accessibility advocate.
  - Use checklist: contrast, touch target size (≥ 48 dp), focus order, error handling.

## Implementation Notes (Tailwind, Tailwind & shadcn/ui Integration

- **Tailwind Config (`tailwind.config.ts`)**:
  - `content`: `["./src/**/*.{ts,tsx}", "./components/**/*.tsx"]`.
  - `theme`: extend `colors`, `spacing`, `borderRadius`, `fontFamily`, `fontSize`.
  - `plugins`: `[require("@tailwindcss/forms"), require("@tailwindcss/typography")]`.
  - `preset`: `[require("@shadcn/ui/tailwind")]`.
- **Custom Variables** (in `src/styles/globals.css` or via `css`):
  - Define CSS variables for any design token not covered by tailwind (e.g., `--color-primary-600`).
- **Component Overrides**:
  - Place custom components in `src/components/ui/` that extend or wrap shadcn/ui primitives.
  - Example: `src/components/ui/button.tsx` exports a `Button` that applies our `btn-{variant}` classes.
- **Dark Mode** (if ever needed):
  - Use `class` strategy; define dark palette in `tailwind.config`.
  - Currently not required; keep `darkMode: false`.
- **Asset Optimization**:
  - Images via `next/image` with `loader="akamai"` or default.
  - SVGs as React components for size and color control (`{...props}`).
- **Performance**:
  - Purge unused CSS in production (`content` paths).
  - Enable `cacheTimeout` for static assets.
  - Lazy‑load heavy components (e.g., map, charts) via `React.lazy` + `Suspense`.

## Content Guidelines

- **Voice**: Helpful, professional, warm.
- **Tone**: Adapt to context:
  - Informational: neutral.
  - Encouraging: when user achieves a milestone (e.g., “Your resume is now searchable!”).
  - Empathetic: when presenting errors or rejections (“We couldn’t find a match; try broadening your filters.”).
- **Capitalization**: Sentence case for UI labels, titles, and messages. Title case only for logos or branded terms.
- **Punctuation**: Avoid exclamation overuse; use for positive affirmations only.
- **Numbers**: Use numerals in UI (“5 jobs”, “12 min read”). Spell out numbers at sentence start.
- **Date Format**:
  - Short: `Sep 14, 2025`.
  - Long: `September 14, 2025`.
  - Relative: “Posted 2 days ago” (if < 7 days), else show date.
- **Time Zones**:
  - Display times in user’s detected timezone (from browser or profile).
  - Store all timestamps UTC.
- **Error Messages**:
  - Avoid blaming language (“You entered an invalid email” → “Please enter a valid email address”).
  - Offer corrective action (`Try again`, `Use a different format`).
- **Help Text**:
  - Concise, one‑sentence max.
  - Use progressive disclosure (tooltip or expandable section) for advanced options.
- **Legal Text**:
  - Links to Terms, Privacy, Cookie Policy open in new tab.
  - Keep checkboxes for consent unchecked by default (opt‑in).
- **Microcopy for Buttons**:
  - Action‑verb first: “Save changes”, “Delete account”, “Invite teammate”.
  - Avoid vague “Submit”, “OK”.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*