import logging
import data_processing
import data_visualization
import trackmiles

logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filemode='w'
)

file_path = 'data/states_2022-06-27-20.csv.gz'
airport='EDDC'

logging.info('start data preprocessing')
df = data_processing.load_csv_gzip(file_path=file_path)
df = data_processing.drop_nan_rows(df=df)
df = data_processing.filter_flights(df=df, airport=airport)
df = data_processing.remove_outliers(df=df)
df = data_processing.remove_outliers_geoaltitude(df=df)

df = trackmiles.calculate_remaining_track_miles(df=df)

data_visualization.animate_flight_trajectories(df=df)

#data_processing.write_animated_kml_for_each_callsign(df=df_filtered)