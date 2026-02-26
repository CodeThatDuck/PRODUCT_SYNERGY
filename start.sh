#!/bin/bash

# Project Synergy - Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting Project Synergy: Oracle to DB2 Takeout Engine"
echo "============================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating Python virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
fi

# Check if Node modules exist
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✓ All dependencies ready${NC}"
echo "============================================================"
echo ""

# Start backend in background
echo -e "${BLUE}🔧 Starting FastAPI Backend (Port 8000)...${NC}"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait a moment for backend to start
sleep 2

# Start frontend in background
echo -e "${BLUE}🎨 Starting React Frontend (Port 3001)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo "============================================================"
echo -e "${GREEN}🎉 Project Synergy is now running!${NC}"
echo "============================================================"
echo ""
echo "📍 Access Points:"
echo "   Frontend:  http://localhost:3001"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "⚠️  Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✓ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait

# Made with Bob
