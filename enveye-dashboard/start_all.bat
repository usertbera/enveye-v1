@echo off

REM Start Backend
cd enveye-backend
pip install -r requirements.txt
start cmd /k "uvicorn enveye_backend:app --host 0.0.0.0 --port 8000 --reload"

REM Start Frontend
cd ../enveye-frontend
start cmd /k "npm install && npm run build && npm run preview -- --port 5173"
