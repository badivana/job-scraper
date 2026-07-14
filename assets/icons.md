# Icons

## Purpose

To standardize the use of icons across the AI-Powered Job Finder interface, ensuring clarity, consistency, and scalability.

## Contents

- Icon Set
- Sizes
- Styles
- Usage Guidelines
- Implementation (React)
- Accessibility

## Icon Set

We use **Heroicons** (outline and solid styles) as our primary icon library. Heroicons are a set of free, MIT‑licensed SVG icons designed by the creators of Tailwind CSS.

- Outline: for neutral, secondary actions.
- Solid: for emphasized, primary actions, or to denote state (e.g., filled star for saved).

## Sizes

Icon sizes are based on the 4px grid and correspond to Tailwind's spacing units:

| Size | Width/Height | Use Case |
|------|--------------|----------|
| 12px | h-3 w-3      | Small inline icons (e.g., in buttons with text) |
| 16px | h-4 w-4      | Default size for most icons |
| 20px | h-5 w-5      | Toolbar icons, list item icons |
| 24px | h-6 w-6      | Large icons, standalone icons |
| 32px | h-8 w-8      | Feature highlights, empty states |

## Styles

- **Stroke**: 1.5px (default for Heroicons outline).
- **Fill**: none for outline; solid fill for solid variants.
- **Color**: Inherit `text-current` by default; apply semantic colors when needed (e.g., red for error, green for success).

## Usage Guidelines

- Use icons to supplement text, not replace it, unless the icon is universally recognized (e.g., search, home, menu).
- Keep icon meaning clear and consistent across the app.
- Do not modify the icon paths; if a custom icon is needed, submit it for review and add to the library under `src/assets/icons/custom`.
- Prefer SVG sprites or inline SVGs for performance and style control.
- When using Tailwind, you can apply classes directly to the SVG element.

## Implementation (React)

We import Heroicons from `@heroicons/react` (or `/optimized`). Example:

```jsx
import { SearchIcon } from '@heroicons/react/outline';

<button className="flex items-center gap-2">
  <SearchIcon className="h-4 w-4 text-slate-600" />
  Search jobs
</button>
```

For solid variants, import from `/solid`.

## Accessibility

- Always provide an accessible name for icon-only buttons via `aria-label` or `aria-labelledby`.
- If the icon is purely decorative, hide it from screen readers with `aria-hidden="true"`.
- Ensure sufficient contrast between the icon color and its background (≥3:1 for UI components).

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*
