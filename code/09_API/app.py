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
    EXPERIMENT_NAME="first_weather_models"
    # Set experiment's info 
    mlflow.set_experiment(EXPERIMENT_NAME)

    print(predictionFeatures)
    # Read data 
    data_employee = pd.DataFrame([predictionFeatures])
    print('good_df')

    # Log model from mlflow 
    logged_model = 'runs:/d81138d3368d4c048bafd9c7fefd70d5/model'
    # logged_model = "s3://renergies99-mlflow/4/d81138d3368d4c048bafd9c7fefd70d5/artifacts/model"
    print(logged_model)


    # # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # If you want to load model persisted locally
    # loaded_model = joblib.load('model_ibm')

    prediction = loaded_model.predict(data_employee)
    print(prediction)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    hist_df = pd.read_csv('https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/prediction/predi.csv')
    resp_df = pd.DataFrame(response, index=list(range(len(response))))
    all_predi = pd.concat([resp_df, hist_df])
    resp_toboto = all_predi.to_csv()
    af.to_boto(bucket, resp_toboto)
    return response

@app.post("/predict_live", tags=["Machine Learning"])
async def predict(file: UploadFile= File(...)):
    """
    Prediction of attrition for an employee! 
    """
    
    data_employees = pd.read_csv(file.file)
    print(data_employees)
    # Read data 
    # data_employee = pd.DataFrame([prediction_data])

    # Log model from mlflow 
    # logged_model = 'runs:/c09d09ef14e546b08f2f339d2c966da6/salary_estimator'

    # # Load model as a PyFuncModel.
    # loaded_model = mlflow.pyfunc.load_model(logged_model)

    # If you want to load model persisted locally
    loaded_model = joblib.load('model_ibm')

    prediction = loaded_model.predict(data_employees)

    # Format response
    response = {"prediction": prediction.tolist()}
    return response