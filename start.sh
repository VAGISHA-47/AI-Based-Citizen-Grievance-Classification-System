#!/bin/bash
echo "Starting JanSetu..."

# Kill old processes
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true
sleep 1

# Update frontend env with current codespace URL
BACKEND_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
echo "VITE_API_URL=${BACKEND_URL}" > /workspaces/AI-Based-Citizen-Grievance-Classification-System/frontend/.env
echo "VITE_API_BASE_URL=${BACKEND_URL}" >> /workspaces/AI-Based-Citizen-Grievance-Classification-System/frontend/.env
echo "VITE_SUPABASE_URL=https://apxaknwrsemylziyxbpj.supabase.co" >> /workspaces/AI-Based-Citizen-Grievance-Classification-System/frontend/.env
echo "Backend URL set to: ${BACKEND_URL}"

# Start backend
cd /workspaces/AI-Based-Citizen-Grievance-Classification-System/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
echo "Backend started on port 8000"
sleep 4

# Start frontend
cd /workspaces/AI-Based-Citizen-Grievance-Classification-System/frontend
npm run dev -- --host 0.0.0.0 --port 5173 &
echo "Frontend started on port 5173"
sleep 3

# Make ports public
gh codespace ports visibility 8000:public -c $CODESPACE_NAME 2>/dev/null || true
gh codespace ports visibility 5173:public -c $CODESPACE_NAME 2>/dev/null || true

echo ""
echo "✅ JanSetu is running!"
echo "Frontend: https://${CODESPACE_NAME}-5173.app.github.dev"
echo "Backend:  https://${CODESPACE_NAME}-8000.app.github.dev"
echo "API Docs: https://${CODESPACE_NAME}-8000.app.github.dev/docs"
