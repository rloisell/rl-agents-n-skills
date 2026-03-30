---
name: bc-gov-design-system
description: BC Government Design System for React/Vite applications — npm packages, component usage (Header, Footer, Button), BC Sans font loading, design token CSS variables, and colour scheme. Use when building or reviewing BC Gov React frontends, replacing manual header/footer markup, or applying correct colour tokens instead of hard-coded hex values.
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: React 18+, Vite. Packages from npmjs.com (@bcgov/*). Validated against HelloNetworkWorld and DSC-modernization.
---

# BC Gov Design System — React Skill

Correct usage of the official BC Government Design System packages in React/Vite applications.

---

## npm Packages

Three packages are required for a compliant BC Gov React frontend:

| Package | Purpose | Import target |
|---------|---------|---------------|
| `@bcgov/design-system-react-components` | Header, Footer, Button, etc. | Named imports from package root |
| `@bcgov/bc-sans` | BC Sans font files (woff/woff2) bundled locally | `@bcgov/bc-sans/css/BC_Sans.css` |
| `@bcgov/design-tokens` | CSS custom properties (colour, spacing, radius) | `@bcgov/design-tokens/css/variables.css` |

```bash
npm install @bcgov/design-system-react-components @bcgov/bc-sans @bcgov/design-tokens
```

**Never** import fonts from `fonts2.gov.bc.ca` — that external URL will be blocked in
network-restricted or air-gapped environments. Always load BC Sans from the npm package.

---

## main.jsx — Required Import Order

CSS imports must appear in this exact order so design token variables are available
before component styles, and component styles are available before app overrides:

```js
import '@bcgov/bc-sans/css/BC_Sans.css';
import '@bcgov/design-tokens/css/variables.css';
import './index.css';   // app-level overrides last
```

---

## Header Component

`Header` renders the official blue BC Gov banner with the BC logo built in via its
internal `SvgBcLogo` component — **no static SVG asset is needed in `public/`**.

```jsx
import { Header } from '@bcgov/design-system-react-components';

<Header
  title="My Application"
  skipLinks={[<a key="main" href="#main-content">Skip to main content</a>]}
/>
```

Key props:

| Prop | Type | Notes |
|------|------|-------|
| `title` | string | Application name shown beside logo |
| `skipLinks` | ReactNode[] | Accessibility skip-nav links |
| `logoLinkElement` | ReactNode | Override the logo anchor (e.g. `<a href="/">`) |
| `logoImage` | ReactNode | Override the logo SVG entirely (rarely needed) |
| `children` | ReactNode | Additional header content (right-side slot) |

---

## Footer Component

```jsx
import { Footer, FooterLinks } from '@bcgov/design-system-react-components';

<Footer
  links={[
    <FooterLinks
      key="about"
      title="BC Government"
      links={[
        <a key="disclaimer"    href="https://www2.gov.bc.ca/gov/content/home/disclaimer">Disclaimer</a>,
        <a key="privacy"       href="https://www2.gov.bc.ca/gov/content/home/privacy">Privacy</a>,
        <a key="accessibility" href="https://www2.gov.bc.ca/gov/content/home/accessibility">Accessibility</a>,
        <a key="copyright"     href="https://www2.gov.bc.ca/gov/content/home/copyright">Copyright</a>,
      ]}
    />,
  ]}
/>
```

`FooterLinks` props: `title` (string), `links` (**array of React elements** — `<a>` nodes, NOT `{ label, href }` objects).
Passing plain objects to `links` causes *"Objects are not valid as a React child"* and a blank page.
`Footer` also accepts `acknowledgement` (string), `hideCopyright` (bool), `contact` (ReactNode).

---

## Design Tokens — CSS Variables

Always use these `var(--...)` references with a hard-coded hex fallback.
Import `@bcgov/design-tokens/css/variables.css` in `main.jsx` before app CSS.

### Colour Tokens

| Token | Value | Use for |
|-------|-------|---------|
| `--surface-color-primary-default` | `#013366` | BC Gov blue — headings, nav active, table headers, buttons |
| `--surface-color-primary-hover` | `#1E5189` | Hover on primary elements |
| `--surface-color-secondary-default` | `#FFFFFF` | Nav/card backgrounds (white) |
| `--surface-color-secondary-hover` | `#EDEBE9` | Hover background on nav links, secondary buttons |
| `--surface-color-background-white` | `#FFFFFF` | Card/modal background |
| `--surface-color-background-light-gray` | `#FAF9F8` | Page body background |
| `--surface-color-background-light-blue` | `#F1F8FE` | Info alert, table row hover |
| `--surface-color-background-dark-blue` | `#053662` | Dark accent panels |
| `--surface-color-border-default` | `#D8D8D8` | Card, table, input borders |
| `--surface-color-border-medium` | `#898785` | Input/select border (normal state) |
| `--surface-color-border-active` | `#2E5DD7` | Focus ring border |
| `--surface-color-overlay-default` | `rgba(0,0,0,0.45)` | Modal backdrop |
| `--surface-color-primary-button-default` | `#013366` | Primary button bg |
| `--surface-color-primary-button-hover` | `#1E5189` | Primary button hover |
| `--surface-color-primary-button-disabled` | `#606060` | Disabled state |
| `--surface-color-primary-danger-button-default` | `#CE3E39` | Danger/destructive button |
| `--surface-color-primary-danger-button-hover` | `#A2312D` | Danger button hover |
| `--support-surface-color-danger` | `#F4E1E2` | Error alert background |
| `--typography-color-primary` | `#313132` | Body text |
| `--typography-color-secondary` | `#595959` | Muted / helper text |
| `--typography-font-families-bc-sans` | BC Sans stack | Set on `body` font-family |

### Layout Tokens

| Token | Notes |
|-------|-------|
| `--layout-border-radius-large` | Card/button/input border-radius (4px) |
| `--layout-padding-large` | Standard large padding (24px) |
| `--layout-padding-medium` | Standard medium padding |
| `--layout-padding-small` | Standard small padding |

---

## Navigation Pattern (DSC / HNW Standard)

BC Gov Design System navigation is **white background with blue text** — not the old
dark-blue/yellow-stripe style. Use BEM class names on `<NavLink>` elements:

```css
/* White nav bar with bottom border */
.hnw-nav {
  background: var(--surface-color-secondary-default, #fff);
  border-bottom: 1px solid var(--surface-color-border-default, #d8d8d8);
  padding: 0 var(--layout-padding-large, 24px);
}

.hnw-nav__link {
  color: var(--surface-color-primary-default, #013366);
  border-bottom: 3px solid transparent;
}

.hnw-nav__link:hover {
  border-bottom-color: var(--surface-color-primary-hover, #1e5189);
  background-color: var(--surface-color-secondary-hover, #edebe9);
}

.hnw-nav__link--active {
  border-bottom-color: var(--surface-color-primary-default, #013366);
  font-weight: 700;
}
```

In React Router, apply the active class via:

```jsx
<NavLink
  to="/route"
  className={({ isActive }) =>
    isActive ? 'hnw-nav__link hnw-nav__link--active' : 'hnw-nav__link'
  }
>
  Label
</NavLink>
```

---

## Body Font Setup

Set on `body` in `index.css` — use the token with a complete fallback stack:

```css
body {
  font-family: var(
    --typography-font-families-bc-sans,
    "BC Sans", "Noto Sans", Verdana, Arial, sans-serif
  );
}
```

---

## What NOT To Do

| Anti-pattern | Correct approach |
|-------------|-----------------|
| `@import url("https://fonts2.gov.bc.ca/...")` | Import `@bcgov/bc-sans/css/BC_Sans.css` in `main.jsx` |
| Hard-code `#003366` or `#38598a` | Use `var(--surface-color-primary-default, #013366)` |
| Render `<img src="/bcid-logo-rev-en.svg">` | Use `<Header>` — logo is built in via `SvgBcLogo` |
| Manual `<div class="bcgov-header">` markup | Use `<Header>` component |
| Dark navy nav (`#38598a`) with yellow active stripe | White nav with blue underline active indicator |
| Load BC Sans only in Regular/Bold weights | Let the npm package supply all weights |

---

## Verified Version Matrix

| Package | Version | Status |
|---------|---------|--------|
| `@bcgov/design-system-react-components` | `^0.6.1` | ✅ Used in HNW + DSC-modernization |
| `@bcgov/bc-sans` | `^2.1.0` | ✅ Used in HNW + DSC-modernization |
| `@bcgov/design-tokens` | `^3.1.0` | ✅ Used in HNW + DSC-modernization |

---

## References

- [BC Gov Design System](https://gov.bc.ca/designsystem)
- [NPM: @bcgov/design-system-react-components](https://www.npmjs.com/package/@bcgov/design-system-react-components)
- [NPM: @bcgov/bc-sans](https://www.npmjs.com/package/@bcgov/bc-sans)
- [NPM: @bcgov/design-tokens](https://www.npmjs.com/package/@bcgov/design-tokens)
