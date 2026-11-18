# BC Gov Design Tokens

Always use `var(--...)` references with a hard-coded hex fallback. Import `@bcgov/design-tokens/css/variables.css` in `main.jsx` before app CSS.

## Colour Tokens

| Token | Value | Use for |
|---|---|---|
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

## Layout Tokens

| Token | Notes |
|---|---|
| `--layout-border-radius-large` | Card/button/input border-radius (4px) |
| `--layout-padding-large` | Standard large padding (24px) |
| `--layout-padding-medium` | Standard medium padding |
| `--layout-padding-small` | Standard small padding |

## Official References

- [BC Gov Design System](https://gov.bc.ca/designsystem)
- [NPM: @bcgov/design-system-react-components](https://www.npmjs.com/package/@bcgov/design-system-react-components)
- [NPM: @bcgov/bc-sans](https://www.npmjs.com/package/@bcgov/bc-sans)
- [NPM: @bcgov/design-tokens](https://www.npmjs.com/package/@bcgov/design-tokens)
