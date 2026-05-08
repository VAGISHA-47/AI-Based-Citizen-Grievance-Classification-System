#!/bin/bash

# AI-Based Citizen Grievance System - Quick Start Script
# This script starts both frontend and backend servers

set -e

PROJECT_ROOT="/workspaces/AI-Based-Citizen-Grievance-Classification-System"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "================================================"
echo "AI-Based Citizen Grievance System - Quick Start"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[1/4]${NC} Checking backend dependencies..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo "Installing backend dependencies..."
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Backend venv found${NC}"
fi

echo ""
echo -e "${BLUE}[2/4]${NC} Checking frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install -q
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend node_modules found${NC}"
fi

echo ""
echo -e "${BLUE}[3/4]${NC} Backend Status..."
echo -e "${YELLOW}Run in Terminal 1:${NC}"
echo ""
echo "cd $BACKEND_DIR"
echo "export \$(cat .env | xargs)"
echo "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""

echo -e "${BLUE}[4/4]${NC} Frontend Status..."
echo -e "${YELLOW}Run in Terminal 2:${NC}"
echo ""
echo "cd $FRONTEND_DIR"
echo "npm run dev -- --host 0.0.0.0 --port 5173"
echo ""

echo "================================================"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "================================================"
echo ""
echo "After starting both servers:"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:5173"
echo "- Health check: curl http://localhost:8000/health"
echo ""
