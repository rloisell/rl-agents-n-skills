# BC Gov Design System Integration Layer

> **Single Source of Truth:** Do **not** duplicate Design System rules here. Invoke the dedicated [`bc-gov-design-system`](https://github.com/richfrem/bc-gov-design-system) skill in **`react` mode** for:
> - `@bcgov/design-system-react-components` (`Header`, `Footer`, `FooterLinks`, `Button`, etc.)
> - `@bcgov/bc-sans` (self-hosted font, never `fonts2.gov.bc.ca`)
> - `@bcgov/design-tokens` (v5 `--color-*` / `--text-*` / `--surface-*` tokens, WCAG 2.1 AA, sentence case, Indigenous acknowledgment footer)

## Install the Upstream Skill

```bash
apm install https://github.com/richfrem/bc-gov-design-system --global --target claude,copilot,codex,agy
```

## React / Vite + OIDC Integration Points (Owned by This Layer)

1. **`main.jsx` CSS import order + `<AuthProvider>`**:
   ```jsx
   import '@bcgov/bc-sans/css/BC_Sans.css';
   import '@bcgov/design-tokens/css/variables.css';
   import './index.css'; // app overrides last
   ```
   Wrap `<App />` in `<AuthProvider {...oidcConfig}>` from `react-oidc-context` (see [react-oidc-client-ts.md](react-oidc-client-ts.md)).

2. **Wire OIDC auth controls into `<Header>`**:
   Pass the authenticated user display name and Sign In / Sign Out action into `<Header>`'s right-side `children` slot, keeping `skipLinks` and `logoLinkElement` compliant with `bc-gov-design-system` (`react` mode).

3. **`react-router-dom` navigation**:
   Use `<NavLink>` inside a white-background nav bar below `<Header>` with Design System CSS tokens (never hard-coded hex values).

4. **Known React gotcha**:
   Pass React `<a>` elements (not `{ label, href }` plain objects) to `<FooterLinks links={[...]} />`.
