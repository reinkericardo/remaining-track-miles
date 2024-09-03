import data_processing_utilities
import data_preprocessing
import data_visualization
import logging

logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

file_path = 'data/states_2022-06-27-20.csv.gz'
EDDF_coords = (50.033333, 8.570556)
EDVE_coords = (52.3165, 10.5594)
EDDH_coords = (53.63375, 9.98530)

df = data_processing_utilities.load_csv_gzip(file_path=file_path)

df = data_preprocessing.drop_nan_rows(df=df)
df = data_preprocessing.filter_flights(df=df, airport_coords=EDDF_coords)
df = data_preprocessing.remove_outliers(df=df)
df = data_preprocessing.remove_outliers_geoaltitude(df=df)


data_visualization.visualize_flight_trajectory(df=df)

#data_processing_utilities.write_animated_kml_for_each_callsign(df=df_filtered)