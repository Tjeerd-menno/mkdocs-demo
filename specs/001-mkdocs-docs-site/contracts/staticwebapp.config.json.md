# Contract: staticwebapp.config.json

**File**: `/staticwebapp.config.json`
**Purpose**: Azure Static Web Apps routing and authentication configuration. This file is committed to the repository root and deployed alongside the built site output.

---

```json
{
  "auth": {
    "identityProviders": {
      "azureActiveDirectory": {
        "userDetailsClaim": "emails",
        "registration": {
          "openIdIssuer": "https://login.microsoftonline.com/<YOUR_TENANT_ID>/v2.0",
          "clientIdSettingName": "AAD_CLIENT_ID",
          "clientSecretSettingName": "AAD_CLIENT_SECRET"
        }
      }
    }
  },
  "routes": [
    {
      "route": "/.auth/*",
      "allowedRoles": ["anonymous"]
    },
    {
      "route": "/*",
      "allowedRoles": ["authenticated"]
    }
  ],
  "responseOverrides": {
    "401": {
      "statusCode": 302,
      "redirect": "/.auth/login/aad"
    }
  },
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/assets/*", "/reference/openapi/*", "/versions.json"]
  }
}
```

---

## Configuration decisions

| Field | Value | Rationale |
|-------|-------|-----------|
| Custom `azureActiveDirectory` provider | tenant-restricted | The built-in `aad` provider accepts any Microsoft account. A custom provider config with `openIdIssuer` pointing to your specific tenant restricts access to internal users only. This is non-negotiable for an internal site. |
| `AAD_CLIENT_ID`, `AAD_CLIENT_SECRET` | App settings (not secrets in config) | Sensitive values are stored as Azure Static Web Apps application settings (environment variables), not hardcoded in this config file. |
| `/.auth/*` anonymous | Allows the auth flow itself to operate without being blocked by the catch-all authenticated rule |
| `/*` → authenticated | Every URL requires sign-in |
| `401 → 302 → /.auth/login/aad` | Redirects unauthenticated browsers to Entra ID login rather than showing an error page |
| `navigationFallback` | Enables `mike`-style clean URLs within each version (mike generates `index.html` per directory) |
| `exclude` from fallback | Static assets and OpenAPI YAML are served directly; they must not be rewritten to `index.html` |

---

## Azure app registration steps (not automated — do manually once)

1. Register an app in Entra ID (Azure Portal → App registrations → New registration).
2. Set Redirect URI: `https://<your-swa-hostname>/.auth/login/aad/callback`
3. Go to **Certificates & secrets** → create a client secret. Copy its value.
4. Go to **Overview** → copy the Application (client) ID.
5. In Azure Static Web Apps → **Configuration** → add application settings:
   - `AAD_CLIENT_ID` = the client ID from step 4
   - `AAD_CLIENT_SECRET` = the secret value from step 3
6. Replace `<YOUR_TENANT_ID>` in `staticwebapp.config.json` with your tenant ID (found in Azure Portal → Azure Active Directory → Overview).
