import mlflow 
import uvicorn
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import joblib
import boto3
from dotenv import load_dotenv
import os

def session_boto():

    
    load_dotenv()

    API_KEY_S3 = os.environ["API_KEY_S3"]
    API_SECRET_KEY_S3 = os.environ["API_SECRET_KEY_S3"]

    bucket_name = "renergies99-bucket"
    

    # Liste des dossiers locaux à uploader
    folders_to_upload = ["prod", "solar", "LandSat", "openweathermap"]

    # Session Boto3
    session = boto3.Session(
        aws_access_key_id=API_KEY_S3,
        aws_secret_access_key=API_SECRET_KEY_S3,
        region_name="eu-west-3",
    )

    s3 = session.resource("s3")
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file()
    return bucket

def to_boto(bucket, predi):
    s3_prefix = "public/prediction/" 
    s3_key = "predi.csv"
    bucket.put_object(
        Body = predi,
        Key = s3_prefix
    )
