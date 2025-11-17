import pandas as pd
from func_utils.utils import save_tocsv

import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from dotenv import load_dotenv
import os
import mlflow

def data_coll_prod(url='../../data/prod/eCO2mix_RTE_Auvergne-Rhone-Alpes_cleaned.csv'):

    # read csv
    df_prod = pd.read_csv(url)
    data_prod = df_prod.copy()

    # formatting the date for future data merge operations
    data_prod['Time'] = pd.to_datetime(data_prod['date']+" "+data_prod['heures'])
    return data_prod


def data_coll_landsat(url ='../../data/LandSat/result_EarthExplorer_region_ARA.csv'):

    # read csv
    df_sat = pd.read_csv(url, encoding='ISO-8859-1', sep=';')
    data_sat = df_sat.copy()

    # formatting the date column "Start Time" for future data merge operations
    time1 = pd.to_datetime(data_sat['Start Time'].str[:16], format='%d/%m/%Y %H:%M', errors='coerce')
    time2 = pd.to_datetime(data_sat['Start Time'].str[:16], format='%Y-%m-%d %H:%M', errors='coerce')

    data_sat['Time'] = time1
    data_sat['Time'] = data_sat['Time'].fillna(time2)
    data_sat['Time']=data_sat['Time'].dt.round('30min') #to match the production data)
    return data_sat

def data_merge(data_prod, data_sat):
    """
    Function designed to merge the different datasets. 
    At the moment: Production data, Landsat (meta)data
    to be included: weather, solar
    """

    # group the landsat data by the time variable to aggregate the images data
    sat_columns_to_use = ['Land Cloud Cover', 'Scene Cloud Cover L1','Sun Elevation L0RA', 'Sun Azimuth L0RA']
    data_sat_grouped = data_sat.groupby('Time')[sat_columns_to_use].mean().reset_index()

    # select columns from production data
    prod_columns_to_use = ['Time', 'solaire', 'tco_solaire_(%)', 'tch_solaire_(%)']
    data_prod_limited = data_prod[prod_columns_to_use]

    merged_data = data_sat_grouped.merge(data_prod_limited, on='Time', how='inner')
    # save_tocsv(merged_data, '../../data/compiled_data/sat_only_data.csv')
    return merged_data

def preprocess(data):
    

def data_prep(merged_data):
    """
    Preprocessing of the data.
    Up to date: Production data and Landsat (meta)data / standard scaler
    to be included: weather, solar / ohe, feature engineering
    """

    y = merged_data['tch_solaire_(%)'].to_numpy() #target
    x = merged_data[['Land Cloud Cover','Sun Elevation L0RA']] #features

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

    # Preprocessing
    sc = StandardScaler()
    sc.fit(x_train)

    x_train = sc.transform(x_train)
    x_test = sc.transform(x_test)

    return x_train, x_test, y_train, y_test

def model_training(model):

    """
    Model training with experiment storage in mlflow server.
    Can be decomposed further by separating the mlflow section. 
    """

    # pour enregistrer dans MLFlow
    load_dotenv()

    os.environ["APP_URI"] = "https://renergies99-mlflow.hf.space/"
    EXPERIMENT_NAME="first_landsat_models"

    mlflow.set_tracking_uri(os.environ["APP_URI"])
    mlflow.set_experiment(EXPERIMENT_NAME)
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

    mlflow.sklearn.autolog()

    # model 1
    run_description = """
    colonnes utilisées : ['Land Cloud Cover','Sun Elevation L0RA']
    \n target = 'tch_solaire_(%)'
    """

    with mlflow.start_run(experiment_id = experiment.experiment_id, description=run_description):
        model = LinearRegression()
        model.fit(x_train, y_train)

        score = model.score(x_test, y_test)
        
        mlflow.log_metric("ScoreR2", score)
        mlflow.sklearn.log_model(model, "model")

    print('model_score_train: ', model.score(x_train,y_train))
    print('model_score_test: ', model.score(x_test,y_test))