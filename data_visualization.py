import plotly.graph_objects as go


def visualize_flight_trajectory(df):
    """
    Visualizes the 3D flight trajectories grouped by callsigns.

    :param df: DataFrame containing flight data with columns 'lon', 'lat', 'geoaltitude', and 'callsign'.
    :return: None. Displays an interactive 3D plot.
    """
    fig = go.Figure()

    grouped = df.groupby('callsign')

    for name, group in grouped:
        fig.add_trace(go.Scatter3d(
            x=group['lon'],
            y=group['lat'],
            z=group['geoaltitude'],
            mode='lines+markers',
            name=name,
            text=group['time'],
            marker=dict(size=4),
            line=dict(width=2)
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(nticks=10, range=[df['lon'].min(), df['lon'].max()]),
            yaxis=dict(nticks=10, range=[df['lat'].min(), df['lat'].max()]),
            zaxis=dict(nticks=10, range=[df['geoaltitude'].min(), df['geoaltitude'].max()]),
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude',
            aspectratio=dict(
                x=1,
                y=1,
                z=0.1
            ),
        ),
        title=dict(
            text="Interactive 3D Flight Paths by Callsign",
            x=0.5
        ),
        legend=dict(
            title='Callsigns',
            x=0.85,
            y=0.9
        ),
    )

    fig.show()