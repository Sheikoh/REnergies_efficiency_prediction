import pandas as pd
from utils import daterange, save_tocsv
from solar_data_func import extract_date, to_boto, session_boto, to_s3
from datetime import date, timedelta, datetime

###Base variables
base_url = "https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/solar_geophysical_activity_summaries"
# dest_url = 
start_date = date(2025, 10, 1)
end_date = datetime.today().date()

### Update date
# stored_data = pd.read_csv("https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/solar/raw_solar_data.csv", index_col=0)
# if stored_data:
#     start_date = (pd.to_datetime(max(stored_data.index))+timedelta(days=1)).date()

### Retrieval loop between start_date and end_date
solar_data = pd.DataFrame()
for single_date in daterange(start_date, end_date):
    print(single_date.strftime("%Y-%m-%d"))
    df_temp = extract_date(base_url, single_date, case='predi')
    solar_data = pd.concat([solar_data, df_temp])

# solar_data = pd.concat([stored_data, solar_data])
url = "https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/solar/raw_solar_data.csv"
to_s3(solar_data)
#storage of the data in a csv
# bucket = session_boto()
# to_boto(bucket, 'data/solar/', "raw_solar.csv", solar_data)

# save_tocsv(solar_data, 'data/solar/raw_solar_data.csv')
# solar_data.to_csv('data/solar/raw_solar_data.csv')