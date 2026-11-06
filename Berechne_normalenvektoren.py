from shapely.geometry import Polygon
import numpy as np

def berechne_normalenvektoren(gebaeude_polygon):
    # Extrahiere die Koordinaten des Polygons
    coords = list(gebaeude_polygon.exterior.coords)
    normalenvektoren = []

    # Iteriere über die Kanten des Polygons
    for i in range(len(coords) - 1):  # Letzter Punkt ist identisch mit dem ersten
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]

        # Berechne den Kantenvektor
        kantenvektor = (x2 - x1, y2 - y1)
        kantenlänge = float(np.sqrt(kantenvektor[0]**2 + kantenvektor[1]**2))
        # Berechne den Normalenvektor (orthogonal zum Kantenvektor)
        normalenvektor = (-(kantenvektor[1]), kantenvektor[0])

        # Normiere den Normalenvektor (optional)
        laenge = np.sqrt(normalenvektor[0]**2 + normalenvektor[1]**2)
        normalenvektor_normalisiert = (normalenvektor[0] / laenge, normalenvektor[1] / laenge)
        normalenvektor_gewichtet = (float(normalenvektor_normalisiert[0]) * kantenlänge, float(normalenvektor_normalisiert[1]) * kantenlänge, 0)
        normalenvektoren.append(normalenvektor_gewichtet)

    return normalenvektoren

#Beispiel: Polygon eines Gebäudes
#gebaeude = Polygon([(0, 0), (4, 0), (4, 3), (0, 3), (0, 0)])  # Rechteck
#normalenvektoren = berechne_normalenvektoren(gebaeude)

#print("Normalenvektoren:", normalenvektoren)