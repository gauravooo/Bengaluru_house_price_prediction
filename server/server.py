from pathlib import Path

import json
import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "banglore_home_prices_model.pickle"
COLUMNS_PATH = BASE_DIR / "columns.json"

with MODEL_PATH.open("rb") as f:
    model = pickle.load(f)

with COLUMNS_PATH.open("r", encoding="utf-8") as f:
    data_columns = json.load(f)["data_columns"]

BASE_FEATURES = {"total_sqft", "bath", "balcony", "bhk"}
LOCATIONS = [col for col in data_columns if col not in BASE_FEATURES]

app = FastAPI(title="Bangalore House Price Prediction API")

class HomeData(BaseModel):
    location: str = Field(..., description="Location of the home")
    total_sqft: float = Field(..., gt=0, description="Total square footage")
    bath: int = Field(..., gt=0, description="Number of bathrooms")
    bhk: int = Field(..., gt=0, description="Number of bedrooms")
    balcony: int = Field(..., ge=0, description="Number of balconies")

    @validator("location")
    def validate_location(cls, value: str) -> str:
        normalized = value.strip().lower()
        candidate = next((loc for loc in LOCATIONS if loc.lower() == normalized), None)
        if not candidate:
            raise ValueError("Location must be one of the supported Bangalore locations")
        return candidate


def build_feature_vector(data: HomeData) -> pd.DataFrame:
    features = {column: 0 for column in data_columns}
    features["total_sqft"] = data.total_sqft
    features["bath"] = data.bath
    features["balcony"] = data.balcony
    features["bhk"] = data.bhk
    features[data.location] = 1
    return pd.DataFrame([features], columns=data_columns)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/locations")
def get_locations():
    return {"locations": LOCATIONS}


@app.post("/predict")
def predict_price(data: HomeData):
    try:
        input_df = build_feature_vector(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    predicted_price = model.predict(input_df)[0]
    return JSONResponse(status_code=200, content={"predicted_price": float(predicted_price)})