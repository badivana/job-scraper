# Design Tokens

## Purpose

To define the centralized set of design tokens (values for spacing, colors, typography, shadows, border radii, etc.) that drive the visual consistency of the UI. These tokens are consumed by the frontend (Tailwind CSS configuration) and can be exported for use in design tools (Figma, Sketch) or other platforms.

## Contents

- Token Categories
- Naming Convention
- Color Tokens
- Spacing Tokens
- Typography Tokens
- Shadow & Elevation Tokens
- Border Radius Tokens
- Opacity Tokens
- Z‑Index Stack
- Usage in Code
- Export Formats
- Updating Tokens

## Token Categories

| Category | Description |
|----------|-------------|
| **Color** | Named colors for UI elements, states, and semantics. |
| **Spacing** | Margin, padding, gap, and layout distances (based on a 4 px grid). |
| **Typography** | Font family, sizes, weights, line heights, letter spacing. |
| **Elevation / Shadow** | Depth cues for cards, dialogs, floating action buttons. |
| **Border Radius** | Roundness of containers, inputs, buttons. |
| **Opacity** | Transparency levels for overlays, disabled states, hover effects. |
| **Z‑Index** | Layering order for modals, popovers, tooltips, fixed headers. |
| **Animation** | Duration and easing curves for transitions and motion. |
| **Breakpoints** | Screen width thresholds for responsive layouts. |

## Naming Convention

Tokens follow a hierarchical, delimiter‑separated pattern:
```
<category>.<sub‑category>.[state].[variant] (optional)
```
Examples: `color‑primary‑600`, `spacing‑lg`, `text‑base‑weight‑medium`, `radius‑md`, `shadow‑sm`.

Where applicable, we use suffixes for states:
- `‑hover`, `‑active`, `‑focus`, `‑disabled`.
For scales we use numeric levels (e.g., `‑100`, `‑200`, … `‑900`) analogous to Tailwind’s scale.

## Color Tokens

