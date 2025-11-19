#----IMPORT LIBRAIRIES----
import pandas as pd
import Model_func as mf


#---VARIABLES----
weather_data_path = 'https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/openweathermap/merge_openweathermap_cleaned.csv'
solar_data_path = 'https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/solar/raw_solar_data.csv'
landsat_data_path = 'https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/LandSat/result_EarthExplorer_region_ARA.csv'

#--- DATA PREP ---
# Data prep = data collect + merge the 3 datasets

collected_weather_data = mf.data_collection_weather(weather_data_path) # collect data and format columns per city
collected_solar_data = mf.data_coll_solar(solar_data_path)
collected_landsat_data = mf.data_coll_landsat(landsat_data_path)


merged_data = mf.merge_weather_solar_landsat_data(collected_weather_data, collected_solar_data, collected_landsat_data)

