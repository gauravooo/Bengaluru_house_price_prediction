import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Bangalore House Price Predictor",
    page_icon="🏠",
    layout="centered"
)

# API Configuration
API_URL = "http://localhost:8000"

# Title
st.title("🏠 Bangalore House Price Predictor")
st.markdown("---")

# Load locations
@st.cache_data
def load_locations():
    try:
        response = requests.get(f"{API_URL}/locations", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return sorted(data.get("locations", []))
    except:
        pass
    return []

locations = load_locations()

if not locations:
    st.error("❌ Cannot connect to backend API at " + API_URL)
    st.info("Make sure the server is running: `python server.py`")
else:
    # Form
    with st.form("prediction_form"):
        st.subheader("Enter Property Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            location = st.selectbox("Location", locations)
            bhk = st.number_input("BHK", min_value=1, max_value=10, value=2)
            balcony = st.number_input("Balconies", min_value=0, max_value=10, value=1)
        
        with col2:
            total_sqft = st.number_input("Total Area (sq ft)", min_value=100.0, value=1000.0, step=100.0)
            bath = st.number_input("Bathrooms", min_value=1, max_value=10, value=2)
        
        submitted = st.form_submit_button("🔮 Predict Price", use_container_width=True)
    
    # Handle prediction
    if submitted:
        try:
            with st.spinner("Calculating..."):
                response = requests.post(
                    f"{API_URL}/predict",
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
                price = result['predicted_price']
                
                st.success("✅ Prediction Complete!")
                st.markdown("---")
                
                # Display result
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Predicted Price", f"₹ {price:,.0f}")
                with col2:
                    st.metric("Location", location)
                
                st.markdown("---")
                st.subheader("Property Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Area", f"{total_sqft:,.0f} sq ft")
                col2.metric("BHK", int(bhk))
                col3.metric("Bathrooms", int(bath))
                col4.metric("Balconies", int(balcony))
            else:
                st.error("❌ Prediction failed: " + response.json().get("detail", "Unknown error"))
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error: {str(e)}")
