import json
import mlflow 
import uvicorn
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import os

description = """
Welcome to Getaround API ! 🚗

## Machine Learning

This is a Machine Learning endpoint that predict suggested location price given some cars' info. Here is the endpoint:

* `/predict` that accepts a dictionaries. You can see an exemple below 👇. 

"""

tags_metadata = [
    {
        "name": "Introduction Endpoints",
        "description": "Simple endpoints to try out!",
    },

    {
        "name": "Machine Learning",
        "description": "Prediction Endpoint."
    }
]

app = FastAPI(
    title="Getaround API : recommended rent prices ",
    description=description,
    version="0.1",
    contact={
        "name": "MarieA",
      #  "url": "tbc",
    },
    openapi_tags=tags_metadata
)

class PredictionFeatures(BaseModel):
    model_key: str = "Citroën"
    mileage: int = 13929
    engine_power: int = 317
    fuel: str = "petrol"
    paint_color: str = "grey"
    car_type: str = "convertible"
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = False
    has_speed_regulator: bool = True
    winter_tires: bool = True

@app.get("/", tags=["Introduction Endpoints"])
async def index():
    """
    Renvoie simplement un message de bienvenue !
    """
    message = "Bonjour! Ce `/` est le point de terminaison le plus simple et par défaut. Si vous voulez en savoir plus, consultez la documentation de l'API sur `/docs`"
    return message

@app.post("/predict", tags=["Machine Learning"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Suggestion of location price for given car infos! 
    """
    # Read data 
    Cars_info = pd.DataFrame(dict(predictionFeatures), index=[0])

     # Log model from mlflow 
    logged_model = 'runs:/66041b67ae354185846b5c361e24f56c/car-price-path'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    ## If you want to load model persisted locally
    #loaded_model = joblib.load('model.joblib')

    prediction = loaded_model.predict(Cars_info)

    # Format response
    response = {"Suggested price in euro": str(round(prediction.tolist()[0],2))} 
    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)