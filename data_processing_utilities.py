import os
import logging
import tarfile
import pandas as pd
from datetime import datetime
from fastkml import kml
import gpxpy
from shapely.geometry import Point



def extract_tar(file_path):
    """
    Extract tar file.
    :param file_path: file path of tar file.
    :return:
    """
    with tarfile.open(file_path, 'r') as tar:
        tar.extractall()


def load_csv_gzip(file_path):
    """
    Load csv file as dataframe with pandas.
    :param file_path:  file path of csv file.
    :return:
    """
    return pd.read_csv(file_path, compression='gzip')


def write_kml_for_each_callsign(df):
    """
    Für jeden callsign eine KML-Datei schreiben.
    :param df: pandas DataFrame mit den Spalten 'callsign', 'time', 'lon', 'lat', 'geoaltitude'
    :return: None
    """
    # Erstelle einen Ordner für KML-Dateien, falls er nicht existiert
    kml_folder = 'kml'
    os.makedirs(kml_folder, exist_ok=True)

    # Gruppiere den DataFrame nach 'callsign'
    grouped = df.groupby('callsign')

    for callsign, group in grouped:
        k = kml.KML()
        doc = kml.Document()
        k.append(doc)
        doc.name = "Animated Tracks"

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

                # Erstelle einen Placemarker
                placemark = kml.Placemark()
                placemark.name = f"Point at {formatted_time}"

                # Erstelle Punkt-Objekt nur mit lon und lat (Höhe wird ignoriert)
                if not pd.isna(row['lon']) and not pd.isna(row['lat']):
                    point = Point(row['lon'], row['lat'])
                    placemark.geometry = point
                    placemark.description = f"Altitude: {row['geoaltitude']} meters"

                    # Erstelle und füge Zeitstempel hinzu
                    timestamp_kml = kml.TimeStamp()
                    timestamp_kml.when = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
                    placemark.time_stamp = timestamp_kml

                    doc.append(placemark)
                else:
                    logging.warning(f"Invalid coordinates for row {row}")

            except Exception as e:
                logging.warning(f"Error processing row {row}: {e}")

        # Speichere die KML-Datei im KML-Ordner
        kml_file_path = os.path.join(kml_folder, f'{callsign}.kml')
        try:
            with open(kml_file_path, 'w') as f:
                f.write(k.to_string(prettyprint=True))
            logging.info(f"Saved KML for {callsign} at {kml_file_path}")
        except Exception as e:
            logging.error(f"Failed to write KML file for {callsign}: {e}")


def write_gpx_for_each_callsign(df):
    """
    Für jeden callsign eine GPX-Datei erstellen.
    :param df: pandas DataFrame mit den Spalten 'callsign', 'time', 'lon', 'lat', 'geoaltitude'
    :return: None
    """
    # Erstelle einen Ordner für GPX-Dateien, falls er nicht existiert
    gpx_folder = 'gpx'
    os.makedirs(gpx_folder, exist_ok=True)

    # Gruppiere den DataFrame nach 'callsign'
    grouped = df.groupby('callsign')

    for callsign, group in grouped:
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