| Token | Value (HEX) | Usage |
|-------|-------------|-------|
| `color‑primary‑500` | #3B82F6 | Primary buttons, links |
| `color‑primary‑600` | #2563EB | Primary button hover, active |
| `color‑primary‑700` | #1D4ED8 | Pressed state |
| `color‑secondary‑500` | #64748B | Secondary buttons, icons |
| `color‑neutral‑50` | #F8FAFC | Page background, card background |
| `color‑neutral‑100` | #F1F5F9 | Input background, sidebar background |
| `color‑neutral‑200` | #E2E8F0 | Dividers, subtle borders |
| `color‑neutral‑600` | #475569 | Body text |
| `color‑neutral‑900` | #0F172A | Headings, high‑contrast text |
| `color‑success‑green** | #10B981 | Success, validation pass |
| `alert‑yellow` | #F59E0B | Warning, attention |
| `error‑red` | #EF4444 | Error, destructive actions |
| `info‑blue` | #3B82F6 | Informational banners (same as primary) |

Additional shades (e.g., `‑50`, `‑100`, `‑200`, `‑300`, `‑400`, `‑500`, `‑600`, `‑700`, `‑800`, `‑900`) are generated for each base hue to allow fine‑grained theming.

## Spacing Tokens

Base unit: 4 px. Tokens map to multiples of this unit.

| Token | Value (px) | rem (assuming 16 px base) |
|-------|------------|---------------------------|
| `spacing‑0` | 0 | 0 |
| `spacing‑xs` | 4 | 0.25 |
| `spacing‑sm` | 8 | 0.5 |
| `spacing‑md` | 12 | 0.75 |
| `spacing‑lg` | 16 | 1.0 |
| `spacing‑xl` | 20 | 1.25 |
| `spacing‑2xl` | 24 | 1.5 |
| `spacing‑3xl` | 32 | 2.0 |
| `spacing‑4xl` | 40 | 2.5 |
| `spacing‑5xl` | 48 | 3.0 |
| `spacing‑6xl` | 56 | 3.5 |
| `spacing‑7xl` | 64 | 4.0 |
| `spacing‑8xl` | 72 | 4.5 |
| `spacing‑9xl` | 80 | 5.0 |
| `spacing‑10xl`| 96 | 6.0 |
| `spacing‑12xl`| 128| 8.0 |

Used for `m-*`, `p-*`, `space-*`, `gap-*`, `margin‑*`, `padding‑*`.

## Typography Tokens

We adopt the **Inter** typeface (variable font) as the primary typeface.

### Font Family
```
font‑family‑base: "Inter", system-ui, sans-serif
```

### Font Sizes (px / rem)

| Token | Value (px) | rem |
|-------|-----------|-----|
| `text‑xs` | 12 | 0.75 |
| `text‑sm` | 14 | 0.875 |
| `text‑base` | 16 | 1.0 |
| `text‑lg` | 18 | 1.125 |
| `text‑xl` | 20 | 1.25 |
| `text‑2xl` | 24 | 1.5 |
| `text‑3xl` | 30 | 1.875 |
| `text‑4xl` | 36 | 2.25 |
| `text‑5xl` | 48 | 3.0 |
| `text‑6xl` | 60 | 3.75 |

### Font Weights
- `font‑weight‑light`: 300
- `font‑weight‑regular`: 400
- `font‑weight‑medium`: 500
- `font‑weight‑semibold`: 600
- `font‑weight‑bold`: 700
- `font‑weight‑extrabold`: 800

### Line Heights (unitless, relative to font size)

| Token | Value |
|-------|-------|
| `leading‑tight` | 1.2 |
| `leading‑snug`  | 1.35 |
| `default`       | 1.5 (used for body) |
| `leading‑relaxed`| 1.6 |
| `leading‑loose` | 2.0 |

### Letter Tracking (em)

| Token | Value |
|-------|-------|
| `tracking‑tighter` | -0.05 |
| `tracking‑tight`   | -0.025 |
| `tracking‑normal`  | 0 |
| `tracking‑wide`    | 0.025 |
| `tracking‑wider`   | 0.05 |

## Shadow & Elevation Tokens

We use a subtle shadow system for depth.

| Token | Value (CSS `box‑shadow`) | Usage |
|-------|--------------------------|-------|
| `shadow‑xs` | `0 1px 2px 0 rgba(0,0,0,0.05)` | Very subtle, inputs |
| `shadow‑sm` | `0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px 0 rgba(0,0,0,0.06)` | Buttons, cards |
| `shadow‑md` | `0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)` | Moderate elevation |
| `shadow‑lg` | `0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)` | Dialogs, modals |
| `shadow‑xl` | `0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.04)` | Large panels, dropdowns |
| `shadow‑2xl`| `0 25px 50px -12px rgba(0,0,0,0.25)` | Heavy overlays |

## Border Radius Tokens

| Token | Value (px) | Usage |
|-------|-----------|-------|
| `radius‑none` | 0 | Square elements |
| `radius‑xs` | 2 | Tight inputs, tags |
| `radius‑sm` | 4 | Small buttons, badges |
| `radius‑md` | 6 | Default cards, inputs |
| `radius‑lg` | 8 | Larger cards, modals |
| `radius‑full` | 9999 | Pills, circles, avatars |

## Opacity Tokens

| Token | Value |
|-------|-------|
| `opacity‑0` | 0 |
| `opacity‑25` | 0.25 |
| `opacity‑50` | 0.5 |
| `opacity‑75` | 0.75 |
| `opacity‑100` | 1 |

Used for disabled states, overlays, fade animations.

## Z‑Index Stack

We keep a limited, explicit range to avoid "z‑index wars".

| Layer | Value | Usage |
|-------|-------|-------|
| `z‑baseline` | 0 | Default flow |
| `z‑docked`   | 10 | Fixed header/footer |
| `z‑drops`    | 20 | Dropdowns, popovers |
| `z‑sticky`   | 30 | Sticky elements |
| `z‑bar`      | 40 | Fixed bars (e.g., chat widget) |
| `z‑modal`    | 100 | Modal backdrop |
| `z‑modal‑content`|105| Modal content |
| `z‑tooltip`  | 200 | Tooltips |
| `z‑popover`  | 250 | Popovers (slightly above tooltip) |
| `z‑drawer`   | 300 | Side drawers, off‑canvas menus |
| `z‑overlay`  | 500 | Full‑screen loader, screen lock |
| `z‑debug`    | 9999 | Debug outlines (only in dev) |

## Opacity Tokens (reiterated for completeness)

```
Opacity values usable anywhere (e.g., bg-opacity-50).
```

## Usage in Code

### Tailwind CSS (via `tailwind.config.ts`)

We extend the default theme with our tokens:

```ts
import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      colors: {
        primary: {
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
        },
        secondary: {
          500: '#64748B',
        },
        neutral: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          600: '#475569',
          900: '#0F172A',
        },
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#3B82F6',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px',
        '2xl': '24px',
        '3xl': '32px',
        '4xl': '40px',
        '5xl': '48px',
        '6xl': '56px',
        '7xl': '64px',
        '8xl': '72px',
        '9xl': '80px',
        '10xl': '96px',
        '12xl': '128px',
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.2' }],
        sm: ['0.875rem', { lineHeight: '1.35' }],
        base: ['1rem', { lineHeight: '1.5' }],
        lg: ['1.125rem', { lineHeight: '1.35' }],
        xl: ['1.25rem', { lineHeight: '1.4' }],
        '2xl': ['1.5rem', { lineHeight: '1.5' }],
        '3xl': ['1.875rem', { lineHeight: '1.3' }],
        '4xl': ['2.25rem', { lineHeight: '1.3' }],
        '5xl': ['3rem', { lineHeight: '1.3' }],
        '6xl': ['3.75rem', { lineHeight: '1.2' }],
      },
      fontWeight: {
        light: 300,
        regular: 400,
        medium: 500,
        semibold: 600,
        bold: 700,
        extrabold: 800,
      },
      borderRadius: {
        none: '0px',
        xs: '2px',
        sm: '4px',
        md: '6px',
        lg: '8px',
        full: '9999px',
      },
      boxShadow: {
        xs: '0 1px 2px 0 rgba(0,0,0,0.05)',
        sm: '0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px 0 rgba(0,0,0,0.06)',
        md: '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)',
        lg: '0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)',
        xl: '0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.04)',
        '2xl': '0 25px 50px -12px rgba(0,0,0,0.25)',
      },
      zIndex: {
        baseline: 0,
        docked: 10,
        drops: 20,
        sticky: 30,
        bar: 40,
        modal: 100,
        'modal-content': 105,
        tooltip: 200,
        popover: 250,
        drawer: 300,
        overlay: 500,
        debug: 9999,
      },
    },
  },
  plugins: [],
};
```

### In JSX/TSX

```tsx
import { cn } from '@/lib/utils';

