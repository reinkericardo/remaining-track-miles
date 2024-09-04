import logging
import os
import tarfile
import pandas as pd
import numpy as np
from datetime import datetime


def extract_tar(file_path):
    """
    Extract tar file in same directory as `file_path`
    :param file_path: File path of tar file.
    :return: None
    """
    with tarfile.open(file_path, 'r') as tar:
        tar.extractall()


def load_csv_gzip(file_path):
    """
    Load csv file as dataframe with pandas.
    :param file_path:  File path of csv file.
    :return: None
    """
    return pd.read_csv(file_path, compression='gzip')


def write_kml_for_each_callsign(df):
    """
    Creates a KML file for each unique callsign in the DataFrame. The KML files will visualize the flight paths with
    coordinates including longitude, latitude, and altitude.

    :param df: pandas DataFrame containing the flight data with columns 'callsign', 'time', 'lon', 'lat', and 'geoaltitude'
    :return: None
    """
    kml_folder = 'kml'
    os.makedirs(kml_folder, exist_ok=True)

    # Group the DataFrame by 'callsign'
    grouped = df.groupby('callsign')

    for callsign, group in grouped:
        # Sort the group by time
        group = group.sort_values('time')

        # Check if there are enough points to create a line
        if group.shape[0] == 0:
            logging.info(f"No points available for callsign: {callsign}")
            continue

        # Create KML structure
        kml_content = []
        kml_content.append("<?xml version='1.0' encoding='UTF-8'?>\n")
        kml_content.append(
            '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
        kml_content.append("<Document>\n")
        kml_content.append(f"<name>Flight path for {callsign}</name>\n")
        kml_content.append("<Placemark>\n")
        kml_content.append(f"   <name>Flight path for {callsign}</name>\n")
        kml_content.append("   <LineString>\n")
        kml_content.append("       <extrude>1</extrude>\n")
        kml_content.append("       <altitudeMode>absolute</altitudeMode>\n")
        kml_content.append("       <coordinates>\n")

        for _, row in group.iterrows():
            try:
                if not pd.isna(row['lon']) and not pd.isna(row['lat']) and not pd.isna(row['geoaltitude']):
                    # Add the coordinates with longitude, latitude, and altitude
                    kml_content.append(f"        {row['lon']},{row['lat']},{row['geoaltitude']}\n")
                else:
                    logging.warning(f"Invalid coordinates for row {row}")

            except Exception as e:
                logging.warning(f"Error processing row {row}: {e}")

        kml_content.append("       </coordinates>\n")
        kml_content.append("   </LineString>\n")
        kml_content.append("</Placemark>\n")
        kml_content.append("</Document>\n")
        kml_content.append("</kml>\n")

        # Save the KML file in the KML folder
        kml_file_path = os.path.join(kml_folder, f'{callsign}.kml')
        try:
            with open(kml_file_path, 'w') as f:
                f.write(''.join(kml_content))
            logging.info(f"Saved KML for {callsign} at {kml_file_path}")
        except Exception as e:
            logging.error(f"Failed to write KML file for {callsign}: {e}")


def write_animated_kml_for_each_callsign(df):
    """
    Creates an animated KML file for each unique callsign in the DataFrame. The KML files will visualize the flight paths
    with coordinates including longitude, latitude, altitude, and time, allowing an animation to take place.

    :param df: pandas DataFrame containing the flight data with columns 'callsign', 'time', 'lon', 'lat', and 'geoaltitude'
    :return: None
    """
    # Create a folder for KML files if it doesn't exist
    kml_folder = 'kml'
    os.makedirs(kml_folder, exist_ok=True)

    # Group the DataFrame by 'callsign'
    grouped = df.groupby('callsign')

    for callsign, group in grouped:
        # Sort the group by time
        group = group.sort_values('time')

        # Check if there are enough points to create a line
        if group.shape[0] < 2:
            logging.info(f"Not enough points available for callsign: {callsign}")
            continue

        # Create KML structure
        kml_content = []
        kml_content.append("<?xml version='1.0' encoding='UTF-8'?>\n")
        kml_content.append('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        kml_content.append("<Document>\n")
        kml_content.append(f"<name>Animated flight path for {callsign}</name>\n")

        for i in range(1, len(group)):
            row_start = group.iloc[i - 1]
            row_end = group.iloc[i]

            # Ensure all required data is available
            if pd.isna(row_start['lon']) or pd.isna(row_start['lat']) or pd.isna(row_start['geoaltitude']) or pd.isna(
                    row_end['lon']) or pd.isna(row_end['lat']) or pd.isna(row_end['geoaltitude']):
                logging.warning(f"Invalid coordinates for callsign {callsign} at index {i}")
                continue

            # Convert Unix timestamp to datetime and format for TimeSpan
            time_start = datetime.utcfromtimestamp(row_start['time']).strftime('%Y-%m-%dT%H:%M:%SZ')
            time_end = datetime.utcfromtimestamp(row_end['time']).strftime('%Y-%m-%dT%H:%M:%SZ')

            kml_content.append("<Placemark>\n")
            kml_content.append(
                f"    <TimeSpan>\n        <begin>{time_start}</begin>\n        <end>{time_end}</end>\n    </TimeSpan>\n")
            kml_content.append("    <LineString>\n")
            kml_content.append("        <extrude>1</extrude>\n")
            kml_content.append("        <altitudeMode>absolute</altitudeMode>\n")
            kml_content.append(
                f"        <coordinates>{row_start['lon']},{row_start['lat']},{row_start['geoaltitude']} {row_end['lon']},{row_end['lat']},{row_end['geoaltitude']}</coordinates>\n")
            kml_content.append("    </LineString>\n")
            kml_content.append("</Placemark>\n")

        kml_content.append("</Document>\n")
        kml_content.append("</kml>\n")

        # Save the KML file in the KML folder
        kml_file_path = os.path.join(kml_folder, f'{callsign}_animated.kml')
        try:
            with open(kml_file_path, 'w') as f:
                f.write(''.join(kml_content))
            logging.info(f"Saved animated KML for {callsign} at {kml_file_path}")
        except Exception as e:
            logging.error(f"Failed to write animated KML file for {callsign}: {e}")


def filter_flights(df, airport_coords):
    """
    Filters the DataFrame to retain only those flights (callsigns) that land or start at a certain airport.

    :param df: pandas DataFrame containing the flight data with columns 'callsign', 'time', 'lon', 'lat', 'geoaltitude'
    :param airport_coords: tuple containing the latitude and longitude of the airport
    :return: filtered DataFrame by 'callsign'
    """

    def within_airport_area(row):
        """
        Check if the given row's coordinates are within a certain threshold distance from the specified airport coordinates.

        :param row: A pandas Series representing a row in the DataFrame.
        :return: True if the row is within the threshold distance from the airport, False otherwise.
        """
        return abs(row['lat'] - airport_coords[0]) < 0.1 and abs(row['lon'] - airport_coords[1]) < 0.1

    filtered_df = df[(df['geoaltitude'] < 1000) & df.apply(within_airport_area, axis=1)]

    return df[df['callsign'].isin(filtered_df['callsign'].unique())]


def drop_nan_rows(df):
    """
    Drops rows from the DataFrame where any NaN values are present in the 'lat', 'geoaltitude', or 'lon' columns.

    :param df: pandas DataFrame containing the flight data with columns 'lat', 'geoaltitude', 'lon', and others.
    :return: DataFrame with rows containing NaN values in the specified columns removed.
    """
    df_cleaned = df.dropna(subset=['lat', 'lon', 'geoaltitude'])

    return df_cleaned


def remove_outliers(df):
    """
    Entfernt Ausreißer aus den 'lon', 'lat' und 'geoaltitude' Spalten eines DataFrames.

    :param df: pandas DataFrame, das die Flugdaten enthält.
    :return: DataFrame: Der bereinigte DataFrame mit entfernten Ausreißern.
    """

    def filter_outliers(group):
        Q1 = group[['lon', 'lat', 'geoaltitude']].quantile(0.25)
        Q3 = group[['lon', 'lat', 'geoaltitude']].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        return group[
            (group['lon'] >= lower_bound['lon']) & (group['lon'] <= upper_bound['lon']) &
            (group['lat'] >= lower_bound['lat']) & (group['lat'] <= upper_bound['lat']) &
            (group['geoaltitude'] >= lower_bound['geoaltitude']) & (group['geoaltitude'] <= upper_bound['geoaltitude'])
            ]

    df_cleaned = df.groupby('callsign', group_keys=False).apply(filter_outliers)

    return df_cleaned


def remove_outliers_geoaltitude(df, threshold=200):
    """
    Entfernt Ausreißer in der geoaltitude-Spalte basierend auf einem Schwellenwert für die Differenz zwischen
    aufeinander folgenden Höhenwerten.

    :param df: DataFrame mit den Flugzeugdaten
    :param threshold: Schwellenwert für die Differenz zwischen aufeinander folgenden Höhenwerten
    :return: DataFrame ohne Ausreißer
    """
    df['prev_geoaltitude'] = df.groupby('callsign')['geoaltitude'].shift(1)
    df['altitude_diff'] = df['geoaltitude'] - df['prev_geoaltitude']

    for callsign, group in df.groupby('callsign'):
        for index, row in group.iterrows():
            if not pd.isna(row['altitude_diff']) and abs(row['altitude_diff']) > threshold:
                logging.info(f'removed for {callsign} the geoaltitude: {df.loc[index, "geoaltitude"]} m')
                df.loc[index, 'geoaltitude'] = np.nan

    df = df.drop(columns=['prev_geoaltitude', 'altitude_diff'])

    df['geoaltitude'] = df.groupby('callsign')['geoaltitude'].transform(lambda x: x.interpolate(method='linear'))

    return df
