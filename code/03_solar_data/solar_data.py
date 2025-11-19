import pandas as pd
from func_utils.utils import daterange, save_tocsv
from solar_data_func import extract_date
from datetime import date

###Base variables
base_url = "https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/solar_geophysical_activity_summaries"
start_date = date(2020, 1, 1)
end_date = date(2025, 10, 1)

### Retrieval loop between start_date and end_date
solar_data = pd.DataFrame()
for single_date in daterange(start_date, end_date, case='predi'):
    print(single_date.strftime("%Y-%m-%d"))
    df_temp = extract_date(base_url, single_date)
    solar_data = pd.concat([solar_data, df_temp])

#storage of the data in a csv
save_tocsv(solar_data, 'data/solar/raw_solar_data.csv')
# solar_data.to_csv('data/solar/raw_solar_data.csv')