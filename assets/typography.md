# Typography

## Purpose

To define the typographic system for the AI-Powered Job Finder, ensuring readable, accessible, and visually consistent text across all platforms.

## Contents

- Font Family
- Font Weights
- Font Sizes
- Line Heights
- Letter Spacing
- Text Styles
- Usage Guidelines
- Accessibility
- Web Font Loading

## Font Family

We use **Inter** as our primary typeface for both headings and body text. Inter is a freely available, open‑source font designed for user interfaces, with excellent legibility on screens.

- Primary: `Inter`, sans-serif
- Fallback: `system-ui`, `sans-serif`

## Font Weights

| Weight | Numeric | Use Case |
|--------|---------|----------|
| Light | 300 | Optional for light headings (rarely used) |
| Regular | 400 | Body text |
| Medium | 500 | Sub‑headings, UI controls |
| SemiBold | 600 | Section headings, strong emphasis |
| Bold | 700 | Page titles, prominent headings |
| ExtraBold | 800 | Logos, special highlights |

## Font Sizes

Base size: 16px (`text-base` in Tailwind). All sizes are multiples of 4px for consistent vertical rhythm.

| Size | px | rem | Use Case |
|------|----|-----|----------|
| xs | 12 | 0.75 | Captions, helper text |
| sm | 14 | 0.875 | Small labels, footnotes |
| base | 16 | 1 | Body text, form inputs |
| lg | 18 | 1.125 | Sub‑headings |
| xl | 20 | 1.25 | Section headings |
| 2xl | 24 | 1.5 | Page titles, large headings |
| 3xl | 30 | 1.875 | Hero titles |
| 4xl | 36 | 2.25 | Extra‑large headings (rare) |
| 5xl | 48 | 3 | Extra‑extra‑large (marketing) |
| 6xl | 60 | 3.75 | Ultra‑large (exceptional) |

## Line Heights

| Name | Value | Use Case |
|------|-------|----------|
| tight | 1.25 | Headings, compact text |
| snug | 1.375 | Tight‑fit headings |
| normal | 1.5 | Default body text |
| relaxed | 1.625 | Comfortable reading (used for body) |
| loose | 2.0 | Very open text (quotes, poetry) |

We use `leading-relaxed` (1.625) for body text and `leading-snug` (1.375) for headings.

## Letter Spacing

| Tracking | Value | Use Case |
|----------|-------|----------|
| tighter | -0.05em | Headings (optional) |
| tight | -0.025em | Headings |
| normal | 0 | Body text |
| wide | 0.025em | All caps, letter‑spacing effect |
| wider | 0.05em | Large all‑caps |

We use `tracking-normal` for body and `tracking-tight` for headings.

## Text Styles

We define reusable Tailwind classes via `@layer utilities` or extract them as constants in JavaScript/TS if needed.

Examples:
- `body-base`: `text-base text-slate-900 leading-relaxed`
- `heading-sm`: `text-sm font-semibold text-slate-900 leading-snug`
- `heading-lg`: `text-lg font-bold text-slate-900 leading-snug`
- `caption`: `text-xs text-slate-500`

## Usage Guidelines

- **Hierarchy**: Use no more than three levels of heading hierarchy in a single view.
- **Consistency**: Apply the same text style to similar elements (e.g., all form labels use `caption`).
- **Responsiveness**: Scale font sizes with breakpoints if needed (e.g., `text-lg md:text-xl`).
- **Alignment**: Left‑align body text; center‑align short headings or call‑to‑actions; right‑align only for specific data (e.g., currency in tables).
- **Decoration**: Avoid underlining text unless it is a link. Use `font-semibold` or color for emphasis instead.

## Accessibility

- **Contrast**: Ensure text meets WCAG 2.1 AA contrast (≥4.5:1 for normal text, ≥3:1 for large text) against its background.
- **Scaling**: Layout must remain functional and readable when text is scaled up to 200% (browser zoom or user font size increase).
- **Avoid Text in Images**: Prefer actual text over images of text for localization and accessibility.
- **Line Length**: Aim for 45–75 characters per line for optimal readability.

## Web Font Loading

We self‑host Inter via `next/font` to eliminate external requests and prevent layout shift.

```js
// In src/app/layout.js
import { Inter } from 'next/font/google';
export const inter = Inter({ subsets: ['latin'] });

// Then use in CSS: className={`${inter.className} ...`}
```

Subsets are limited to Latin to reduce file size; expand if needed for other languages.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*
