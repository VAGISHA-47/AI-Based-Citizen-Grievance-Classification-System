#!/bin/bash
set -e

echo "Starting JanSetu AI stack..."

# Kill old processes on required ports
fuser -k 8001/tcp 2>/dev/null || true
fuser -k 8000/tcp 2>/dev/null || true
sleep 1

# Ensure ffmpeg exists for transcription
sudo apt-get install -y ffmpeg -q 2>/dev/null || true
# Ensure venv support is installed
sudo apt-get install -y python3-venv -q 2>/dev/null || true

# Start AI engine (install to user site to avoid venv issues)
cd /workspaces/AI-Based-Citizen-Grievance-Classification-System/services/ai-engine
/usr/bin/python3 -m pip install --break-system-packages --user -r requirements.txt
/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload &
echo "AI engine started on port 8001"

# Wait for AI engine health
for i in {1..20}; do
  if curl -fsS http://127.0.0.1:8001/health >/dev/null 2>&1; then
    echo "AI engine health check passed"
    break
  fi
  if [ "$i" -eq 20 ]; then
    echo "AI engine failed health check"
    exit 1
  fi
  sleep 1
done

# Start backend and point to AI engine
cd /workspaces/AI-Based-Citizen-Grievance-Classification-System/backend
/usr/bin/python3 -m pip install --break-system-packages --user -r requirements.txt
AI_ENGINE_URL=http://127.0.0.1:8001 /usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
echo "Backend started on port 8000"

echo ""
echo "Services running:"
echo "AI Engine: http://127.0.0.1:8001/health"
echo "Backend:   http://127.0.0.1:8000/health"
echo "Backend:   http://127.0.0.1:8000/health"
echo "Both services started successfully!"