<button className={cn(
  'bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors'
)}>
  Save
</button>
```

### Export Formats

- **JSON**: `tokens.json` – flat key/value map for consumption by design tools or other services.
- **TS Module**: `tokens.ts` – exported constants (as above) for direct import.
- **SCSS Map**: `tokens.scss` – `$map: (...)` for Sass‑based projects.
- **Figma Plugin**: Can import the JSON to create style definitions.

## Updating Tokens

1. **Identify Need**: New color, spacing, or typographic requirement (e.g., a new brand accent).
2. **Add Token**: Choose an appropriate level in the existing scale or create a new named token if it doesn’t fit.
3. **Update `tailwind.config.ts`**: Insert the new value in the relevant section.
4. **Update Documentation**: Reflect the change in this file and any component usage guides.
5. **Run Visual Regression**: Ensure existing components remain unaffected (or update them appropriately).
6. **Commit & Push**: Changes flow through CI; staged environments update automatically.
7. **Optional**: Publish a new version of the design‑token package if distributed as an npm package.

## Accessibility Considerations

- Contrast ratios are checked against WCAG 2.1 AA for all text/background combinations.
- All interactive components meet a minimum touch target of 48 px (achieved via sufficient padding and minimum dimensions).
- Focus visible outlines use `color‑primary‑500` with an offset of 2 px (`ring-2 ring-primary-500`).

## Related Documents

- `docs/UI_UX_GUIDELINES.md` – usage guidelines, component specifications, accessibility.
- `docs/CODING_STANDARDS.md` – frontend tech stack (Tailwind, shadcn/ui).
- `assets/color_palette.md` – complementary detail on color semantics.
- `assets/typography.md` – deeper dive into type scale, line heights, language support.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*