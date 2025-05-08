#!/bin/bash

# Function to start backend and frontend in a new terminal window
start_backend() {
    cd enveye-backend || exit
    pip install -r requirements.txt
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS uses osascript (AppleScript) to open a new Terminal window
        osascript -e 'tell application "Terminal" to do script "uvicorn enveye_backend:app --host 0.0.0.0 --port 8000 --reload"'
    else
        # Linux uses gnome-terminal to open a new terminal window
        gnome-terminal -- bash -c "uvicorn enveye_backend:app --host 0.0.0.0 --port 8000 --reload; exec bash"
    fi
}

start_frontend() {
    cd ../enveye-frontend || exit
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS uses osascript (AppleScript) to open a new Terminal window
        osascript -e 'tell application "Terminal" to do script "npm install && npm run build && npm run preview -- --port 5173"'
    else
        # Linux uses gnome-terminal to open a new terminal window
        gnome-terminal -- bash -c "npm install && npm run build && npm run preview -- --port 5173; exec bash"
    fi
}

# Start Backend
start_backend

# Start Frontend
start_frontend
