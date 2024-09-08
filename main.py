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

waypoints_file_path = 'data/AIP/2 AIP Database/ED_Waypoints_2024-09-05_2024-09-05_snapshot.csv'
adsb_data_file_path = 'data/ADS-B/states_2022-06-27-20.csv.gz'
airport_ICAO_code = 'EDDS'
show_animation = True

logging.info('start data preprocessing')
waypoints_data = data_processing.load_csv(file_path=waypoints_file_path)

adsb_data = data_processing.load_csv(file_path=adsb_data_file_path, compression='gzip')
adsb_data = data_processing.drop_nan_rows(df=adsb_data)
adsb_data = data_processing.filter_flights(df=adsb_data, airport_ICAO_code=airport_ICAO_code)
adsb_data = data_processing.remove_outliers(df=adsb_data)
adsb_data = data_processing.remove_outliers_geoaltitude(df=adsb_data)

adsb_data = trackmiles.calculate_remaining_track_miles(df=adsb_data)

data_visualization.visualize(adsb_data=adsb_data, waypoints_data=waypoints_data, airport_ICAO_code=airport_ICAO_code,
                             show_animation=show_animation)

data_processing.write_kml_for_each_callsign(df=adsb_data, animate=show_animation)