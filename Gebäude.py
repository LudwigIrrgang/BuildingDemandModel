# Stand: 2025-04-08

from Baujahr_100mGrid import Baujahr
from Gebaeudehoehe import gebaeudehoehe
from math import cos, pi, isnan
from NWG.Dämmwerte_NWG import get_u_values, get_waste_heat, get_hot_drinking_water
import numpy as np

class Gebaeude:
    def __init__(self, id, koordinaten, Grundfläche, Geometrie, Stockwerke, umfang, Weather_obj, category):
        self.id = id
        self.koordinaten = koordinaten #EPSG:25832
        self.gf = Grundfläche
        self.umfang = umfang
        self.category = category 
        self.geometrie = Geometrie
        self.weather_obj = Weather_obj
        self.höhe_adresse_neigung = gebaeudehoehe(self.koordinaten)
        self.höhe = self.höhe_adresse_neigung[0]
        self.adresse = self.höhe_adresse_neigung[1]
        self.neigung = float(self.höhe_adresse_neigung[2]) if self.höhe_adresse_neigung[2] is not None else 0.0 # ohne Angabe in LoD2: Flachdach
        self.stockwerke = int(float(self.höhe) / 3) if np.sum(Stockwerke) == 0 else Stockwerke  # Stockwerke = Höhe / 3m
        self.dachfläche = self.gf / cos(float(self.neigung) * pi / 180) # geneigte Dachfläche = Grundfläche / cos(Neigung); Flachdach (0°) = Grundfläche
        self.wandfläche = float(self.umfang) * float(self.höhe) # Umfang * Höhe
        self.nutzfläche = self.gf * np.sum(self.stockwerke) * 0.65 # Grundfläche * Stockwerke * 0.65 (Verhältnis von Bruttogrundfläche zu Wohnfläche - VDI 3807 Mittelwert aus EFH und MFH)
        self.gebaeudetyp = "EFH" if self.nutzfläche < 344 else "MFH" # Schätzwerte für Einfamilienhaus und Mehrfamilienhaus (IWU - Wert zwischen EFH und MFH in Gebäudetypologie)
        self.baujahr_class = Baujahr(self.koordinaten)
        self.baujahr = self.baujahr_class.alter
        self.heizfläche = 0.25*self.nutzfläche/0.65 if self.gebaeudetyp == "EFH" else 0.15*self.nutzfläche/0.65 # Heizfläche = 25% der Gesamtfläche für EFH, 15% der Gesamtfläche für MFH (DIN V 18599 Blatt 10)
        # U-Werte (Dach massiv, Dach Holz, Wand, Fenster, Tür) aus Baujahr_100mGrid; verwendet werden Wand und Dach (massiv)
        self.u_werte = {"Dach": self.baujahr_class.u_werte[0], "Wand": self.baujahr_class.u_werte[2]}
        self.u_wert_avg = (self.u_werte["Wand"] * self.wandfläche + self.u_werte["Dach"] * self.dachfläche) / (self.wandfläche + self.dachfläche) # Durchschnittlicher U-Wert für Wand und Dach
        self.kühlen = self.get_kühlbedarf()
        self.kühlbedarf = self.kühlen[0] # in kWh
        self.kühlbedarf_zeitreihe = self.kühlen[1] # in kWh
        self.rel_kühlbedarf = self.kühlbedarf / self.nutzfläche # Kühlbedarf pro m² Nutzfläche   
        self.max_kühlbedarf = min(self.kühlbedarf_zeitreihe) # Maximaler Kühlbedarf in der Zeitreihe
        self.heizen = self.get_heizbedarf()
        self.heizbedarf = self.heizen[0] # in kWh
        self.heizbedarf_zeitreihe = self.heizen[1] # in kWh
        self.rel_heizbedarf = self.heizbedarf / self.nutzfläche # Heizbedarf pro m² Nutzfläche   
        self.max_heizbedarf = max(self.heizbedarf_zeitreihe) # Maximaler Heizbedarf in der Zeitreihe
  
        


    
    def get_kühlbedarf(self):
        Q_tdiff = np.array(self.weather_obj.t_diff_cooling) * (self.wandfläche * self.u_werte["Wand"] + self.dachfläche * self.u_werte["Dach"]) / 1000 # in kWh
        Q_irridation = np.array(self.weather_obj.endstrahlungsenergie(self.geometrie, 0.2, 0.6)) * float(self.höhe) * 0.9 * 0.6 / 1000 
        # G-Wert nach "Energetische Bewertung von Bestandsgebäuden" von "zukunft haus" für 2-Scheiben-Wärmeschutz-Verglasung
        #  mit 0.9 für typischen Verschattungswert nach GEG §25(2) und 0.6 für typischen Glasanteil am Fenster
        Q_wasteheat = np.array(get_waste_heat(self.gebaeudetyp)) * self.heizfläche / 1000
        Q_ges = [min(a - b - c, 0) for a, b, c in zip(Q_tdiff, Q_irridation, Q_wasteheat)] # in kWh
        return abs(np.sum(Q_ges)), Q_ges # in kWh
    
    def get_heizbedarf(self):
        Q_tdiff = np.array(self.weather_obj.t_diff_heating) * (self.wandfläche * self.u_werte["Wand"] + self.dachfläche * self.u_werte["Dach"]) / 1000 # in kWh
        Q_irridation = np.array(self.weather_obj.endstrahlungsenergie(self.geometrie, 0.2, 0.6)) * float(self.höhe) * 0.6 * 0.8 / 1000
        Q_wasteheat = np.array(get_waste_heat(self.gebaeudetyp)) * self.heizfläche / 1000
        Q_hot_drinking_water = np.array(get_hot_drinking_water(self.gebaeudetyp)) * self.nutzfläche / 1000 # in kWh
        Q_ges = [max(a - b - c + d, d) for a, b, c, d in zip(Q_tdiff, Q_irridation, Q_wasteheat, Q_hot_drinking_water)] # in kWh
        return np.sum(Q_ges), Q_ges # in kWh
    
    def __str__(self):
        return f"\nAdresse: {self.adresse}\n\
Kategorie: {self.category}\n\
Baujahr: {round(float(self.baujahr))}\n\
Höhe [m]: {round(float(self.höhe))}\n\
Koordinaten [EPSG:25832]: {self.koordinaten}\n\
Grundfläche [m²]: {round(float(self.gf))}\n\
Stockwerke: {self.stockwerke}\n\
Neigung [°]: {round(float(self.neigung))}\n\
Dachfläche [m²]: {round(float(self.dachfläche))}\n\
Wandfläche [m²]: {round(float(self.wandfläche))}\n\
U-Werte [W/(m²K)]: {self.u_werte}\n\
Endkühlbedarf pro Jahr [KWh/a]: {round(float(self.kühlbedarf))}\n\
Endheizbedarf pro Jahr [KWh/a]: {round(float(self.heizbedarf))}\n\
relativer Endheizbedarf pro m² Nutzfläche und Jahr [KWh/(m²a)]: {round(float(self.rel_heizbedarf),2)}\n\
relativer Endkühlbedarf pro m² Nutzfläche und Jahr [KWh/(m²a)]: {round(float(self.rel_kühlbedarf), 2)}"


