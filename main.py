import logging
import data_processing
import data_visualization
import trackmiles
import plotly.graph_objects as go

logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filemode='w'
)

waypoints_file_path = 'data/ED_Waypoints_2024-09-05_2024-09-05_snapshot.csv'
adsb_data_file_path = 'data/states_2022-06-27-20.csv.gz'
airport_ICAO_code = 'EDDF'

logging.info('start data preprocessing')
waypoints_data = data_processing.load_csv(file_path=waypoints_file_path)
adsb_data = data_processing.load_csv(file_path=adsb_data_file_path, compression='gzip')
adsb_data = data_processing.drop_nan_rows(df=adsb_data)
adsb_data = data_processing.filter_flights(df=adsb_data, airport_ICAO_code=airport_ICAO_code)
adsb_data = data_processing.remove_outliers(df=adsb_data)
adsb_data = data_processing.remove_outliers_geoaltitude(df=adsb_data)

adsb_data = trackmiles.calculate_remaining_track_miles(df=adsb_data)

logging.info('start data visualization')
fig = go.Figure()
fig = data_visualization.plot_waypoints(df=waypoints_data, fig=fig, airport_ICAO_code=airport_ICAO_code)
fig = data_visualization.animate_flight_trajectories(df=adsb_data, fig=fig)
fig.show()

#data_processing.write_animated_kml_for_each_callsign(adsb_data=df_filtered)