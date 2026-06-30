"""
NovaFlix — Entry Point
======================
This project has been migrated from Streamlit to a React + FastAPI stack.

  OLD (Streamlit):  python -m streamlit run main.py          ← archived as main_streamlit_backup.py
  NEW (FastAPI):    python -m uvicorn main:application --reload --port 8000
  NEW (Frontend):   cd ../frontend && npm run dev

Run the new app from the project root:
  Terminal 1:  cd backend  && python -m uvicorn main:application --reload --port 8000
  Terminal 2:  cd frontend && npm run dev
  Browser:     http://localhost:5173

Or use the one-click scripts in the parent folder:
  start-backend.bat
  start-frontend.bat
"""

print(__doc__)