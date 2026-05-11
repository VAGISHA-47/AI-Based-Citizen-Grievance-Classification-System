#!/bin/bash
echo "Starting JanSetu..."

# Kill old processes
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true
sleep 1

# Install AI dependencies (needed after every Codespace restart)
echo "Installing AI dependencies..."
pip install openai-whisper -q 2>/dev/null || true
sudo apt-get install -y ffmpeg -q 2>/dev/null || true
echo "AI dependencies ready"

# Update frontend env
BACKEND_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
echo "VITE_API_URL=${BACKEND_URL}" > /workspaces/AI-Based-Citizen-Grievance-Classification-System/frontend/.env
echo "VITE_SUPABASE_URL=https://apxaknwrsemylziyxbpj.supabase.co" >> /workspaces/AI-Based-Citizen-Grievance-Classification-System/frontend/.env
echo "Backend URL: ${BACKEND_URL}"

# Start backend
cd /workspaces/AI-Based-Citizen-Grievance-Classification-System/backend
HF_HUB_DISABLE_IMPLICIT_TOKEN=1 uvicorn app.main:app \
	--reload --host 0.0.0.0 --port 8000 &
echo "Backend started"
sleep 5

# Start frontend
cd /workspaces/AI-Based-Citizen-Grievance-Classification-System/frontend
npm run dev -- --port 5173 &
echo "Frontend started"
sleep 3

# Make ports public
gh codespace ports visibility 8000:public \
	-c $CODESPACE_NAME 2>/dev/null || true
gh codespace ports visibility 5173:public \
	-c $CODESPACE_NAME 2>/dev/null || true

echo ""
echo "JanSetu is running!"
echo "Frontend: https://${CODESPACE_NAME}-5173.app.github.dev"
echo "Backend:  https://${CODESPACE_NAME}-8000.app.github.dev"
echo "Docs:     https://${CODESPACE_NAME}-8000.app.github.dev/docs"
