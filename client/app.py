import streamlit as st
import requests
import json
from pathlib import Path
import os

# Page configuration
st.set_page_config(
    page_title="Bangalore House Price Predictor",
    page_icon="🏠",
    layout="wide"
)

# API Configuration
API_URL = "http://localhost:8000"

# Title
st.title("🏠 Bangalore House Price Predictor")
st.markdown("---")

# Small about / instructions
with st.expander("About this app", expanded=False):
    st.write(
        "Simple Streamlit UI for predicting Bangalore house prices. Choose a location, set property details, and click Predict."
    )

# Sidebar: settings and examples
st.sidebar.title("Settings")
api_url = st.sidebar.text_input("Backend API URL", API_URL)
use_local_fallback = st.sidebar.checkbox("Use local locations fallback", value=True)
st.sidebar.markdown("---")
st.sidebar.subheader("Examples")
if "location" not in st.session_state:
    st.session_state.location = None
if "bhk" not in st.session_state:
    st.session_state.bhk = 2
if "total_sqft" not in st.session_state:
    st.session_state.total_sqft = 1000.0
if "bath" not in st.session_state:
    st.session_state.bath = 2
if "balcony" not in st.session_state:
    st.session_state.balcony = 1

if st.sidebar.button("Example: 2BHK, 1000 sqft"):
    st.session_state.bhk = 2
    st.session_state.total_sqft = 1000.0
    st.session_state.bath = 2
    st.session_state.balcony = 1

if st.sidebar.button("Example: 4BHK, 2000 sqft"):
    st.session_state.bhk = 4
    st.session_state.total_sqft = 2000.0
    st.session_state.bath = 3
    st.session_state.balcony = 2

# Load locations (try API first, then fallback to local columns.json)
@st.cache_data
def load_locations(api_url, allow_local=True):
    # Try backend
    try:
        response = requests.get(f"{api_url}/locations", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return sorted(data.get("locations", []))
    except Exception:
        pass

    # Fallback to local file
    if allow_local:
        try:
            base = Path(__file__).resolve().parents[1]
            columns_file = base / "server" / "columns.json"
            if columns_file.exists():
                with open(columns_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cols = data.get("data_columns", [])
                    # data_columns includes numeric cols at start; filter string locations
                    locations = [c for c in cols if isinstance(c, str) and not c.replace('.', '', 1).isdigit() and c.islower()]
                    # If heuristic fails, try taking items after first 4 columns
                    if not locations and len(cols) > 4:
                        locations = cols[4:]
                    return sorted(locations)
        except Exception:
            pass

    return []

# Use defaults; allow overriding via sidebar
locations = load_locations(api_url, allow_local=use_local_fallback)

if not locations:
    st.error("❌ Cannot find locations (backend may be down and no local fallback available)")
    st.info("Start the backend in ../server: python server.py or enable local fallback")
else:
    # Form
    with st.form("prediction_form"):
        st.subheader("Enter Property Details")

        col1, col2 = st.columns(2)

        with col1:
            # add a clear placeholder option so users must pick a real location
            location_options = ["Select a location"] + locations
            location = st.selectbox("Location", location_options, index=0, key="location")
            bhk = st.number_input("BHK", min_value=1, max_value=10, value=st.session_state.bhk, key="bhk")
            balcony = st.number_input("Balconies", min_value=0, max_value=10, value=st.session_state.balcony, key="balcony")

        with col2:
            total_sqft = st.number_input("Total Area (sq ft)", min_value=100.0, value=st.session_state.total_sqft, step=50.0, key="total_sqft")
            bath = st.number_input("Bathrooms", min_value=1, max_value=10, value=st.session_state.bath, key="bath")

        # quick inline validation hints
        if total_sqft < bhk * 200:
            st.warning("Entered area is small for the chosen BHK — please confirm the value.")

        submitted = st.form_submit_button("🔮 Predict Price", use_container_width=True)
    
    # Handle prediction
    if submitted:
        # Guard: ensure a real location was selected
        if location == "Select a location":
            st.error("Please select a valid location before requesting a prediction.")
        else:
            try:
                with st.spinner("Calculating..."):
                    response = requests.post(
                        f"{api_url}/predict",
                        json={
                            "location": location,
                            "total_sqft": total_sqft,
                            "bhk": int(bhk),
                            "bath": int(bath),
                            "balcony": int(balcony)
                        },
                        timeout=10
                    )

                if response.status_code == 200:
                    result = response.json()
                    price = result.get('predicted_price')

                    if price is None:
                        st.error("✅ Prediction returned no price. Unexpected response format.")
                    else:
                        st.success("✅ Prediction Complete!")
                        st.markdown("---")

                        # Display result and additional metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Predicted Price", f"₹ {price:,.0f}")
                        with col2:
                            st.metric("Location", location)

                        # additional metric: price per sqft
                        try:
                            ppsq = price / float(total_sqft)
                            st.metric("Price / sq ft", f"₹ {ppsq:,.0f}")
                        except Exception:
                            pass

                        st.markdown("---")
                        st.subheader("Property Summary")

                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Area", f"{total_sqft:,.0f} sq ft")
                        col2.metric("BHK", int(bhk))
                        col3.metric("Bathrooms", int(bath))
                        col4.metric("Balconies", int(balcony))
                else:
                    # try to show useful error details
                    try:
                        err = response.json().get("detail", response.text)
                    except Exception:
                        err = response.text
                    st.error(f"❌ Prediction failed: {err}")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error: {str(e)}")
