import os
import logging
import tarfile
import pandas as pd
from datetime import datetime
import gpxpy


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


def drop_nan_rows(df):
    """
    Drops rows from the DataFrame where any NaN values are present in the 'lat', 'geoaltitude', or 'lon' columns.

    :param df: pandas DataFrame containing the flight data with columns 'lat', 'geoaltitude', 'lon', and others.
    :return: DataFrame with rows containing NaN values in the specified columns removed.
    """
    df_cleaned = df.dropna(subset=['lat', 'lon', 'geoaltitude'])

    return df_cleaned


def write_kml_for_each_callsign(df):
    """
    Creates a KML file for each unique callsign in the DataFrame. The KML files will visualize the flight paths with
    coordinates including longitude, latitude, and altitude.

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


def write_gpx_for_each_callsign(df):
    """
    Write for each callsing a seperate gpx file
    :param df: grouped pandas DataFrame with the columns 'callsign', 'time', 'lon', 'lat', 'geoaltitude'
    :return: None
    """
    # Erstelle einen Ordner für GPX-Dateien, falls er nicht existiert
    gpx_folder = 'gpx'
    os.makedirs(gpx_folder, exist_ok=True)

    for callsign, group in df:
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        # Sortiere nach Zeit
        group = group.sort_values('time')

        # Überprüfen, ob genug Punkte vorhanden sind
        if group.shape[0] == 0:
            logging.info(f"No points available for callsign: {callsign}")
            continue

        for _, row in group.iterrows():
            try:
                # Konvertiere Zeitstempel zu datetime
                timestamp = datetime.fromtimestamp(row['time'])
                formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                # Erstelle einen Wegpunkt
                waypoint = gpxpy.gpx.GPXWaypoint(
                    latitude=row['lat'],
                    longitude=row['lon'],
                    elevation=row['geoaltitude'],
                    time=timestamp
                )
                gpx_segment.points.append(waypoint)
            except Exception as e:
                logging.warning(f"Error processing row {row}: {e}")

        # Speichere die GPX-Datei im GPX-Ordner
        gpx_file_path = os.path.join(gpx_folder, f'{callsign}.gpx')
        try:
            with open(gpx_file_path, 'w') as f:
                f.write(gpx.to_xml())
            logging.info(f"Saved GPX for {callsign} at {gpx_file_path}")
        except Exception as e:
            logging.error(f"Failed to write GPX file for {callsign}: {e}")
