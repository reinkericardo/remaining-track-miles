import os
import logging
import tarfile
import pandas as pd
from datetime import datetime


def extract_tar(file_path):
    """
    Extract tar file.
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
        kml_content.append('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
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
            if pd.isna(row_start['lon']) or pd.isna(row_start['lat']) or pd.isna(row_start['geoaltitude']) or pd.isna(row_end['lon']) or pd.isna(row_end['lat']) or pd.isna(row_end['geoaltitude']):
                logging.warning(f"Invalid coordinates for callsign {callsign} at index {i}")
                continue

            # Convert Unix timestamp to datetime and format for TimeSpan
            time_start = datetime.utcfromtimestamp(row_start['time']).strftime('%Y-%m-%dT%H:%M:%SZ')
            time_end = datetime.utcfromtimestamp(row_end['time']).strftime('%Y-%m-%dT%H:%M:%SZ')

            kml_content.append("<Placemark>\n")
            kml_content.append(f"    <TimeSpan>\n        <begin>{time_start}</begin>\n        <end>{time_end}</end>\n    </TimeSpan>\n")
            kml_content.append("    <LineString>\n")
            kml_content.append("        <extrude>1</extrude>\n")
            kml_content.append("        <altitudeMode>absolute</altitudeMode>\n")
            kml_content.append(f"        <coordinates>{row_start['lon']},{row_start['lat']},{row_start['geoaltitude']} {row_end['lon']},{row_end['lat']},{row_end['geoaltitude']}</coordinates>\n")
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
