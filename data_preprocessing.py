from geopy.distance import geodesic


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

    # Filter the DataFrame based on altitude and proximity to the airport
    filtered_df = df[(df['geoaltitude'] < 1000) & df.apply(within_airport_area, axis=1)]

    # Retain only rows corresponding to callsigns that meet the criteria
    return df[df['callsign'].isin(filtered_df['callsign'].unique())]



