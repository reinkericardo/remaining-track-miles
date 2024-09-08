import logging
import os
import shutil
import tarfile
import pandas as pd
import numpy as np
import airportsdata
from datetime import datetime


def convert_timestamp_to_datetime(timestamp):
    """
    converts timestamp to datetime object
    :param timestamp:
    :return:
    """
    dt = datetime.utcfromtimestamp(timestamp)
    return dt.strftime('%d %m %Y %H %M %S')


def extract_tar(file_path):
    """
    Extract tar file in same directory as `adsb_data_file_path`
    :param file_path: File path of tar file.
    :return: None
    """
    with tarfile.open(file_path, 'r') as tar:
        tar.extractall()
    logging.info('tar file extracted')


def xlsx_to_csv(input_file, output_file, sheet_name=0):
    df = pd.read_excel(input_file, sheet_name=sheet_name, engine='openpyxl')
    df.to_csv(output_file, index=False)
    logging.info(f"{input_file} saved to {output_file}")


def load_csv(file_path, compression=None):
    """
    Load csv file as dataframe with pandas.
    :param file_path:  File path of csv file.
    :return: dataframe with pandas.
    """
    df = pd.read_csv(file_path, compression=compression)
    logging.info(f'loaded csv file from {file_path}')
    return df


def write_kml_for_each_callsign(df, animate=False):
    """
    Creates a KML file for each unique callsign in the DataFrame. The KML files visualize the flight paths with
    coordinates including longitude, latitude, and altitude. If animate is True, an animated KML path is created.

    :param df: pandas DataFrame containing the flight data with columns 'callsign', 'time', 'lon', 'lat', and 'geoaltitude'
    :param animate: Boolean indicating whether to create animated KML paths.
    :return: None
    """
    kml_folder = 'kml'
    if os.path.exists(kml_folder):
        shutil.rmtree(kml_folder)
    os.makedirs(kml_folder, exist_ok=True)

    grouped = df.groupby('callsign')

    for callsign, group in grouped:
        group = group.sort_values('time')

        if group.empty:
            logging.info(f"No points available for callsign: {callsign}")
            continue

        # KML header
        kml_content = [
            "<?xml version='1.0' encoding='UTF-8'?>\n",
            '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n',
            "<Document>\n",
            f"<name>Flight path for {callsign}</name>\n"
        ]

        # Add static or animated path
        if animate:
            kml_content.append("<Placemark>\n")
            kml_content.append(f"<name>Animated Flight path for {callsign}</name>\n")
            kml_content.append("<gx:Track>\n")
            kml_content.append("<altitudeMode>absolute</altitudeMode>\n")

            # Add time and coordinates for animation
            for _, row in group.iterrows():
                kml_content.append(f"<when>{row['time']}</when>\n")
                kml_content.append(f"<gx:coord>{row['lon']} {row['lat']} {row['geoaltitude']}</gx:coord>\n")

            kml_content.append("</gx:Track>\n")
            kml_content.append("</Placemark>\n")
        else:
            # Standard static path
            kml_content.append("<Placemark>\n")
            kml_content.append(f"   <name>Flight path for {callsign}</name>\n")
            kml_content.append("   <LineString>\n")
            kml_content.append("       <extrude>1</extrude>\n")
            kml_content.append("       <altitudeMode>absolute</altitudeMode>\n")
            kml_content.append("       <coordinates>\n")

            for _, row in group.iterrows():
                if pd.notna(row['lon']) and pd.notna(row['lat']) and pd.notna(row['geoaltitude']):
                    kml_content.append(f"        {row['lon']},{row['lat']},{row['geoaltitude']}\n")
                else:
                    logging.warning(f"Invalid coordinates for row {row}")

            kml_content.append("       </coordinates>\n")
            kml_content.append("   </LineString>\n")
            kml_content.append("</Placemark>\n")

        # KML footer
        kml_content.append("</Document>\n</kml>\n")

        # Save the KML file
        kml_file_path = os.path.join(kml_folder, f'{callsign}.kml')
        try:
            with open(kml_file_path, 'w') as f:
                f.write(''.join(kml_content))
            logging.info(f"Saved KML for {callsign} at {kml_file_path}")
        except Exception as e:
            logging.error(f"Failed to write KML file for {callsign}: {e}")


def filter_flights(df, airport_ICAO_code):
    """
    Filters the DataFrame to retain only those flights (callsigns) that land or start at a certain airport_ICAO_code.

    :param df: pandas DataFrame containing the flight data with columns 'callsign', 'time', 'lon', 'lat', 'geoaltitude'
    :param airport_ICAO_code: airport_ICAO_code ICAO code to filter
    :return: filtered DataFrame by 'callsign'
    """

    def within_airport_area(row):
        """
        Check if the given row's coordinates are within a certain threshold distance from the specified airport_ICAO_code coordinates.

        :param row: A pandas Series representing a row in the DataFrame.
        :return: True if the row is within the threshold distance from the airport_ICAO_code, False otherwise.
        """
        return abs(row['lat'] - airport_lat) < 0.1 and abs(row['lon'] - airport_lon) < 0.1

    airports = airportsdata.load()
    airport_lat = airports[airport_ICAO_code]['lat']
    airport_lon = airports[airport_ICAO_code]['lon']
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
