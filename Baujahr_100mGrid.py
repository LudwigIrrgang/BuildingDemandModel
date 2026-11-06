import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
 
class Baujahr:

    def __init__(self, koordinaten):
        self.koordinaten = koordinaten
        self.zelle = self.get_zelle()
        self.u_werte = self.get_u_wert()
        self.alter = self.get_baujahr()
        self.altersklassen = self.altersklassen_rel()
    
    def get_zelle(self): 
        Zelle  = pd.DataFrame()
        df = pd.read_csv("Baujahr/Zensus2022_Gebaeude_nach_Baujahr_in_Mikrozensus_Klassen_100m-Gitter.csv", delimiter = ";")
        point = gpd.GeoSeries([Point(self.koordinaten[0],self.koordinaten[1])], crs="EPSG:25832")
        point = point.to_crs("EPSG:3035")
        koord_gerundet = (round(point.y.iloc[0], -2), round(point.x.iloc[0], -2))    
        i = 0
        while Zelle.empty:
            i += 1
            Zelle = df[df["GITTER_ID_100m"] == f"CRS3035RES100mN{int(koord_gerundet[0])}E{int(koord_gerundet[1])}"]
            print(f"CRS3035RES100mN{int(koord_gerundet[0])}E{int(koord_gerundet[1])}")
            koord_gerundet = (koord_gerundet[0] + 100, koord_gerundet[1])
            if i > 10:
                Zelle = df[df["GITTER_ID_100m"] == "CRS3035RES100mN2784400E4427800"] # Dummy-Wert, falls keine Zelle gefunden wird

        return Zelle
        
    def get_u_wert(self):
        Z1= pd.to_numeric(self.zelle["Vor1919"], errors='coerce').fillna(0).values[0]
        Z2 = pd.to_numeric(self.zelle["a1919bis1948"], errors='coerce').fillna(0).values[0]
        Z3 = pd.to_numeric(self.zelle["a1949bis1978"], errors='coerce').fillna(0).values[0]
        Z4 = pd.to_numeric(self.zelle["a1979bis1990"], errors='coerce').fillna(0).values[0]
        Z5 = pd.to_numeric(self.zelle["a1991bis2000"], errors='coerce').fillna(0).values[0]
        Z6 = pd.to_numeric(self.zelle["a2001bis2010"], errors='coerce').fillna(0).values[0]
        Z7 = pd.to_numeric(self.zelle["a2011bis2019"], errors='coerce').fillna(0).values[0]
        Z8 = pd.to_numeric(self.zelle["a2020undspaeter"], errors='coerce').fillna(0).values[0]
        anzahl_Gebäude = Z1+Z2+Z3+Z4+Z5+Z6+Z7+Z8
        if anzahl_Gebäude == 0:
            anzahl_Gebäude = 1
            Z4 = 1 
            # Dummy-Wert, falls Zelle existiert aber keine Gebäudedaten vorhanden sind
        # U-Werte anhand "Bekanntmachung BMVBS NWG Datenerfassung 2009"
        U_Wert_Dach_massiv = round((Z1*2.1+Z2*2.1+Z3*1.634+Z4*0.445+Z5*0.333+(Z6+Z7+Z8)*0.3)/anzahl_Gebäude, 2)
        U_Wert_Dach_holz = round((Z1*2.6+Z2*1.4+Z3*1.214+Z4*0.445+Z5*0.333+(Z6+Z7+Z8)*0.3)/anzahl_Gebäude, 2)
        U_Wert_Wand = round((Z1*1.2+Z2*1.2+Z3*1.155+Z4*0.691+Z5*0.6+Z6*0.6+Z7*0.6+Z8*0.6)/anzahl_Gebäude, 2) # massive Wand
        U_Wert_Fenster = round((Z1*2.9+Z2*2.9+Z3*2.9+Z4*2.9+Z5*1.9+Z6*1.4+Z7*1.4+Z8*1.4)/anzahl_Gebäude, 2)
        U_Wert_Tür = 3.5
        return (float(U_Wert_Dach_massiv), float(U_Wert_Dach_holz), float(U_Wert_Wand), float(U_Wert_Fenster), U_Wert_Tür)

    def get_baujahr(self):
        Z1= pd.to_numeric(self.zelle["Vor1919"], errors='coerce').fillna(0).values[0]
        Z2 = pd.to_numeric(self.zelle["a1919bis1948"], errors='coerce').fillna(0).values[0]
        Z3 = pd.to_numeric(self.zelle["a1949bis1978"], errors='coerce').fillna(0).values[0]
        Z4 = pd.to_numeric(self.zelle["a1979bis1990"], errors='coerce').fillna(0).values[0]
        Z5 = pd.to_numeric(self.zelle["a1991bis2000"], errors='coerce').fillna(0).values[0]
        Z6 = pd.to_numeric(self.zelle["a2001bis2010"], errors='coerce').fillna(0).values[0]
        Z7 = pd.to_numeric(self.zelle["a2011bis2019"], errors='coerce').fillna(0).values[0]
        Z8 = pd.to_numeric(self.zelle["a2020undspaeter"], errors='coerce').fillna(0).values[0]
        anzahl_Gebäude = Z1+Z2+Z3+Z4+Z5+Z6+Z7+Z8
        print(f"anzahl_Gebäude: {anzahl_Gebäude}")
        if anzahl_Gebäude == 0:
            anzahl_Gebäude = 1
            Z4 = 1 
            # Dummy-Wert, falls Zelle existiert aber keine Gebäudedaten vorhanden sind
        alter = (Z1*1900+Z2*1934+Z3*1964+Z4*1985+Z5*1996+Z6*2006+Z7*2015+Z8*2022)/anzahl_Gebäude
        print(f"alter: {alter}")
        return alter

    def altersklassen_rel(self):
        Z1= pd.to_numeric(self.zelle["Vor1919"], errors='coerce').fillna(0).values[0]
        Z2 = pd.to_numeric(self.zelle["a1919bis1948"], errors='coerce').fillna(0).values[0]
        Z3 = pd.to_numeric(self.zelle["a1949bis1978"], errors='coerce').fillna(0).values[0]
        Z4 = pd.to_numeric(self.zelle["a1979bis1990"], errors='coerce').fillna(0).values[0]
        Z5 = pd.to_numeric(self.zelle["a1991bis2000"], errors='coerce').fillna(0).values[0]
        Z6 = pd.to_numeric(self.zelle["a2001bis2010"], errors='coerce').fillna(0).values[0]
        Z7 = pd.to_numeric(self.zelle["a2011bis2019"], errors='coerce').fillna(0).values[0]
        Z8 = pd.to_numeric(self.zelle["a2020undspaeter"], errors='coerce').fillna(0).values[0]
        sum = Z1+Z2+Z3+Z4+Z5+Z6+Z7+Z8
        if sum == 0:
            sum = 1
            Z4 = 1 
            # Dummy-Wert, falls Zelle existiert aber keine Gebäudedaten vorhanden sind
        Z1 = Z1/sum
        Z2 = Z2/sum
        Z3 = Z3/sum
        Z4 = Z4/sum
        Z5 = Z5/sum
        Z6 = Z6/sum
        Z7 = Z7/sum
        Z8 = Z8/sum
        return (Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8)
    #a1 = Baujahr((5336658, 6800340))    
    #print(a1)