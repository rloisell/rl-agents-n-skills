# React OIDC Setup (`oidc-client-ts`)

## Install

```bash
npm install oidc-client-ts react-oidc-context
```

## Auth Config

```js
// src/auth/authConfig.js — OIDC UserManager config
export const oidcConfig = {
  authority:                import.meta.env.VITE_OIDC_AUTHORITY,
  // e.g. https://loginproxy.gov.bc.ca/auth/realms/standard
  client_id:                import.meta.env.VITE_OIDC_CLIENT_ID,
  redirect_uri:             `${window.location.origin}/callback`,
  post_logout_redirect_uri: `${window.location.origin}/`,
  response_type:            'code',
  scope:                    'openid profile email',
  automaticSilentRenew:     true,
  silent_redirect_uri:      `${window.location.origin}/silent-callback.html`,
  monitorSession:           true,
  filterProtocolClaims:     true,
  loadUserInfo:             true,
};
```

## Provider Wrapping

```jsx
// src/main.jsx
import { AuthProvider } from 'react-oidc-context';
import { oidcConfig } from './auth/authConfig';

root.render(
  <AuthProvider {...oidcConfig}>
    <App />
  </AuthProvider>
);
```

## Callback Page

```jsx
// src/pages/Callback.jsx — redirect landing page
import { useAuth } from 'react-oidc-context';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

export default function Callback() {
  const auth = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!auth.isLoading && !auth.error) navigate('/');
  }, [auth.isLoading, auth.error]);

  if (auth.error) return <div>Login error: {auth.error.message}</div>;
  return <div>Logging in…</div>;
}
```

## Silent Renew Page

Create `/public/silent-callback.html`:

```html
<!doctype html>
<html><body>
<script src="/oidc-client-ts/dist/browser/oidc-client-ts.min.js"></script>
<script>new oidc.UserManager().signinSilentCallback();</script>
</body></html>
```

## Using the Token in API Calls

```js
// src/api/apiClient.js — axios interceptor using shared UserManager instance
import { UserManager } from 'oidc-client-ts';
import { oidcConfig } from '../auth/authConfig';
import axios from 'axios';

// Share the same UserManager instance used by AuthProvider
export const userManager = new UserManager(oidcConfig);

const apiClient = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL });

apiClient.interceptors.request.use(async (config) => {
  const user = await userManager.getUser();
  if (user?.access_token) {
    config.headers.Authorization = `Bearer ${user.access_token}`;
  }
  return config;
});

export default apiClient;
```

Alternatively, inside a React component or hook, read the token directly from `auth.user?.access_token` (via `useAuth()` from `react-oidc-context`) rather than creating a second `UserManager` instance.
