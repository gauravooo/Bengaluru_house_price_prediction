# Complete Setup Guide

Follow these steps to run both backend and frontend.

## Prerequisites
- Python 3.8 or higher
- Virtual environment already created (.venv folder exists)

---

## Step 1: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

You should see `(.venv)` at the beginning of your terminal prompt.

---

## Step 2: Install Backend Dependencies

From the project root directory:

```bash
pip install -r server/requirements.txt
```

This installs:
- FastAPI
- Uvicorn
- Pandas
- Scikit-learn
- Pydantic

---

## Step 3: Verify Model Files Exist

Check that these files exist in the `server/` folder:
- `banglore_home_prices_model.pickle` (the ML model)
- `columns.json` (feature columns)

If missing, train/generate them first.

---

## Step 4: Start the Backend Server

In **Terminal 1**, run:

```bash
cd server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Keep this terminal open and running!

**Note:** The `--reload` flag enables auto-restart when you make code changes.

---

## Step 5: Install Frontend Dependencies

In **Terminal 2** (while backend is running), from the project root:

```bash
pip install streamlit requests
```

---

## Step 6: Run the Frontend

In **Terminal 2**, run:

```bash
cd client
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

Streamlit will automatically open in your browser at `http://localhost:8501`

---

## Step 7: Use the App

1. Select a location from the dropdown
2. Enter:
   - Total Area (sq ft)
   - BHK (number of bedrooms/halls/kitchens)
   - Bathrooms
   - Balconies
3. Click "Predict Price"
4. View the predicted house price

---

## Troubleshooting

### Backend Server Issues

**Error: "Module not found"**
- Make sure virtual environment is activated: `(.venv)` should show in prompt
- Reinstall dependencies: `pip install -r server/requirements.txt`

**Error: "Model file not found"**
- Check that `banglore_home_prices_model.pickle` exists in `server/` folder
- Check that `columns.json` exists in `server/` folder

**Port already in use**
- Backend is already running on another terminal
- Or kill the process: `netstat -ano | findstr :8000` (Windows)

### Frontend Issues

**Error: "Cannot connect to API"**
- Make sure backend server is running first (Step 4)
- Check that backend is running on `http://localhost:8000`
- Try restarting both terminals

**Streamlit not found**
- Make sure virtual environment is activated
- Reinstall: `pip install streamlit requests`

**Streamlit opens but form doesn't work**
- Check browser console for errors (F12)
- Make sure backend server is still running

---

## Quick Summary

**Terminal 1 - Backend:**
```powershell
.\.venv\Scripts\Activate.ps1
cd server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
.\.venv\Scripts\Activate.ps1
pip install streamlit requests
cd client
streamlit run app.py
```

Keep both running!
