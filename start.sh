#!/bin/bash
echo "Starting JanSetu..."
BASE=/workspaces/JANSETU/JANSETU

fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true
sleep 1

pip install openai-whisper -q 2>/dev/null || true
sudo apt-get install -y ffmpeg -q 2>/dev/null || true

echo "VITE_API_BASE_URL=" > $BASE/frontend/.env
echo "VITE_SUPABASE_URL=https://apxaknwrsemylziyxbpj.supabase.co" >> $BASE/frontend/.env

cd $BASE/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
sleep 5

cd $BASE/frontend
npm run dev -- --port 5173 &
sleep 3

gh codespace ports visibility 8000:public -c $CODESPACE_NAME 2>/dev/null || true
gh codespace ports visibility 5173:public -c $CODESPACE_NAME 2>/dev/null || true

echo ""
echo "JanSetu is running!"
echo "Frontend: https://${CODESPACE_NAME}-5173.app.github.dev"
echo "Backend:  https://${CODESPACE_NAME}-8000.app.github.dev"
