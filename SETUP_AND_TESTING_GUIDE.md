# Full Stack Commands & Testing Guide

## 📦 PROJECT STRUCTURE
```
/workspaces/AI-Based-Citizen-Grievance-Classification-System/
├── backend/               # FastAPI server (Port 8000)
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── db/           # Database layer
│   │   ├── services/     # Business logic
│   │   ├── main.py       # App entry point
│   │   └── config.py     # Config/settings
│   ├── .env              # Backend environment (dev)
│   ├── requirements.txt   # Python dependencies
│   └── pytest.ini        # Test configuration
│
├── frontend/             # React + Vite (Port 5173)
│   ├── src/
│   │   ├── services/     # API client
│   │   ├── store/        # Zustand auth store
│   │   ├── apps/         # Page components
│   │   └── components/   # Reusable components
│   ├── .env              # Frontend environment
│   ├── package.json      # Dependencies
│   └── vite.config.js    # Vite configuration
```

---

## 🚀 STEP-BY-STEP SETUP

### Step 1: Navigate to Project Root
```bash
cd /workspaces/AI-Based-Citizen-Grievance-Classification-System
```

### Step 2: Backend Setup & Run

#### 2a. Install Backend Dependencies (One-time)
```bash
cd backend
pip install -r requirements.txt
```

#### 2b. Verify Backend .env
```bash
cat backend/.env
# Should output:
# DATABASE_URL=sqlite:///./grievances.db
# MONGO_URI=mongodb://127.0.0.1:27017/jansetu
# REDIS_URL=redis://127.0.0.1:6379/0
# SECRET_KEY=dev-secret-key-change-in-production
```

#### 2c. Run Backend Server
```bash
cd backend
export $(cat .env | xargs)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/workspaces/...']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 3: Frontend Setup & Run

#### 3a. Install Frontend Dependencies (One-time)
```bash
cd frontend
npm install
```

#### 3b. Verify Frontend .env
```bash
cat frontend/.env
# Should output:
# VITE_API_URL=http://127.0.0.1:8000
```

#### 3c. Run Frontend Dev Server
```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

**Expected Output:**
```
  VITE v8.0.10  ready in 372 ms

  ➜  Local:   http://127.0.0.1:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 🧪 TESTING ENDPOINTS

### Test 1: Backend Health Check
```bash
# In new terminal:
curl -X GET http://127.0.0.1:8000/health

# Expected Response:
# {"status":"ok"}
```

### Test 2: CORS Configuration
```bash
curl -X OPTIONS http://127.0.0.1:8000/ \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -v

# Look for these headers in response:
# access-control-allow-origin: http://localhost:5173
# access-control-allow-methods: *
# access-control-allow-headers: *
```

### Test 3: Login Endpoint
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "password":"test123"
  }'

# Expected Response:
# {
#   "access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type":"bearer"
# }
```

### Test 4: Get User Profile (Requires Token)
```bash
# First, get a token from Test 3
TOKEN="<paste_token_from_test_3>"

curl -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected Response:
# {"email":"test@example.com","sub":"test@example.com"}
```

### Test 5: Submit Grievance
```bash
# First, get a token
TOKEN="<paste_token_from_test_3>"

curl -X POST http://127.0.0.1:8000/grievances/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Broken Road" \
  -F "description=Road has large potholes near Junction" \
  -F "citizen_name=John Doe" \
  -F "citizen_phone=+919876543210" \
  -F "lat=19.076" \
  -F "lng=72.877"

# Expected Response:
# {
#   "message":"Grievance submitted",
#   "status":"processing",
#   "grievance_id":"<mongo_id>"
# }
```

### Test 6: Get Officer Assigned Complaints
```bash
TOKEN="<paste_token_from_test_3>"

curl -X GET http://127.0.0.1:8000/officer/assigned \
  -H "Authorization: Bearer $TOKEN"

# Expected Response:
# {
#   "message":"Assigned grievances endpoint ready",
#   "officer_id":"mock-officer-id",
#   "grievances":[],
#   "note":"Database query will be integrated later"
# }
```

### Test 7: Get Analytics Summary
```bash
TOKEN="<paste_token_from_test_3>"

curl -X GET http://127.0.0.1:8000/officer/analytics/summary \
  -H "Authorization: Bearer $TOKEN"

# Expected Response (placeholder):
# Mock analytics data
```

---

## 🔍 DIAGNOSTICS

### Check if Backend is Running
```bash
curl http://127.0.0.1:8000/health && echo "" || echo "Backend not running"
```

### Check if Frontend is Running  
```bash
curl http://127.0.0.1:5173 && echo "" || echo "Frontend not running"
```

### View Backend Logs
```bash
# Already visible in terminal where backend is running
# Look for: INFO, WARNING, ERROR messages
```

### View Frontend Logs
```bash
# Already visible in terminal where frontend is running
# Look for: compilation errors, warning messages
```

### Check Port Usage
```bash
# Check port 8000 (Backend)
lsof -i :8000

# Check port 5173 (Frontend)
lsof -i :5173

# Kill process using port (if needed)
kill -9 <PID>
```

---

## 🔧 COMMON ISSUES & SOLUTIONS

### Issue: "Port 8000 already in use"
```bash
# Solution 1: Kill existing process
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Solution 2: Use different port
cd backend
uvicorn app.main:app --port 9000 --reload
# Then update frontend .env: VITE_API_URL=http://127.0.0.1:9000
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
```bash
# Reinstall backend dependencies
cd backend
pip install --force-reinstall -r requirements.txt
```

### Issue: "Command not found: npm"
```bash
# Install Node.js (if not installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### Issue: "CORS error in browser console"
```bash
# Check backend CORS config in backend/app/main.py
# Ensure frontend origin is in allowed_origins list

# Restart backend after changes
# (Backend has auto-reload enabled)
```

### Issue: "JWT token invalid/expired"
```bash
# Get a new token by logging in again
# Frontend automatically stores in localStorage["jansetu_token"]

# Or test with curl:
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "password":"test123"
  }'
```

---

## 📋 VERIFICATION CHECKLIST

- [ ] Backend running on http://0.0.0.0:8000
- [ ] Frontend running on http://0.0.0.0:5173
- [ ] Backend health check returns `{"status":"ok"}`
- [ ] CORS headers present in OPTIONS response
- [ ] Login endpoint returns valid JWT token
- [ ] Frontend can fetch from backend (no CORS errors)
- [ ] Grievance submission works with auth token
- [ ] Officer endpoints return data
- [ ] Browser DevTools Network tab shows successful requests
- [ ] No console errors in browser frontend
- [ ] No traceback errors in backend terminal

---

## 🎯 QUICK REFERENCE

| Component | URL | Port | Status Command |
|-----------|-----|------|-----------------|
| Backend | http://localhost:8000 | 8000 | `curl http://localhost:8000/health` |
| Frontend | http://localhost:5173 | 5173 | `curl http://localhost:5173` |
| API Base | http://localhost:8000 | 8000 | See health check |

---

## 📞 SUPPORT

For issues not covered here:
1. Check browser DevTools Console for errors
2. Check backend terminal for tracebacks
3. Verify both servers are running
4. Verify CORS configuration
5. Check .env files are in place
6. Restart both servers

---

Generated: 2026-05-08
System: Full Stack Integration Testing Guide
