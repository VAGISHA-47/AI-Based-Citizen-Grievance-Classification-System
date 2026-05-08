# GitHub Codespaces Configuration - Frontend/Backend Communication

## Problem Encountered
When running in GitHub Codespaces, the frontend and backend couldn't communicate because:
- Frontend was trying to reach `http://127.0.0.1:8000` (localhost)
- But browsers can't access `127.0.0.1` from a Codespaces domain (`*.app.github.dev`)
- This resulted in "Failed to fetch" errors

## Solution Applied

### 1. Frontend .env Updated
**File:** `frontend/.env`
```env
# OLD (doesn't work in GitHub Codespaces)
VITE_API_URL=http://127.0.0.1:8000

# NEW (works in GitHub Codespaces)
VITE_API_URL=https://organic-trout-v6p95wvxr5pj36ww9-8000.app.github.dev
```

### 2. Backend CORS Updated  
**File:** `backend/app/main.py`

Added the Codespaces frontend domain to the CORS allowed origins:
```python
allowed_origins = [
    "http://localhost:5173",          # Local development
    "http://127.0.0.1:5173",         # Local (127.0.0.1)
    "http://localhost:3000",         # Alternative local
    "http://127.0.0.1:3000",         # Alternative local
    "https://organic-trout-v6p95wvxr5pj36ww9-5174.app.github.dev",  # GitHub Codespaces
]
```

## How GitHub Codespaces Port Forwarding Works

When you have:
- **Frontend on Port 5174:** `https://organic-trout-v6p95wvxr5pj36ww9-5174.app.github.dev`
- **Backend on Port 8000:** `https://organic-trout-v6p95wvxr5pj36ww9-8000.app.github.dev`

The pattern is:
```
https://<CODESPACE_NAME>-<PORT>.app.github.dev
```

Where `<CODESPACE_NAME>` is: `organic-trout-v6p95wvxr5pj36ww9`

## Access Points

| Component | Local URL | Codespaces URL |
|-----------|-----------|-----------------|
| Frontend | `http://localhost:5174` | `https://organic-trout-v6p95wvxr5pj36ww9-5174.app.github.dev` |
| Backend | `http://localhost:8000` | `https://organic-trout-v6p95wvxr5pj36ww9-8000.app.github.dev` |

## For Future Reference

When working with different environments:

### Local Development (Laptop/Desktop)
```env
VITE_API_URL=http://127.0.0.1:8000
# or
VITE_API_URL=http://localhost:8000
```

### GitHub Codespaces
```env
# Replace with your actual Codespace name
VITE_API_URL=https://<CODESPACE_NAME>-8000.app.github.dev
```

### Production / Remote Server
```env
VITE_API_URL=https://api.yourdomain.com
```

## Testing the Connection

### Check Backend Health
```bash
curl https://organic-trout-v6p95wvxr5pj36ww9-8000.app.github.dev/health
```

### Test CORS from Frontend Domain
```bash
curl -X OPTIONS https://organic-trout-v6p95wvxr5pj36ww9-8000.app.github.dev/ \
  -H "Origin: https://organic-trout-v6p95wvxr5pj36ww9-5174.app.github.dev" \
  -v
```

## Notes

- GitHub Codespaces automatically upgrades HTTP to HTTPS for port-forwarded domains
- Ports must be explicitly configured (5173 for frontend, 8000 for backend)
- Each Codespace has a unique domain name based on `CODESPACE_NAME`
- The `app.github.dev` domain is always used for port forwarding

## Making It Dynamic (Optional Enhancement)

For a more robust solution, you could:
1. Detect the current environment
2. Automatically construct the API URL based on available env variables

Example in vite.config.js or App.jsx:
```javascript
const getApiUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Auto-detect Codespaces
  if (window.location.hostname.includes('.app.github.dev')) {
    const host = window.location.hostname.split('-')[0];
    const port = 8000;
    return `https://${host}-${port}.app.github.dev`;
  }
  
  // Fallback to localhost
  return 'http://127.0.0.1:8000';
};
```

---

**Current Status:** ✅ Frontend-Backend communication should now work from GitHub Codespaces
