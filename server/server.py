from pathlib import Path
import json
import pickle
import logging
import os
from typing import List
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Pydantic v2 uses field_validator; v1 uses validator.
try:
    from pydantic import BaseModel, Field, field_validator as validator
except ImportError:
    from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "banglore_home_prices_model.pickle"
COLUMNS_PATH = BASE_DIR / "columns.json"

# Initialize model and columns
model = None
data_columns = None
BASE_FEATURES = {"total_sqft", "bath", "balcony", "bhk"}
LOCATIONS = []


def load_model_and_columns():
    """Load the machine learning model and feature columns from disk."""
    global model, data_columns, LOCATIONS
    
    try:
        logger.info(f"Loading model from {MODEL_PATH}")
        with MODEL_PATH.open("rb") as f:
            model = pickle.load(f)
        logger.info("Model loaded successfully")
    except FileNotFoundError:
        logger.error(f"Model file not found at {MODEL_PATH}")
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise RuntimeError(f"Failed to load model: {e}")
    
    try:
        logger.info(f"Loading columns from {COLUMNS_PATH}")
        with COLUMNS_PATH.open("r", encoding="utf-8") as f:
            data_columns = json.load(f)["data_columns"]
        LOCATIONS = [col for col in data_columns if col not in BASE_FEATURES]
        logger.info(f"Loaded {len(data_columns)} total features, {len(LOCATIONS)} locations")
    except FileNotFoundError:
        logger.error(f"Columns file not found at {COLUMNS_PATH}")
        raise RuntimeError(f"Columns file not found: {COLUMNS_PATH}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in columns file: {e}")
        raise RuntimeError(f"Invalid JSON format in columns file: {e}")
    except Exception as e:
        logger.error(f"Error loading columns: {e}")
        raise RuntimeError(f"Failed to load columns: {e}")


# Load model on startup
try:
    load_model_and_columns()
except RuntimeError as e:
    logger.critical(f"Failed to initialize server: {e}")
    raise

app = FastAPI(
    title="Bangalore House Price Prediction API",
    description="ML API for predicting house prices in Bangalore based on location, size, and amenities",
    version="1.0.0"
)

# Add CORS middleware for client communication
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HomeData(BaseModel):
    """Model for house price prediction input."""
    location: str = Field(..., description="Location of the home in Bangalore")
    total_sqft: float = Field(..., gt=0, description="Total square footage of the property")
    bath: int = Field(..., gt=0, description="Number of bathrooms")
    bhk: int = Field(..., gt=0, description="Number of bedrooms/halls/kitchens")
    balcony: int = Field(..., ge=0, description="Number of balconies")

    @validator("location")
    def validate_location(cls, value: str) -> str:
        """Validate that location is a supported Bangalore location."""
        if not value or not isinstance(value, str):
            raise ValueError("Location must be a non-empty string")
        
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Location cannot be empty or whitespace-only")
        
        candidate = next((loc for loc in LOCATIONS if loc.lower() == normalized), None)
        if not candidate:
            raise ValueError(
                f"Location '{value}' is not supported. "
                f"Please choose from available locations: {', '.join(LOCATIONS[:5])}... "
                f"(Total {len(LOCATIONS)} locations available)"
            )
        return candidate
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "location": "Indira Nagar",
                "total_sqft": 1000,
                "bath": 2,
                "bhk": 2,
                "balcony": 1
            }
        }


def build_feature_vector(data: HomeData) -> pd.DataFrame:
    """Build feature vector for model prediction."""
    try:
        features = {column: 0 for column in data_columns}
        features["total_sqft"] = data.total_sqft
        features["bath"] = data.bath
        features["balcony"] = data.balcony
        features["bhk"] = data.bhk
        features[data.location] = 1
        return pd.DataFrame([features], columns=data_columns)
    except KeyError as e:
        logger.error(f"Feature column missing: {e}")
        raise ValueError(f"Feature configuration error: {e}")
    except Exception as e:
        logger.error(f"Error building feature vector: {e}")
        raise ValueError(f"Failed to process input data: {e}")


@app.get("/health", tags=["Health"])
def health_check():
    """Check if the server and model are healthy and ready."""
    try:
        if model is None or data_columns is None:
            logger.error("Model or columns not loaded")
            return JSONResponse(
                status_code=503,
                content={"status": "error", "message": "Server not fully initialized"}
            )
        logger.debug("Health check passed")
        return {
            "status": "ok",
            "model_loaded": True,
            "features_loaded": True,
            "locations_available": len(LOCATIONS)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": str(e)}
        )


@app.get("/locations", tags=["Data"])
def get_locations() -> dict:
    """Get list of all supported Bangalore locations."""
    try:
        if not LOCATIONS:
            logger.warning("No locations available")
            raise HTTPException(status_code=503, detail="Locations data not loaded")
        logger.debug(f"Returning {len(LOCATIONS)} locations")
        return {"locations": sorted(LOCATIONS), "count": len(LOCATIONS)}
    except Exception as e:
        logger.error(f"Error retrieving locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve locations")


@app.post("/predict", tags=["Prediction"])
def predict_price(data: HomeData) -> dict:
    """
    Predict the house price based on location and property details.
    
    Returns the predicted price in Indian Rupees (INR).
    """
    try:
        if model is None:
            logger.error("Model not loaded for prediction")
            raise HTTPException(status_code=503, detail="Model not available")
        
        logger.info(f"Processing prediction request for {data.location}")
        input_df = build_feature_vector(data)
        
        predicted_price = model.predict(input_df)[0]
        
        # Validate prediction
        if predicted_price <= 0:
            logger.warning(f"Unusual prediction: {predicted_price}")
        
        logger.info(f"Prediction successful: {predicted_price} for {data.location}")
        return {
            "predicted_price": float(predicted_price),
            "location": data.location,
            "unit": "INR"
        }
    except ValueError as e:
        logger.warning(f"Validation error in prediction: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to make prediction")