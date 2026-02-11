#!/bin/bash
# UniControl Backend - Run Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  UniControl Backend Server${NC}"
echo -e "${GREEN}================================${NC}"

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python is not installed!${NC}"
    exit 1
fi

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Copying from .env.example...${NC}"
    cp ../.env.example .env 2>/dev/null || echo -e "${RED}No .env.example found${NC}"
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
alembic upgrade head

# Run server
echo -e "${GREEN}Starting server...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
