import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

import pvlib

import mlflow
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

import Model_func as mf
import boto3

from dotenv import load_dotenv
import os

#----VARIABLES------
data_weather_path = 'https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/openweathermap/merge_openweathermap_cleaned.csv'
data_prod_path = 'https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/prod/eCO2mix_RTE_Auvergne-Rhone-Alpes_cleaned.csv'
features = ['temp', 'pressure', 'humidity', 'clouds'] #add sunset-sunrise
target = ['tch_solaire_(%)']


#----DATA COLLECTION--------------
collected_weather_data = mf.data_collection_weather(data_weather_path)
collected_prod_data = mf.data_collection_prod(data_prod_path)

#---DATA PREP FOR ML----
prep_data = mf.data_prep_for_ML(collected_weather_data, features)

#-----ADD TARGET------
targeted_weather_data = mf.add_target(collected_weather_data, collected_prod_data)

#------Machine Learning------
#split
#fit
# pipeline pour le tracker dans MLflow