from fastapi import FastAPI
from pydantic import BaseModel, Field
import json
import pickle
import pandas as pd
from typing import Literal, Annotated
from fastapi.responses import JSONResponse

with open("banglore_home_prices_model.pickle", "rb") as f:
    model = pickle.load(f)

with open("columns.json", "r") as f:
    data_columns = json.load(f)['data_columns']

app = FastAPI()

class HomeData(BaseModel):
    location: Annotated[Literal[tuple(data_columns)], Field(...,description="Location of the home")]
    total_sqft: Annotated[float, Field(...,gt=0, description="Total square footage")]
    bath: Annotated[int, Field(...,gt=0, description="Number of bathrooms")]
    bhk: Annotated[int, Field(...,gt=0, description="Number of bedrooms")]
    balcony: Annotated[int, Field(...,gt=0, description="Number of balconies")]

@app.post("/predict_price")
def predict_price(data: HomeData):
    input_df = pd.DataFrame([{
        'total_sqft': data.total_sqft,
        'bath': data.bath,
        'balcony': data.balcony,
        'bhk': data.bhk
    }])
    location_index = data_columns.index(data.location)
    input_df = pd.concat([input_df, pd.get_dummies([data.location], prefix='location')], axis=1)
    input_df = input_df.reindex(columns=data_columns, fill_value=0)
    predicted_price = model.predict(input_df)[0]
    return JSONResponse(status_code=200, content={"predicted_price": predicted_price})