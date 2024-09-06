import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import numpy as np
from PIL import Image


def plot_flight_trajectories(df):
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
            line=dict(width=2),
            hovertemplate=
            "Longitude: %{x}<br>" +
            "Latitude: %{y}<br>" +
            "Altitude: %{z}<br>" +
            "Time: %{text}<br>" +
            "RTM: %{customdata:.2f} km<extra></extra>",
            customdata=group['rtm']
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
                z=0.05
            ),
        ),
        title=dict(
            text='remaining track miles',
            x=0.5
        ),
        legend=dict(
            title='Callsigns',
            x=0.85,
            y=0.9
        ),
    )

    fig.show()


def plot_flight_trajectories_with_map(df, map_image_path='map_image.png'):
    """
    Visualizes flight trajectories with a 2D map embedded as the XY plane in a rotating 3D plot.

    :param df: DataFrame containing flight data with columns 'lon', 'lat', 'geoaltitude', and 'callsign'.
    :param map_image_path: Path to save the exported map image.
    :return: None. Displays an interactive 3D plot with embedded 2D map.
    """

    # Generiere eine 2D-Karte mit Plotly Express
    map_figure = px.scatter_mapbox(df, lat='lat', lon='lon', zoom=4, height=500)
    map_figure.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Exportiere die Karte als Bild
    pio.write_image(map_figure, map_image_path, format='png', scale=2)

    # Bild laden und in ein Array konvertieren
    img = Image.open(map_image_path)
    img = img.convert('RGB')
    img_array = np.array(img)

    # 2D-Koordinaten für die 3D-Projektion erstellen
    x = np.linspace(df['lon'].min(), df['lon'].max(), img_array.shape[1])
    y = np.linspace(df['lat'].min(), df['lat'].max(), img_array.shape[0])
    x, y = np.meshgrid(x, y)

    # Z-Ebene für die Projektion
    z = np.zeros_like(x)

    # Verwende den Rotkanal des Bildes als Farbwert (surfacecolor)
    surfacecolor = img_array[..., 0]  # Verwende den Rotkanal für surfacecolor

    # Erstelle die Plotly-Figur
    fig = go.Figure()

    # Füge die 2D-Karte als Oberfläche hinzu
    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        surfacecolor=surfacecolor,
        colorscale='Gray',  # Du kannst auch 'Viridis' oder andere Farbskalen verwenden
        cmin=0, cmax=255,
        showscale=False
    ))

    # Hinzufügen der Flugtrajektorien als 3D Scatter
    grouped = df.groupby('callsign')
    for name, group in grouped:
        scatter = go.Scatter3d(
            x=group['lon'],
            y=group['lat'],
            z=group['geoaltitude'],
            mode='lines',  # Linienmodus für die Darstellung der Trajektorien
            line=dict(width=2, color='blue'),
            text=group['callsign'],
            name=name
        )
        fig.add_trace(scatter)

    # Layout-Update für die 3D-Anzeige
    fig.update_layout(
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude',
            aspectmode='cube',
            xaxis=dict(range=[df['lon'].min(), df['lon'].max()]),
            yaxis=dict(range=[df['lat'].min(), df['lat'].max()]),
            zaxis=dict(range=[0, df['geoaltitude'].max()])
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=700
    )

    # Plot anzeigen
    fig.show()

def animate_flight_trajectories(df):
    """
        Visualizes the 3D flight trajectories grouped by callsigns with time-based animation.

        :param df: DataFrame containing flight data with columns 'lon', 'lat', 'geoaltitude', 'callsign', and 'time'.
        :return: None. Displays an interactive 3D animated plot.
        """
    fig = go.Figure()

    # Sort data by time to ensure proper animation
    df = df.sort_values(by='time')

    grouped = df.groupby('callsign')

    # Create an animated trace for each flight based on time
    for name, group in grouped:
        fig.add_trace(go.Scatter3d(
            x=group['lon'],
            y=group['lat'],
            z=group['geoaltitude'],
            mode='lines+markers',
            name=name,
            text=group['time'],
            marker=dict(size=4),
            line=dict(width=2),
            hovertemplate=
            "Longitude: %{x}<br>" +
            "Latitude: %{y}<br>" +
            "Altitude: %{z}<br>" +
            "Time: %{text}<br>" +
            "RTM: %{customdata:.2f} km<extra></extra>",
            customdata=group['rtm']
        ))

    # Update layout for animation and 3D interactivity
    fig.update_layout(
        updatemenus=[dict(type='buttons', showactive=False,
                          buttons=[dict(label='Play',
                                        method='animate',
                                        args=[None, dict(frame=dict(duration=500, redraw=True),
                                                         fromcurrent=False)])])],
        scene=dict(
            xaxis=dict(nticks=10, range=[df['lon'].min(), df['lon'].max()]),
            yaxis=dict(nticks=10, range=[df['lat'].min(), df['lat'].max()]),
            zaxis=dict(nticks=10, range=[df['geoaltitude'].min(), df['geoaltitude'].max()]),
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude',
            aspectratio=dict(x=1, y=1, z=0.05),
            dragmode='turntable'
        ),
        title=dict(text='Flight Trajectories Over Time', x=0.5),
        legend=dict(title='Callsigns', x=0.85, y=0.9),
    )

    # Create frames for animation
    frames = [go.Frame(data=[go.Scatter3d(
        x=group['lon'][group['time'] <= t],
        y=group['lat'][group['time'] <= t],
        z=group['geoaltitude'][group['time'] <= t],
        mode='lines+markers',
        name=name,
        marker=dict(size=4),
        line=dict(width=2),
        text=group['time'][group['time'] <= t],
        hovertemplate=
        "Longitude: %{x}<br>" +
        "Latitude: %{y}<br>" +
        "Altitude: %{z}<br>" +
        "Time: %{text}<br>" +
        "RTM: %{customdata:.2f} km<extra></extra>",
        customdata=group['rtm'][group['time'] <= t]
    ) for name, group in grouped],
        name=str(t),
        layout=go.Layout(title=f'Flight Trajectories at Time {t}')
    ) for t in sorted(df['time'].unique())]

    fig.frames = frames

    fig.show()
