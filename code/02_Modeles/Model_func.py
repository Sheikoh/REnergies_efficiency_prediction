import pandas as pd
#from func_utils.utils import save_tocsv

import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from dotenv import load_dotenv
import os
import mlflow

#--------------COLLECT DATA FUNCTIONS & ADD TARGET---------------------------------------
#---Prod
def data_coll_prod(url='../../data/prod/eCO2mix_RTE_Auvergne-Rhone-Alpes_cleaned.csv'):

    # read csv
    df_prod = pd.read_csv(url)
    data_prod = df_prod.copy()

    # formatting the date for future data merge operations
    data_prod['Time'] = pd.to_datetime(data_prod['date']+" "+data_prod['heures'])
    return data_prod

#---LandSat
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

def add_target_column_sat(data_sat, data_prod):
    """
    Function designed to add a target column (from prod_data) to the data_sat dataframe.
    Returns a dataset with selected columns (not all columns)
    Warning : the sat_data are grouped by 'Time', and the target is 'tch_solaire_(%)'
    """
    # group the landsat data by the time variable to aggregate the images data
    sat_columns_to_use = ['Land Cloud Cover', 'Scene Cloud Cover L1','Sun Elevation L0RA', 'Sun Azimuth L0RA']
    data_sat_grouped = data_sat.groupby('Time')[sat_columns_to_use].mean().reset_index()

    # select columns from production data
    prod_columns_to_use = ['Time', 'tch_solaire_(%)']
    data_prod_limited = data_prod[prod_columns_to_use]

    targeted_sat_data = data_sat_grouped.merge(data_prod_limited, on='Time', how='inner')
    # save_tocsv(merged_data, '../../data/compiled_data/sat_only_data.csv')
    return targeted_sat_data

#---OpenWeather
def data_coll_weather(url ='../../data/openweathermap/merge_openweathermap_cleaned.csv'):
    # read csv
    df_weather = pd.read_csv(url)
    data_weather = df_weather.copy()

    # formatting the date for future data merge operations
    data_weather['Time'] = pd.to_datetime(data_weather['dt'])
    return data_weather

def split_data_weather_by_city(data_weather, Cities='city'):
    """
    Split the dataframe data_weather into 5 separate dataframes (1 for each city).
    Returns a dictionary {"city" : dataframe}.
    """
    dict_dfs_cities = {}
    for city in data_weather[Cities].unique():
        key_name = f"{city}"  # name of the dataframe=city
        dict_dfs_cities[key_name] = data_weather[data_weather[Cities]==city].copy()
    return dict_dfs_cities

def concat_data_weather_by_city(dict_dfs_cities):
    """
    Concat columns of the 5 dataframes data_weather_by_city 
    Add the name of the city in the columns names
    Keep only one column 'Time'
    Returns a Dataframe
    """
    # Sort each DataFrame by 'Date' if the column exists
    sorted_dfs = {}
    for name, df in dict_dfs_cities.items():
        if 'Time' in df.columns:
            sorted_df = df.sort_values('Time').reset_index(drop=True)
            sorted_dfs[name] = sorted_df
        else:
            raise ValueError(f"The DataFrame '{name}' does not contain a 'Time' column.")
    # check if 'Time' columns are identical in each Dataframe
    time_columns = [df['Time'] for df in dict_dfs_cities.values()]
    if not all(time_columns[0].equals(tc) for tc in time_columns[1:]):
        raise ValueError("The 'Time' columns are not identical across DataFrames.")

    # Concatenate columns with a prefix for each DataFrame
    final_df = pd.concat([df.add_prefix(f"{name}_") for name, df in dict_dfs_cities.items()], axis=1)
    # keep only one columns 'Time"
    time_cols = [col for col in final_df.columns if col.endswith('Time')]
    final_df['Time'] = final_df[time_cols[0]]
    final_df = final_df.drop(columns=time_cols)
    return final_df

def merge_weather_dfs_by_city(dict_dfs_cities):
    """
    Merge (inner joint) columns of the 5 dataframes in the dict_dfs_cities
    Add the name of the city in the columns names
    Keep only one column 'Time'
    Returns a Dataframe
    """
    merged_df = None

    for city, df in dict_dfs_cities.items():
        if 'Time' not in df.columns:
            raise ValueError(f"The DataFrame for '{city}' does not contain a 'Time' column.")

        df_prefixed = df.rename(columns={col: f"{city}_{col}" for col in df.columns if col != 'Time'})

        # Merge with inner joint
        if merged_df is None:
            merged_df = df_prefixed
        else:
            merged_df = pd.merge(merged_df, df_prefixed, on='Time', how='inner')

    merged_df = merged_df.sort_values('Time').reset_index(drop=True)
    return merged_df


def add_target_column_weather(weather_data, prod_data):
    """
    Function designed to add a target column (from prod_data) to the data_weather dataframe.
    the data_weather dataframe is a merge from dataframes by cities 
        (see also split_data_weather_by_city() and  merge_weather_dfs_by_city())
    """
    # select columns from production data
    prod_columns_to_use = ['Time', 'tch_solaire_(%)']
    prod_data_limited = prod_data[prod_columns_to_use]

    targeted_weather_data = weather_data.merge(prod_data_limited, on='Time', how='left')
    return targeted_weather_data

#--------------------------------------------------------------------

def preprocess(data):
    return


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

def model_training(model, x_train, x_test, y_train, y_test):

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