class Nichtwohngebäude:
    def __init__(self, id, koordinaten, Grundfläche, Geometrie, Stockwerke, umfang, Weather_obj, category):
        self.id = id
        self.koordinaten = koordinaten #EPSG:25832
        self.gf = Grundfläche
        self.geometrie = Geometrie
        self.umfang = umfang
        self.category = category
        self.weather_obj = Weather_obj
        self.baujahr_class = Baujahr(self.koordinaten)
        self.u_werte = self.get_u_werte(self.category)
        self.höhe_adresse_neigung = gebaeudehoehe(self.koordinaten)
        self.höhe = self.höhe_adresse_neigung[0]
        self.adresse = self.höhe_adresse_neigung[1]
        self.neigung = float(self.höhe_adresse_neigung[2]) if self.höhe_adresse_neigung[2] is not None else 0.0 # ohne Angabe in LoD2: Flachdach
        self.stockwerke = int(float(self.höhe) / 3) if np.sum(Stockwerke) == 0 else Stockwerke  # Stockwerke = Höhe / 3m
        self.dachfläche = self.gf / cos(float(self.neigung) * pi / 180) # geneigte Dachfläche = Grundfläche / cos(Neigung); Flachdach (0°) = Grundfläche
        self.wandfläche = float(self.umfang) * float(self.höhe) # Umfang * Höhe
        self.nutzfläche = self.gf * np.sum(self.stockwerke) * 0.6 # Grundfläche * Stockwerke * 0.6 (typisches Verhältnis von Nutzfläche zu Grundfläche für NWG - aus VDI 3807)
        self.baujahr = self.baujahr_class.alter
        self.u_wert_avg = (self.u_werte["Wand"] * self.wandfläche + self.u_werte["Dach"] * self.dachfläche) / (self.wandfläche + self.dachfläche) # Durchschnittlicher U-Wert für Wand und Dach
        self.kühlen = self.get_kühlbedarf()
        self.kühlbedarf = self.kühlen[0] # in kWh
        self.kühlbedarf_zeitreihe = self.kühlen[1]
        self.rel_kühlbedarf = self.kühlbedarf / self.nutzfläche # Kühlbedarf pro m² Nutzflächefläche 
        self.max_kühlbedarf = min(self.kühlbedarf_zeitreihe) # Maximaler Kühlbedarf in der Zeitreihe 
        self.heizen = self.get_heizbedarf()
        self.heizbedarf = self.heizen[0] # in kWh
        self.heizbedarf_zeitreihe = self.heizen[1]
        self.rel_heizbedarf = self.heizbedarf / self.nutzfläche # Heizbedarf pro m² Nutzflächefläche 
        self.max_heizbedarf = max(self.heizbedarf_zeitreihe) # Maximaler Heizbedarf in der Zeitreihe     

    #Klassemethoden für den Zugriff auf den Kühlbedarf ohne Instanzierung der Klasse
    @classmethod
    def get_kühlbedarf_cls(cls, u_werte, geometrie, gf, wandfläche, dachfläche, Weather_obj, category, nutzfläche, höhe):
        Q_tdiff = np.array(Weather_obj.t_diff_cooling) * ((wandfläche) * u_werte["Wand"] + dachfläche * u_werte["Dach"]) / 1000 # in kWh
        Q_irridation = np.array(Weather_obj.endstrahlungsenergie(geometrie, u_werte["Fenster_Wand"], 0.6)) * float(höhe) * 0.6 * 0.9 / 1000 # in kWh
        Q_wasteheat = np.array(get_waste_heat(category)) * nutzfläche / 1000 # in kWh
        Q_ges = [min(a - b - c, 0) for a, b, c in zip(Q_tdiff, Q_irridation, Q_wasteheat)] # in kWh
        return abs(np.sum(Q_ges)), Q_ges # in kWh
    
    # gf in konstruktor für identischen Aufbau wie in Gebaeude
    def get_kühlbedarf(self):
        Q_tdiff = np.array(self.weather_obj.t_diff_cooling) * ((self.wandfläche) * self.u_werte["Wand"] + self.dachfläche * self.u_werte["Dach"]) / 1000 # in kWh
        Q_irridation = np.array(self.weather_obj.endstrahlungsenergie(self.geometrie, self.u_werte["Fenster_Wand"], 0.6)) * float(self.höhe) * 0.6 * 0.9 / 1000 # in kWh
        Q_wasteheat = np.array(get_waste_heat(self.category)) * self.nutzfläche / 1000 # in kWh
        Q_ges = [min(a - b - c, 0) for a, b, c in zip(Q_tdiff, Q_irridation, Q_wasteheat)] # in kWh
        return abs(np.sum(Q_ges)), Q_ges # in kWh

    #Klassemethoden für den Zugriff auf den Wärmebedarf ohne Instanzierung der Klasse
    @classmethod
    def get_heizbedarf_cls(cls, u_werte, geometrie, gf, wandfläche, dachfläche, Weather_obj, category, nutzfläche, höhe):
        Q_tdiff = np.array(Weather_obj.t_diff_heating) * ((wandfläche) * u_werte["Wand"] + dachfläche * u_werte["Dach"]) / 1000 # in kWh
        Q_irridation = np.array(Weather_obj.endstrahlungsenergie(geometrie, u_werte["Fenster_Wand"], 0.6)) * float(höhe) * 0.6 * 0.9 / 1000 # in kWh
        Q_wasteheat = np.array(get_waste_heat(category)) * nutzfläche / 1000 # in kWh
        Q_hot_drinking_water = np.array(get_hot_drinking_water(category)) * nutzfläche / 1000 # in kWh
        Q_ges = [max(a - b - c + d, d) for a, b, c, d in zip(Q_tdiff, Q_irridation, Q_wasteheat, Q_hot_drinking_water)] # in kWh
        return np.sum(Q_ges), Q_ges # in kWh
    
    # gf in konstruktor für identischen Aufbau wie in Gebaeude
    def get_heizbedarf(self):
        Q_tdiff = np.array(self.weather_obj.t_diff_heating) * ((self.wandfläche) * self.u_werte["Wand"] + self.dachfläche * self.u_werte["Dach"]) / 1000 # in kWh
        Q_irridation = np.array(self.weather_obj.endstrahlungsenergie(self.geometrie, self.u_werte["Fenster_Wand"], 0.6)) * float(self.höhe) * 0.6 * 0.9 / 1000 # in kWh
        Q_wasteheat = np.array(get_waste_heat(self.category)) * self.nutzfläche / 1000 # in kWh
        Q_hot_drinking_water = np.array(get_hot_drinking_water(self.category)) * self.nutzfläche / 1000 # in kWh
        Q_ges = [max(a - b - c + d, d) for a, b, c, d in zip(Q_tdiff, Q_irridation, Q_wasteheat, Q_hot_drinking_water)] # in kWh
        return np.sum(Q_ges), Q_ges # in kWh
    
    #Klassemethoden für den Zugriff auf die U-Werte ohne Instanzierung der Klasse
    @classmethod
    def get_u_werte_cls(cls, category, coordinates):
        altersklassen = Baujahr(coordinates).altersklassen
        BAK1 = altersklassen[0] + altersklassen[1] + altersklassen[2] # vor 1978
        BAK2 = altersklassen[3] + altersklassen[4] + altersklassen[5] # 1978-2010
        BAK3 = altersklassen[6] + altersklassen[7]  # nach 2010
        U_Werte = get_u_values(category)
        U_Wert_Dach = BAK1 * U_Werte[0][0] + BAK2 * U_Werte[0][1] + BAK3 * U_Werte[0][2]
        U_Wert_Wand = BAK1 * U_Werte[1][0] + BAK2 * U_Werte[1][1] + BAK3 * U_Werte[1][2]
        return {"Dach":float(U_Wert_Dach),"Wand": float(U_Wert_Wand), "Fenster_Wand": float(U_Werte[2])}    
    
    def get_u_werte(self, category):
        altersklassen = self.baujahr_class.altersklassen
        BAK1 = altersklassen[0] + altersklassen[1] + altersklassen[2] # vor 1978
        BAK2 = altersklassen[3] + altersklassen[4] + altersklassen[5] # 1978-2010
        BAK3 = altersklassen[6] + altersklassen[7]  # nach 2010
        U_Werte = get_u_values(category)
        U_Wert_Dach = BAK1 * U_Werte[0][0] + BAK2 * U_Werte[0][1] + BAK3 * U_Werte[0][2]
        U_Wert_Wand = BAK1 * U_Werte[1][0] + BAK2 * U_Werte[1][1] + BAK3 * U_Werte[1][2]
        return {"Dach":float(U_Wert_Dach),"Wand": float(U_Wert_Wand), "Fenster_Wand": float(U_Werte[2])}

    def __str__(self):
        return f"\nNichtwohngebäude: {self.category}\n\
Adresse: {self.adresse}\n\
Baujahr: {round(self.baujahr)}\n\
Höhe [m]: {round(float(self.höhe))}\n\
Koordinaten [EPSG:25832]: {self.koordinaten}\n\
Grundfläche [m²]: {round(float(self.gf))}\n\
Stockwerke: {self.stockwerke}\n\
Neigung [°]: {round(float(self.neigung))}\n\
Dachfläche [m²]: {round(float(self.dachfläche))}\n\
Wandfläche [m²]: {round(float(self.wandfläche))}\n\
U-Werte [W/(m²K)]: {self.u_werte}\n\
Endkühlbedarf pro Jahr [KWh/a]: {round(float(self.kühlbedarf))}\n\
Endheizbedarf pro Jahr [KWh/a]: {round(float(self.heizbedarf))}\n\
relativer Endheizbedarf pro m² Nutzfläche und Jahr [KWh/(m²a)]: {round(float(self.rel_heizbedarf), 2)}\n\
relativer Endkühlbedarf pro m² Nutzfläche und Jahr [KWh/(m²a)]: {round(float(self.rel_kühlbedarf), 2)}"


#H1 = Gebaeude(1, (681536.263, 5337028.992), 100)
#print(H1)