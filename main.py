import data_processing_utilities
import data_preprocessing
import logging

logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

file_path = 'data/states_2022-06-27-20.csv.gz'
EDDF_coords = (50.033333, 8.570556)

df = data_processing_utilities.load_csv_gzip(file_path=file_path)
df_cleaned = data_processing_utilities.drop_nan_rows(df=df)

filtered_df = data_preprocessing.filter_flights(df=df_cleaned, airport_coords=EDDF_coords)

data_processing_utilities.write_kml_for_each_callsign(df=filtered_df)