import logging
import airportsdata
import numpy as np
import plotly.graph_objects as go


def visualize(adsb_data, waypoints_data, airport_ICAO_code, show_animation):
    logging.info('start data visualization')
    fig = go.Figure()
    fig = plot_waypoints(df=waypoints_data, fig=fig, airport_ICAO_code=airport_ICAO_code)
    fig = visualize_flight_trajectories(df=adsb_data, fig=fig, airport_ICAO_code=airport_ICAO_code,
                                        show_animation=show_animation)
    fig.show()


def plot_waypoints(df, fig, airport_ICAO_code):
    """
    Plots waypoints on the provided figure for the specified airport_ICAO_code ICAO code.

    :param df: DataFrame with columns 'Latitude', 'Longitude', 'Designator', 'Name', 'Type', 'Associated Airport'.
    :param fig: Plotly figure object to which the waypoints will be added.
    :param airport_ICAO_code: The ICAO code of the airport_ICAO_code to filter waypoints.
    :return: Updated figure with waypoint traces added.
    """
    df_filtered = df[(df['Associated Airport'] == airport_ICAO_code) &
                     (df['Type'].isin(['ICAO', 'TERMINAL']))]
    for index, waypoint in df_filtered.iterrows():
        logging.info(f'Waypoint {waypoint["Name"]}')
    z = np.zeros(len(df_filtered))

    fig.add_trace(go.Scatter3d(
        x=df_filtered['Longitude'],
        y=df_filtered['Latitude'],
        z=z,
        mode='markers',
        marker=dict(size=8, color='blue'),
        text=df_filtered['Designator'],
        hoverinfo='text',
        name='Waypoints'
    ))

    return fig


def visualize_flight_trajectories(df, fig, airport_ICAO_code, show_animation=True):
    """
    Visualizes the 3D flight trajectories grouped by callsigns with time-based animation.

    :param show_animation: if true animates the flight trajectories
    :param df: DataFrame containing flight data with columns 'lon', 'lat', 'geoaltitude', 'callsign', and 'time'.
    :return: None. Displays an interactive 3D animated plot.
    """

    df = df.sort_values(by='time')
    df_grouped = df.groupby('callsign')
    airports = airportsdata.load()
    airport_name = airports[airport_ICAO_code]['name']

    for name, group in df_grouped:
        fig.add_trace(go.Scatter3d(
            x=group['lon'],
            y=group['lat'],
            z=group['geoaltitude'],
            mode='lines+markers',
            name=name,
            text=group['time'],
            marker=dict(size=4),
            line=dict(width=2),
            hovertemplate="Longitude: %{x}<br>" +
                          "Latitude: %{y}<br>" +
                          "Altitude: %{z}<br>" +
                          "Time: %{text}<br>" +
                          "RTM: %{customdata:.2f} km<extra></extra>",
            customdata=group['rtm']
        ))

    # Common layout settings
    scene_settings = dict(
        xaxis=dict(nticks=10, range=[df['lon'].min(), df['lon'].max()]),
        yaxis=dict(nticks=10, range=[df['lat'].min(), df['lat'].max()]),
        zaxis=dict(nticks=10, range=[0, max(df['geoaltitude'].max(), 10)]),
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        zaxis_title='Altitude',
        aspectratio=dict(x=1, y=1, z=0.1),
        dragmode='turntable' if show_animation else 'zoom',
    )

    fig.update_layout(
        scene=scene_settings,
        title=dict(text=f'Flight Trajectories for {airport_name} ({airport_ICAO_code})', x=0.5),
        legend=dict(title='Callsigns', x=0.85, y=0.9),
    )

    if show_animation:
        fig.update_layout(
            updatemenus=[dict(type='buttons', showactive=False,
                              buttons=[dict(label='Play',
                                            method='animate',
                                            args=[None, dict(frame=dict(duration=500, redraw=True),
                                                             fromcurrent=False)])])],
        )

        frames = [go.Frame(data=[go.Scatter3d(
            x=group['lon'][group['time'] <= t],
            y=group['lat'][group['time'] <= t],
            z=group['geoaltitude'][group['time'] <= t],
            mode='lines+markers',
            name=name,
            marker=dict(size=4),
            line=dict(width=2),
            text=group['time'][group['time'] <= t],
            hovertemplate="Longitude: %{x}<br>" +
                          "Latitude: %{y}<br>" +
                          "Altitude: %{z}<br>" +
                          "Time: %{text}<br>" +
                          "RTM: %{customdata:.2f} km<extra></extra>",
            customdata=group['rtm'][group['time'] <= t]
        ) for name, group in df_grouped],
            name=str(t),
            layout=go.Layout(title=f'Flight Trajectories at Time {t}')
        ) for t in sorted(df['time'].unique())]

        fig.frames = frames

    return fig
