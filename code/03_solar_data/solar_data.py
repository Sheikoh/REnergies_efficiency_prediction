import pandas as pd
from utils import daterange, save_tocsv
from solar_data_func import extract_date, to_boto, session_boto
from datetime import date, timedelta, datetime
from dotenv import load_dotenv
import os

def to_s3(data):
    load_dotenv()

    API_KEY_S3 = os.environ["AWS_ACCESS_KEY_ID"]
    API_SECRET_KEY_S3 = os.environ["AWS_SECRET_ACCESS_KEY"]
    print(API_KEY_S3)
    print(API_SECRET_KEY_S3)

    data.to_csv("https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/solar/raw_solar_data.csv",
                  index=False,
                  storage_options={
                      "key": API_KEY_S3,
                      "secret": API_SECRET_KEY_S3,
                      })


###Base variables
base_url = "https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/solar_geophysical_activity_summaries"
# dest_url = 
start_date = date(2025, 11, 1)
end_date = datetime.today().date()

### Update date
# stored_data = pd.read_csv("https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/solar/raw_solar_data.csv", index_col=0)
# if stored_data:
#     start_date = (pd.to_datetime(max(stored_data.index))+timedelta(days=1)).date()

### Retrieval loop between start_date and end_date
solar_data = pd.DataFrame()
for single_date in daterange(start_date, end_date):
    #print(single_date.strftime("%Y-%m-%d"))
    df_temp = extract_date(base_url, single_date, case='historic')
    print(single_date, df_temp)
    solar_data = pd.concat([solar_data, df_temp])

# solar_data = pd.concat([stored_data, solar_data])
url = "https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/solar/raw_solar_data.csv"
#to_s3(solar_data)
#storage of the data in a csv
print(solar_data.head())
bucket = session_boto()
to_boto(bucket, 'public/solar/', "raw_solar.csv", solar_data.to_csv())

# save_tocsv(solar_data, 'data/solar/raw_solar_data.csv')
# solar_data.to_csv('data/solar/raw_solar_data.csv')