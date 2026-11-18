## Contents

- [npm Packages](#npm-packages)
- [main.jsx Required Import Order](#mainjsx-required-import-order)
- [Header Component](#header-component)
- [Footer Component](#footer-component)
- [Navigation Pattern](#navigation-pattern)
- [Body Font Setup](#body-font-setup)
- [What NOT To Do & Verified Versions](#what-not-to-do--verified-versions)

# BC Gov Design System (React / Vite)

## npm Packages

Three packages are required for a compliant BC Gov React frontend:

| Package | Purpose | Import target |
|---|---|---|
| `@bcgov/design-system-react-components` | Header, Footer, Button, etc. | Named imports from package root |
| `@bcgov/bc-sans` | BC Sans font files (woff/woff2) bundled locally | `@bcgov/bc-sans/css/BC_Sans.css` |
| `@bcgov/design-tokens` | CSS custom properties (colour, spacing, radius) | `@bcgov/design-tokens/css/variables.css` |

```bash
npm install @bcgov/design-system-react-components @bcgov/bc-sans @bcgov/design-tokens
```

**Never** import fonts from `fonts2.gov.bc.ca` — that external URL is blocked in network-restricted or air-gapped environments. Always load BC Sans from the npm package.

## main.jsx Required Import Order

CSS imports must appear in this exact order so design token variables are available before component styles, and component styles are available before app overrides:

```js
import '@bcgov/bc-sans/css/BC_Sans.css';
import '@bcgov/design-tokens/css/variables.css';
import './index.css'; // app-level overrides last
```

## Header Component

`Header` renders the official blue BC Gov banner with the BC logo built in via its internal `SvgBcLogo` component — **no static SVG asset is needed in `public/`**.

```jsx
import { Header } from '@bcgov/design-system-react-components';

<Header
  title="My Application"
  skipLinks={[<a key="main" href="#main-content">Skip to main content</a>]}
/>
```

Key props:

| Prop | Type | Notes |
|---|---|---|
| `title` | string | Application name shown beside logo |
| `skipLinks` | ReactNode[] | Accessibility skip-nav links |
| `logoLinkElement` | ReactNode | Override the logo anchor (e.g. `<a href="/">`) |
| `logoImage` | ReactNode | Override the logo SVG entirely (rarely needed) |
| `children` | ReactNode | Additional header content (right-side slot) |

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

`FooterLinks` props: `title` (string), `links` (**array of React elements** — `<a>` nodes, NOT `{ label, href }` objects). Passing plain objects to `links` causes *"Objects are not valid as a React child"* and a blank page. `Footer` also accepts `acknowledgement` (string), `hideCopyright` (bool), and `contact` (ReactNode).

## Navigation Pattern

BC Gov Design System navigation is **white background with blue text** — not the old dark-blue/yellow-stripe style. Use BEM class names on `<NavLink>` elements:

```css
/* White nav bar with bottom border */
.app-nav {
  background: var(--surface-color-secondary-default, #fff);
  border-bottom: 1px solid var(--surface-color-border-default, #d8d8d8);
  padding: 0 var(--layout-padding-large, 24px);
}

.app-nav__link {
  color: var(--surface-color-primary-default, #013366);
  border-bottom: 3px solid transparent;
}

.app-nav__link:hover {
  border-bottom-color: var(--surface-color-primary-hover, #1e5189);
  background-color: var(--surface-color-secondary-hover, #edebe9);
}

.app-nav__link--active {
  border-bottom-color: var(--surface-color-primary-default, #013366);
  font-weight: 700;
}
```

In React Router, apply the active class via:

```jsx
<NavLink
  to="/route"
  className={({ isActive }) =>
    isActive ? 'app-nav__link app-nav__link--active' : 'app-nav__link'
  }
>
  Label
</NavLink>
```

## Body Font Setup

Set on `body` in `index.css` using the token with a complete fallback stack:

```css
body {
  font-family: var(
    --typography-font-families-bc-sans,
    "BC Sans", "Noto Sans", Verdana, Arial, sans-serif
  );
}
```

## What NOT To Do & Verified Versions

| Anti-pattern | Correct approach |
|---|---|
| `@import url("https://fonts2.gov.bc.ca/...")` | Import `@bcgov/bc-sans/css/BC_Sans.css` in `main.jsx` |
| Hard-code `#003366` or `#38598a` | Use `var(--surface-color-primary-default, #013366)` |
| Render `<img src="/bcid-logo-rev-en.svg">` | Use `<Header>` — logo is built in via `SvgBcLogo` |
| Manual `<div class="bcgov-header">` markup | Use `<Header>` component |
| Dark navy nav (`#38598a`) with yellow active stripe | White nav with blue underline active indicator |
| Load BC Sans only in Regular/Bold weights | Let the npm package supply all weights |

Verified version matrix:

- `@bcgov/design-system-react-components`: `^0.6.1`
- `@bcgov/bc-sans`: `^2.1.0`
- `@bcgov/design-tokens`: `^3.1.0`
