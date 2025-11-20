import mlflow 
import uvicorn
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import joblib
import app_func as af
import boto3
from dotenv import load_dotenv
import os
import rte
import openweathermap as owm
# data = pd.read_excel("ibm_hr_attrition.xlsx", index_col=0)
# model = joblib.load("model_ibm")

bucket = af.session_boto()

# Set tracking URI to your Hugging Face application
mlflow.set_tracking_uri("https://renergies99-mlflow.hf.space/")

# Set your variables for your environment
EXPERIMENT_NAME="first_weather_models"
# Set experiment's info 
mlflow.set_experiment(EXPERIMENT_NAME)

# Get our experiment info
experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
# mlflow.sklearn.autolog()

description = """

Description to be redone
Welcome to Jedha demo API. This app is made for you to understand how FastAPI works! Try it out 🕹️

## Introduction Endpoints

Here are two endpoints you can try:
* `/`: **GET** request that display a simple default message.
* `/greetings`: **GET** request that display a "hello message"

## Blog Endpoints

Imagine this API deals with blog articles. With the following endpoints, you can retrieve and create blog posts 
* `/blog-articles/{blog_id}`: **GET** request that retrieve a blog article given a `blog_id` as `int`.
* `/create-blog-article`: POST request that creates a new article

## Machine Learning

This is a Machine Learning endpoint that predict salary given some years of experience. Here is the endpoint:

* `/predict` that accepts `floats`


Check out documentation below 👇 for more information on each endpoint. 
"""

tags_metadata = [
    {
        "name": "Basic Endpoints",
        "description": "Simple endpoints to observe the data!",
    },

    {
        "name": "tbd Endpoints",
        "description": "More complex endpoints that deals with actual data with **GET** and **POST** requests."
    },

    {
        "name": "Machine Learning",
        "description": "Prediction Endpoint."
    }
]

app = FastAPI(
    title="🪐 Jedha Demo API",
    description=description,
    version="0.1",
    contact={
        "name": "Jedha",
        "url": "https://jedha.co",
    },
    openapi_tags=tags_metadata
)

class BlogArticles(BaseModel):
    title: str
    content: str
    author: str = "Anonymous Author"

class PredictionFeatures(BaseModel):
    YearsExperience: float



@app.get("/", tags=["Introduction Endpoints"])
async def index():
    """
    Simply returns a welcome message!
    """
    message = "Hello world! This `/` is the most simple and default endpoint. If you want to learn more, check out documentation of the api at `/docs`"
    return message


@app.post("/predict", tags=["Machine Learning"])
async def predict(predictionFeatures: dict[str, Union[str, float]]):
    """
    Prediction of the Renewable Energies based on the input data 
    """

    # Set your variables for your environment
    EXPERIMENT_NAME="all_columns_models"
    # Set experiment's info 
    mlflow.set_experiment(EXPERIMENT_NAME)

    print(predictionFeatures)
    # Read data 
    data = pd.DataFrame([predictionFeatures])

    # Log model from mlflow 
    logged_model = 'runs:/c9de1740e84e491ba8c15eafb16a8fa0/pipeline_model'

    # # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(data)
    artifact_uri = mlflow.get_run(logged_model).info.artifact_uri
    errors = mlflow.artifacts.load_dict(artifact_uri + "/error.json")
    error = get_error()
    print(prediction)

    # Format response
    response = {"prediction": prediction.tolist()[0],
                "error": error}
    hist_df = pd.read_csv('https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/prediction/predi.csv')
    resp_df = pd.DataFrame(response, index=list(range(len(response))))
    all_predi = pd.concat([resp_df, hist_df])
    resp_toboto = all_predi.to_csv()
    af.to_boto(bucket, resp_toboto)
    return response

@app.post("/predict_live", tags=["Machine Learning"])
async def predict(file: UploadFile= File(...)):
    """
    Prediction of solar panel output based on weather and solar data 
    """
    
    data = pd.read_csv(file.file)
    time = data['time']
    data = data.drop('time', axis=1)
    print(data)
    # Read data 
    # data_employee = pd.DataFrame([prediction_data])

    # Log model from mlflow 
    logged_model = 'runs:/5af5104e94fe40d2948ca5471e2e7d72/pipeline_model'

    # # Load model as a PyFuncModel.
    # loaded_model = mlflow.pyfunc.load_model(logged_model)

    # If you want to load model persisted locally
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    prediction = loaded_model.predict(data)

    # Format response
    response = {"prediction": prediction.tolist()}
    return response

@app.get("/load_rte_data", tags=["RTE"])
async def load_rte_data():
    """
    Load RTE data
    """
    if not rte.is_rte_data_already_downloaded():
        try:
            previous_data = rte.get_previous_rte_data()
            en_cours_data = rte.en_cours_rte_data()

            previous_data.append(en_cours_data)

            df = pd.concat(previous_data, ignore_index=True)

            rte.rte_df_to_csv(df)
            
            return "RTE data successfully uploaded"

        except Exception as e:
            return e
    
    return "RTE data is already downloaded today"

@app.get("/rte_last_download", tags=["RTE"])
async def rte_last_download():
    """
    Get the date of the last downloaded version of RTE data
    """
    return rte.get_rte_last_download()

@app.get("/load_openweathermap_forecasts", tags=["Openweathermap"])
async def load_openweathermap_forecasts():
    """
    Load Openweathermap data for forecasting
    """
    if not owm.is_openweathermap_data_already_downloaded():
        try:
            cities_coord = owm.get_city_data()
            owm.load_openweathermap_data(cities_coord)
            
            return "Openweathermap data successfully uploaded"

        except Exception as e:
            return e
    
    return "Openweathermap data is already downloaded today"

@app.get("/openweathermap_last_download", tags=["Openweathermap"])
async def openweathermap_last_download():
    """
    Get the date of the last downloaded version of Openweathermap data
    """
    return owm.get_openweathermap_last_download()