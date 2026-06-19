# Bangalore House Price Predictor - Streamlit Frontend

Simple Streamlit frontend for the house price prediction model.

## Installation

```bash
pip install streamlit requests
```

## Usage

1. Start the backend server:
```bash
cd ../server
python server.py
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

Notes:
- The app includes a **Settings** sidebar where you can change the Backend API URL and enable a local fallback for locations.
- Use the **Examples** buttons in the sidebar to quickly populate common property inputs.

## Features

- Select from Bangalore locations
- Enter property details (area, BHK, bathrooms, balconies)
- Get instant price predictions
- Clean and simple interface
