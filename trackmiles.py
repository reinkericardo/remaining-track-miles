import pandas as pd
import numpy as np
from geopy.distance import geodesic


def calculate_remaining_track_miles(df):
    df = df.groupby('callsign').apply(calculate_rtm)
    df = df.reset_index(drop=True)
    return df


def calculate_rtm(df):
    distances = [0]
    rtm = 0

    # Gehe die Punkte in umgekehrter Reihenfolge durch
    for i in range(len(df) - 1, 0, -1):
        if df.iloc[i]['onground']:
            rtm = 0
        else:
            point1 = (df.iloc[i - 1]['lat'], df.iloc[i - 1]['lon'])
            point2 = (df.iloc[i]['lat'], df.iloc[i]['lon'])
            rtm += geodesic(point1, point2).kilometers

        distances.append(rtm)

    distances.reverse()  # Da wir rückwärts gezählt haben, muss die Liste umgedreht werden
    df['rtm'] = distances
    return df