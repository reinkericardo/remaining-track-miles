import logging
import numpy as np
import pandas as pd
from scipy.stats import zscore


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



