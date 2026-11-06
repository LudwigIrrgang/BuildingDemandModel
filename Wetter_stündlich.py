from pathlib import Path
import numpy as np
from Berechne_normalenvektoren import berechne_normalenvektoren

class Wetter_normal:
    def __init__(self, koordinaten, Raumtemperatur_Sommer, Raumtemperatur_Winter, strahlungswinkel, weather_type = "Normal"):
        self.strahlungswinkel = strahlungswinkel
        self.koordinaten = koordinaten
        self.weather_type = weather_type
        self.roomtemperature_summer = Raumtemperatur_Sommer
        self.roomtemperature_winter = Raumtemperatur_Winter
        self.pfad = Wetter_normal.get_path(self)
        self.datensatz = Wetter_normal.get_data(self)
        self.temperature = self.datensatz[0]
        self.irridation = self.datensatz[1]
        self.t_diff_heating = Wetter_normal.temperaturdifferenz(self)[1]
        self.t_diff_cooling = Wetter_normal.temperaturdifferenz(self)[0]
        
    
    def get_path(self):
        # suche den pfad der zu den Koordinaten passt
        type_dict = {"2015 Normal": ["/TRY2015_", "_Jahr.dat"], "2015 Heiß": ["/TRY2015_", "_Somm.dat"], "2015 Kalt": ["/TRY2015_", "_Wint.dat"], 
                     "2045 Normal": ["/TRY2045_", "_Jahr.dat"], "2045 Heiß": ["/TRY2045_", "_Somm.dat"], "2045 Kalt": ["/TRY2045_", "_Wint.dat"]}
        
        dist = 1000000
        pfad = Path("Wetterdaten")
        for f in pfad.iterdir():
            if not (f.is_dir() and f.name.startswith("TRY_")):
                continue  # andere Dateien (z. B. README.md) überspringen
            lat = int(f.name[4:10])
            lon = int(f.name[10:])
            distanz = ((round(self.koordinaten[0]*10000) - lat)**2 + (round(self.koordinaten[1]*10000) - lon)**2)**0.5
            if distanz < dist:
                dist = distanz
                pfad = "Wetterdaten/" + f.name + type_dict[self.weather_type][0] + f.name[4:] + type_dict[self.weather_type][1]
        print(pfad)
        return pfad
    
    def get_data(self):
        # suche den pfad der zu den Koordinaten passt
        with open(self.pfad, "r") as f:
            lines = f.readlines()
            temperature = []
            irridation = [[],[]]
            # starte ab zeile 35 wenn Jahr = 2015 sonst in Zeile 37
            if self.pfad[34] == "4":
                x = 36
            else:
                x = 34
            for line in lines[x:]:
                values = line.split()
                temperature.append(float(values[5]))
                irridation[0].append(float(values[12]))
                irridation[1].append(float(values[13]))
        return temperature, irridation
    
    
    def temperaturdifferenz(self):
        liste_sommer = []
        liste_winter = []
        for i in self.temperature:
            diff_sommer = round(self.roomtemperature_summer - i)
            diff_winter = round(self.roomtemperature_winter - i)
            liste_sommer.append(diff_sommer)
            liste_winter.append(diff_winter)
        return liste_sommer, liste_winter
    
    def endstrahlungsenergie(self, objekt, glasanteil, g_wert):
        grundriss_normalen = berechne_normalenvektoren(objekt)
        Q_dir = []
        for i in range(len(self.irridation[0])):
            Q_dir_tmp = min(max(0, self.irridation[0][i]/self.strahlungswinkel[i][2]), 1000) # max 1000 W/m²
            Q_dir.append(Q_dir_tmp)
        Q_dir = np.array(Q_dir) * glasanteil * g_wert
        Q_indir = np.array(self.irridation[1]) * glasanteil * g_wert

        Q_end = []
        for i in range(len(Q_dir)):
            Q_end.append(0)                  
            for normale in grundriss_normalen:

                Q_end[i] = Q_end[i] + max(Q_dir[i] * np.dot(self.strahlungswinkel[i], normale), 0) + Q_indir[i]
        return Q_end
            

    

    
    def __str__(self):
        return f"\nkoordinaten: {self.koordinaten}\nerste 50 Temperaturdifferenzen: {self.t_diff_kühlen[:50]}\n"
#w1 = Wetter_normal((481511,114391), 1)