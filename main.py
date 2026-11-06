# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 13:31:50 2024

@author: cb
"""

import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from math import isnan
import pandas as pd
from shapely.geometry import Point
import numpy as np
from Gebäude import Gebaeude, Nichtwohngebäude
from Wetter_stündlich import Wetter_normal
from Berechne_normalenvektoren import berechne_normalenvektoren
from Strahlungswinkel import strahlungswinkel
from clickable_plot import PlotObj
from Einzugsgebiet_klasse import Einzugsgebiet
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import Font


# Funktion zur Ermittlung der Koordinaten anhand einer Adresse
def geocode_address(address):
    point = ox.geocode(address)
    point = (point[1], point[0])
    gdf = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=[Point(point)])
    if not gdf.empty:
        point = gdf['geometry'].iloc[0].centroid
        print(f"Koordinaten: {point.y}, {point.x}")
        return (point.y, point.x)
    else:
        raise ValueError(f'Adresse "{address}" konnte nicht geocodiert werden.')
    

# Funktion zur Berechnung der UTM-Zone für gegebene Koordinaten
def get_utm_crs(lat, lon):
    utm_band = str((int(lon) + 180) // 6 + 1)
    if lat >= 0:
        return f"EPSG:326{utm_band.zfill(2)}"
    else:
        return f"EPSG:327{utm_band.zfill(2)}"

# Funktion zur Abfrage und Verarbeitung von Gebäudedaten
def get_buildings_near_address(address, radius):
    # Geokodiere die Adresse, um die Koordinaten zu erhalten
    lat, lon = geocode_address(address)

    # Abruf der Gebäudedaten mit OSMnx innerhalb des definierten Radius
    buildings = ox.features_from_point((lat, lon), tags={'building': True}, dist=radius)

    # Konvertiere die Gebäudedaten in eine GeoDataFrame für die weitere Verarbeitung
    buildings_gdf = gpd.GeoDataFrame(buildings, crs='EPSG:4326')  # Verwende WGS84 (EPSG:4326)
    print(f"polygon: {buildings_gdf['geometry']}")
    print(f"spalten : {buildings_gdf.columns}")
    return buildings_gdf, lat, lon

building_types_dict={"nicht_klassifiziert" : ["yes"],
                "Wohnhaus" : ["Wohnhaus", "apartments", "barracks", "bungalow", "cabin", "detached", "dormitory", "annexed", "farm", "house", "hotel", "houseboat", "residential", "semidetached_house", "terrace",],
                "Verwaltung" : ["Verwaltung", "office", "government", "public","commercial"],
                "Hochschule" : ["Hochschule", "college", "university"],
                "Gesundheit" : ["Gesundheit", "hospital", "toilets"],
                "Schule" : ["Schule", "school", "kindergarten"],
                "Freizeit" : ["Freizeit", "museum", "church", "civic", "synagogue", "castle"],
                "Sport" : ["Sport", "stadium", "sports_hall", "sports_centre"],
                "Industrie" : ["Industrie", "industrial", "warehouse"],
                "Handel" : ["Handel","supermarket", "convenience", "department_store", "retail"]
}

# Funktion zur Erstellung des GUI
def create_gui():
    def plot_buildings():
        # Abrufen der Eingaben aus den Textfeldern
        input_address = entry_address.get()
        input_radius = float(entry_radius.get()) if entry_radius.get() else float(50)
        input_temperature_summer = float(entry_temperature_summer.get()) if entry_temperature_summer.get() else 25
        input_temperature_winter = float(entry_temperature_winter.get()) if entry_temperature_winter.get() else 21
        weather_type_value = weather_type.get() if weather_type.get() else "2015 Normal"
        print(f"Adresse: {input_address}, Radius: {input_radius} m")
        # Abrufen der Gebäudedaten
        buildings_gdf, lat, lon = get_buildings_near_address(input_address, input_radius)
        buildings_gdf = buildings_gdf.to_crs("EPSG:25832")
        print(f"typen: {buildings_gdf['building']}")
        # Berechnung des stündlichen Strahlungswinkels IN MÜNCHEN
        irridation_angle = strahlungswinkel(lat, lon)
        # stündliche Temperaturdifferenz zwischen Außen- und Innentemperatur
        Weather_obj = Wetter_normal((lat, lon), input_temperature_summer, input_temperature_winter, irridation_angle, weather_type_value)
        # Gruppieren der Gebäude nach Typ für die Farbkodierung

        buildings_gdf['id'] = range(len(buildings_gdf))
        buildings_gdf = buildings_gdf[buildings_gdf.geometry.geom_type == 'Polygon']

        for building in buildings_gdf:
            # count the number of buildings of each type
            if 'building' not in buildings_gdf.columns:
                print("Keine Gebäude gefunden.")
                return

        building_counts = buildings_gdf['building'].value_counts()
        print("Anzahl der Gebäude nach Typ:")
        print(f"Anzahl der Gebäude: {len(buildings_gdf)}")
        for building_type, count in building_counts.items():
            print(f"{building_type}: {count}")

        if keine_Wohngebäude.get():
            print("Nur Nichtwohngebäude anzeigen")
            # Filtere die Gebäude, um nur Nichtwohngebäude anzuzeigen
            buildings_gdf = buildings_gdf[buildings_gdf['building'].isin(building_types_dict["nicht_klassifiziert"]) | 
                                          buildings_gdf['building'].isin(building_types_dict["Verwaltung"]) | 
                                          buildings_gdf['building'].isin(building_types_dict["Hochschule"]) | 
                                          buildings_gdf['building'].isin(building_types_dict["Gesundheit"]) | 
                                          buildings_gdf['building'].isin(building_types_dict["Schule"]) | 
                                          buildings_gdf['building'].isin(building_types_dict["Freizeit"]) | 
                                          buildings_gdf['building'].isin(building_types_dict["Sport"]) | 
                                          buildings_gdf['building'].isin(building_types_dict["Industrie"])
                                          | buildings_gdf['building'].isin(building_types_dict["Handel"])]



        # Plot erzeugen:
        Plot_obj = PlotObj(buildings_gdf, input_address, frame_map, building_types_dict, Weather_obj)
        Plot_obj.plot_map()
        
        
        Plot_obj.draw_area()






        

        def calculate_properties():

            gdf = Plot_obj.buildings_gdf.to_crs("EPSG:25832")
            y_wert = gdf.geometry.centroid.y.mean()
            print(y_wert)
            x_wert = gdf.geometry.centroid.x.mean()
            print(x_wert)
            utm_crs = get_utm_crs(lat, lon)

            gdf = gdf.to_crs(utm_crs)

            # Extrahiere benötigte Informationen und berechne die Fläche in Quadratmetern
            result_df = gdf[['building', 'geometry']].copy()
            result_df['area_m2'] = result_df['geometry'].area
            result_df['circumference_m'] = result_df['geometry'].length
            # Gebaeudemittelpunkt in EPSG:25832
            result_df['centroid'] = result_df['geometry'].centroid
            gdf['building:levels'] = gdf['building:levels'].fillna(0) if 'building:levels' in gdf.columns else 0
            gdf['roof:levels'] = gdf['roof:levels'].fillna(0) if 'roof:levels' in gdf.columns else 0

            result_df['levels'] = list(zip(gdf['building:levels'].astype(int), gdf['roof:levels'].astype(int)))

            result_df['type'] = gdf['building']

            result_df['id'] = gdf['id']

            building_list = {}

            # Sicherung für lange Laufzeiten
            def sichere_dict(daten):
                with open("Gebäudedaten_backup.txt", "w") as f:
                    for key, obj in daten.items():
                        f.write(f'ID {obj.id}: "Typ" {obj.category}, "Adresse" {obj.adresse}, "Baujahr" {round(float(obj.baujahr))}, "Grundläche" {round(float(obj.gf))}, "Nutzfläche" {round(float(obj.nutzfläche))}, "Höhe" {round(float(obj.höhe),1)}, "Stockwerke" {str(obj.stockwerke)}, "Endenergiebedarf heizen" {round(float(obj.heizbedarf))}, "relativer Endenergiebedarf heizen pro m² Nutzfläche" {round(float(obj.rel_heizbedarf),1)}, "maximaler Heizbedarf" {round(float(obj.max_heizbedarf),1)}, "Endenergiebedarf kühlen" {round(float(obj.kühlbedarf))}, "relativer Endenergiebedarf kühlen pro m² Nutzfläche" {round(float(obj.rel_kühlbedarf),1)}, "maximaler Kühlbedarf" {round(float(obj.max_kühlbedarf),1)}\n')
                        
            for obj in result_df.iloc:
                if obj['type'] in building_types_dict["nicht_klassifiziert"]:
                    category = "nicht klassifiziert"
                elif obj['type'] in building_types_dict["Wohnhaus"]:
                    category = "Wohnhaus"
                elif obj['type'] in building_types_dict["Verwaltung"]:
                    category = "Verwaltung"
                elif obj['type'] in building_types_dict["Hochschule"]:
                    category = "Hochschule"
                elif obj['type'] in building_types_dict["Gesundheit"]:
                    category = "Gesundheit"
                elif obj['type'] in building_types_dict["Schule"]:
                    category = "Schule"
                elif obj['type'] in building_types_dict["Freizeit"]:
                    category = "Freizeit"
                elif obj['type'] in building_types_dict["Sport"]:
                    category = "Sport"
                elif obj['type'] in building_types_dict["Industrie"]:
                    category = "Industrie"
                elif obj['type'] in building_types_dict["Handel"]:
                    category = "Handel"
                else:
                    category = "nicht relevant"
                    continue
                id = int(obj['id'])
                koord = (obj.centroid.x, obj.centroid.y)
                flaeche = float(obj.area_m2)
                Stockwerke = obj['levels']
                print(f"Stockwerke: {Stockwerke}")
                umfang = float(obj['circumference_m'])
                geometrie = obj.geometry

                print(koord, flaeche, Stockwerke, umfang)
                if category == "Wohnhaus":
                    building_list[id] = Gebaeude(id, koord, flaeche, geometrie, Stockwerke, umfang, Weather_obj, category)
                elif category == "nicht klassifiziert":
                    building_list[id] = Gebaeude(id, koord, flaeche, geometrie, Stockwerke, umfang, Weather_obj, category)
                else:
                    building_list[id] = Nichtwohngebäude(id, koord, flaeche, geometrie, Stockwerke, umfang, Weather_obj, category)
                if len(building_list) % 25 == 0:
                    sichere_dict(building_list)
            
            # Plot wird anklickbar und erlaubt korrektur der errechnenten Gebäudedaten. Korrekturen werden in Objekten in building_list gespeichert
            Plot_obj.building_obj_dict = building_list
            Plot_obj.enable_clickable()
            building_list = Plot_obj.building_obj_dict


            
            

            def save_data():
                # Speichern der Ergebnisse in einer Excel-Datei
                save_path = filedialog.asksaveasfilename(defaultextension='.xlsx',
                                                         filetypes=[('Excel Dateien', '*.xlsx'), ('Alle Dateien', '*.*')])
                if Plot_obj.area is None:
                    area = (input_radius* 2) ** 2
                else:
                    area = Plot_obj.area
                EZG = Einzugsgebiet(input_address, area, building_list)
                if save_path:
                    csv_path_heating = save_path.replace('.xlsx', '_heizen.csv')
                    csv_path_cooling = save_path.replace('.xlsx', '_kühlen.csv')
                    # Umwandlung des Arrays in einen DataFrame
                    df_heizen = pd.DataFrame(EZG.endenergie_heizen[0], columns=["Heizenergie"])
                    df_kuehlen = pd.DataFrame(EZG.endenergie_kühlen[0], columns=["Kühlenergie"])

                    # Speichern als CSV
                    df_heizen.to_csv(csv_path_heating, index=False)
                    df_kuehlen.to_csv(csv_path_cooling, index=False)

                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Gebäudedaten"
                    ws.append(["Gebäudedaten und Endenergiebedarf des Einzugsgebietes"])
                    ws["A1"].font = Font(size=14, bold=True)
                    ws.append([""])
                    ws.append([""]) 
                    ws.append(["Einzugsgebiet:"])
                    ws["A4"].font = Font(bold=True)
                    ws.append(["Name", "Fläche", "Anzahl Gebäude gesamt", "Anzahl Wohngebäude", "Anzahl Nichtwohngebäude", "Jährlicher Endenergiebedarf heizen", "Maximalbedarf heizen", "Jährlicher Endenergiebedarf kühlen", "Maximalbedarf kühlen"])
                    ws.append(["", "[m²]", "", "", "", "[kWh/a]", "[kWh/h]", "[kWh/a]", "[kWh/h]"])
                    ws.append([EZG.name, EZG.fläche, EZG.anzahl_gebäude, EZG.anzahl_WG, EZG.anzahl_NWG, round(float(EZG.jährlicher_heiz_endenergiebedarf)), round(float(EZG.max_heizenergie),1), round(float(EZG.jährlicher_kühl_endenergiebedarf)), round(float(EZG.max_kühlenergie),1)])                   
                    ws.append([""])
                    img1 = Image(EZG.image_path)
                    img1.width = img1.width * (30/24)
                    img1.height = img1.height * (30/24)
                    ws.add_image(img1, "L9") # Endenergiebedarf Verlauf
                    img2 = Image(Plot_obj.image_path)
                    img2.width = img2.width * (30/50)
                    img2.height = img2.height * (30/50)
                    ws.add_image(img2, "A9") # Kartendarstellung
                    ws.row_dimensions[9].height = 450
                    ws.append([""])
                    ws.append([""])
                    ws.append([""])
                    ws.append(["Gebäudeinformationen"])
                    ws["A12"].font = Font(bold=True)
                    ws.append(["ID", "lattitude", "longitude", "Typ", "Adresse", "Baujahr", "Grundläche", "Nutzfläche", "Höhe", "Stockwerke", "U-Wert Gebäudehülle", "Endenergiebedarf heizen", "relativer Endenergiebedarf heizen pro m² Nutzfläche", "maximaler Endenergiebedarf heizen", "Endenergiebedarf kühlen", "relativer Endenergiebedarf kühlen pro m² Nutzfläche", "maximaler Endenergiebedarf kühlen"])
                    ws.append(["","EPSG:25832", "EPSG:25832", "", "", "", "[m²]", "[m²]", "[m]", "", "[W/(m²K)]", "[kWh/a]", "[kWh/(m²a)]", "[kWh/h]", "[kWh/a]", "[kWh/(m²a)]", "[kWh/h]"])
                    result_df.to_excel(save_path, index=False)
                    tk.Label(root, text=f'Die Ergebnisse wurden unter {save_path} gespeichert.', fg='green').pack()
                    for G in building_list:
                        gebäude = building_list[G]
                        ws.append([gebäude.id, gebäude.koordinaten[1], gebäude.koordinaten[0], gebäude.category, gebäude.adresse, round(float(gebäude.baujahr)), round(float(gebäude.gf)), round(float(gebäude.nutzfläche)), round(float(gebäude.höhe),1), str(gebäude.stockwerke), round(float(gebäude.u_wert_avg),3), round(float(gebäude.heizbedarf)), round(float(gebäude.rel_heizbedarf),1), round(float(gebäude.max_heizbedarf),1), round(float(gebäude.kühlbedarf)), round(float(gebäude.rel_kühlbedarf),1), round(float(gebäude.max_kühlbedarf),1)])
                    wb.save(save_path)

            # Button zum Speichern der Daten (zunächst deaktiviert)
            btn_save = tk.Button(frame_inputs, text='Daten speichern', command=save_data, state=tk.DISABLED)
            btn_save.grid(row=7, columnspan=2, padx=5, pady=10)
            btn_save.config(state=tk.NORMAL, command=save_data)

            # BooleanVar für den Zustand der Checkbox
            add_building_var = tk.BooleanVar(value=False)  # Standardmäßig nicht angekreuzt

            # Callback-Funktion für die Checkbox
            def toggle_add_building():
                Plot_obj.hinzufügen = add_building_var.get()
                print(f"Gebäude hinzufügen: {Plot_obj.hinzufügen}")
                Plot_obj.plot_map()  # Plot sofort neu aufbauen!

            # Checkbox erstellen und mit der BooleanVar und der Callback-Funktion verknüpfen
            check_button = tk.Checkbutton(
                frame_inputs,
                text="Gebäude hinzufügen",
                variable=add_building_var,  # Verknüpfe die Checkbox mit der BooleanVar
                command=toggle_add_building  # Rufe die Callback-Funktion auf, wenn der Zustand sich ändert
            )
            check_button.grid(row=8, columnspan=2, padx=5, pady=10)


        # Button zum Berechnen der Gebäudeeigenschaften (zunächst deaktiviert)
        btn_calculate = tk.Button(frame_inputs, text='Eigenschaften berechnen', command=calculate_properties, state=tk.DISABLED)
        btn_calculate.grid(row=6, columnspan=2, padx=5, pady=10)
        btn_calculate.config(state=tk.NORMAL)

    # GUI erstellen
    root = tk.Tk()
    root.title('Gebäude Visualisierung und Speicherung')

    # Rahmen für Eingabefelder und Plot
    frame_inputs = tk.Frame(root)
    frame_inputs.pack(pady=10)

    frame_map = tk.Frame(root)
    frame_map.pack()

    # Eingabefelder für Adresse und Radius
    tk.Label(frame_inputs, text='Adresse*:').grid(row=0, column=0, padx=5, pady=5)
    entry_address = tk.Entry(frame_inputs, width=50)
    entry_address.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text='Umkreis (in Metern)*:').grid(row=1, column=0, padx=5, pady=5)
    entry_radius = tk.Entry(frame_inputs)
    entry_radius.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text='Raumtemperatur Winter (optional):').grid(row=2, column=0, padx=5, pady=5)
    entry_temperature_winter = tk.Entry(frame_inputs)
    entry_temperature_winter.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text='Raumtemperatur Sommer (optional):').grid(row=3, column=0, padx=5, pady=5)
    entry_temperature_summer = tk.Entry(frame_inputs)
    entry_temperature_summer.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text='Art des Jahrestemperaturverlaufs*').grid(row=4, column=0, padx=10, pady=10)
    weather_type = ttk.Combobox(frame_inputs, values = ["2015 Normal", "2015 Heiß", "2015 Kalt", "2045 Normal", "2045 Heiß", "2045 Kalt"])
    weather_type.grid(row=4, column=1, padx=10, pady=10)

    keine_Wohngebäude = tk.BooleanVar(value=False)
    tk.Checkbutton(frame_inputs, text = "Nur Nichtwohngebäude anzeigen", variable = keine_Wohngebäude).grid(row=5, column=0, padx=10, pady=10)


    # Button zum Plotten der Gebäude
    btn_plot = tk.Button(frame_inputs, text='Gebäude anzeigen', command=plot_buildings)
    btn_plot.grid(row=6, columnspan=2, padx=5, pady=10)

    

    

    # Starten des GUI-Loops
    root.mainloop()

# Aufrufen der Funktion zur Erstellung des GUI
create_gui()