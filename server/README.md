# Bangalore House Price Prediction API

A FastAPI-based machine learning API for predicting house prices in Bangalore.

## Features

- **ML Model Integration**: Uses a pre-trained scikit-learn model for price predictions
- **Input Validation**: Robust validation for location and property features
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Logging**: Built-in logging for debugging and monitoring
- **CORS Support**: Configured for client-server communication
- **API Documentation**: Interactive Swagger UI and ReDoc documentation

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and adjust settings as needed:

```bash
cp .env.example .env
```

Key configuration options:
- `LOG_LEVEL`: Set logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)

### 3. Run the Server

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the server and model are healthy.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "features_loaded": true,
  "locations_available": 229
}
```

### 2. Get Supported Locations
**GET** `/locations`

Get the list of all supported Bangalore locations.

**Response:**
```json
{
  "locations": ["Indira Nagar", "Koramangala", ...],
  "count": 229
}
```

### 3. Predict Price
**POST** `/predict`

Predict house price based on location and property features.

**Request Body:**
```json
{
  "location": "Indira Nagar",
  "total_sqft": 1000,
  "bath": 2,
  "bhk": 2,
  "balcony": 1
}
```

**Response:**
```json
{
  "predicted_price": 5500000,
  "location": "Indira Nagar",
  "unit": "INR"
}
```

## API Documentation

Once running, access interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Model Loading Issues
Ensure `banglore_home_prices_model.pickle` and `columns.json` are in the server directory. Check logs for detailed error messages.

### CORS Issues
Update `ALLOWED_ORIGINS` in `.env` to include your client's URL.

### Validation Errors
- Use the `/locations` endpoint to get valid location names
- Ensure all numeric fields are positive numbers
- Location names are case-insensitive

## Improvements Made

✅ **Error Handling**: Comprehensive error handling with graceful failure modes  
✅ **Logging**: Full logging for debugging and monitoring  
✅ **CORS Support**: Configured for frontend communication  
✅ **Configuration Management**: Environment variables for flexible deployment  
✅ **Input Validation**: Enhanced validation with helpful error messages  
✅ **API Documentation**: Improved endpoint descriptions and examples  
✅ **Startup Checks**: Verifies model and columns load successfully  
✅ **Type Hints**: Complete type annotations for better IDE support  
