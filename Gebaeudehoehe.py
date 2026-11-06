#Höhenermittlung für das erste Gebäude das sich innerhalb von 50m um die Adresse befindet

import xml.dom.minidom
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

def gebaeudehoehe(Koordinaten):
    def get_path(Koordinaten):
        # suche den Pfad der zu den Koordinaten passt
        dist = 1000000
        pfad = Path("Gebäudehöhe")
        for f in pfad.iterdir():
            if f.suffix.lower() != ".gml":
                continue  # andere Dateien (z. B. README.md) überspringen
            lon = int(f.name[0:3])
            lat = int(f.name[4:8])
            print(lon, lat)
            if 0 <= Koordinaten[0]/1000 - lon <= 2 and 0 <= Koordinaten[1]/1000 - lat <= 2:
                return f.name
        raise ValueError(f'Keine passende Datei für die Koordinaten {Koordinaten} gefunden.')
    pfad = get_path(Koordinaten)
    doc = xml.dom.minidom.parse(f"Gebäudehöhe/{pfad}")
    CityObjectMember = doc.getElementsByTagName("cityObjectMember")
    Höhe = []
    Address = []
    Neigung = []
    suchradius = 20
    while Höhe == []:
        koord_gerundet = (round(Koordinaten[0]/suchradius)*suchradius, round(Koordinaten[1]/suchradius)*suchradius)
        print(koord_gerundet)
        for com in CityObjectMember:
            bldg = com.getElementsByTagName("bldg:Building")
            if len(bldg) == 0:
                continue
            bldg = bldg[0]
            #print(bldg.getElementsByTagName("creationDate")[0].firstChild.data)

            boden = bldg.getElementsByTagName("bldg:GroundSurface")[0]
            Koordinaten_dataset = boden.getElementsByTagName("gml:posList")[0].firstChild.data.split(" ")
            
        
            for i in range(round(len(Koordinaten_dataset)/3)):
                lat = float(Koordinaten_dataset[3*i])
                lon = float(Koordinaten_dataset[3*i+1])
                lat_gerundet = round(lat/suchradius)*suchradius
                lon_gerundet = round(lon/suchradius)*suchradius
                if koord_gerundet == (lat_gerundet, lon_gerundet):
                    if len(bldg.getElementsByTagName("bldg:measuredHeight")) > 0:
                        height = bldg.getElementsByTagName("bldg:measuredHeight")[0].firstChild.data
                        Höhe.append(height)
                    else:
                        Höhe.append(10)  # Standardhöhe, falls keine Höhe angegeben ist
                    # falls "xAL:ThoroughfareName" vorhanden ist, dann wird die Adresse extrahiert
                    Adresse = bldg.getElementsByTagName("xAL:ThoroughfareName")[0].firstChild.data if bldg.getElementsByTagName("xAL:ThoroughfareName") else None
                    Address.append(Adresse)
                    Dachneigung_node = bldg.getElementsByTagName("gen:stringAttribute")
                    for node in Dachneigung_node:
                        if node.getAttribute("name") == "Dachneigung":
                            Dachneigung = node.getElementsByTagName("gen:value")[0].firstChild.data
                            Neigung.append(Dachneigung)
                            break
                    else:
                        Neigung.append(None)  # Falls keine Dachneigung gefunden wird, füge None hinzu
                    return (Höhe[0], Address[0], Neigung[0])
        suchradius += 20
    

