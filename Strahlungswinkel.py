import pandas as pd
import pvlib
from pvlib.location import Location
def strahlungswinkel(lat, lon):
    # Standortdefinition für München
    location = Location(latitude=lat, longitude=lon, tz='Europe/Berlin')

    # Zeitstempel für das Jahr 2025 in stündlicher Auflösung
    times = pd.date_range(start='2015-01-01 00:00', end='2015-12-31 23:00', freq='h', tz='Europe/Berlin')

    # Berechnung des Sonnenstands
    solar_position = location.get_solarposition(times)

    # Extraktion von Azimut und Elevation
    azimuth = solar_position['azimuth']
    elevation = solar_position['apparent_elevation']

    # Berechnung des Richtungsvektors
    import numpy as np

    # Umwandlung in Bogenmaß
    azimuth_rad = np.radians(azimuth)
    elevation_rad = np.radians(elevation)

    # Berechnung der Richtungsvektoren
    x = np.cos(elevation_rad) * np.sin(azimuth_rad)
    y = np.cos(elevation_rad) * np.cos(azimuth_rad)
    z = np.sin(elevation_rad)

    # Erstellung eines DataFrames mit den Richtungsvektoren
    direction_vectors = pd.DataFrame({'x': x, 'y': y, 'z': z}, index=times)
    array = direction_vectors.to_numpy()
    print(array[0:10])  # Ausgabe der ersten 10 Zeilen zur Überprüfung
    return array


# Beispielaufruf der Funktion
if __name__ == "__main__":
    lat = 48.1351  # Beispiel: München
    lon = 11.5820
    strahlungswinkel(lat, lon)