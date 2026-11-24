#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null || python -m spacy download en_core_web_sm || true
if [ ! -f .env ]; then cp .env.example .env; fi
python -m uvicorn app.main:app --reload &
SERVER_PID=$!
sleep 2
python -c "import webbrowser; webbrowser.open('http://localhost:8000')"
wait "$SERVER_PID"
