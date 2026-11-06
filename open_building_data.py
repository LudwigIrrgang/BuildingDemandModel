import tkinter as tk
from tkinter import ttk
from math import pi, cos, sqrt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from Gebäude import Gebaeude, Nichtwohngebäude


# Funktion zum Speichern der Eingabe
def obj_data(obj):
    result = [obj]
    def save_data():
        # Werte aus den Eingabefeldern abrufen
        if building_type.get():
            obj.category = building_type.get()
            obj.nutzfläche = obj.gf * np.sum(obj.stockwerke) * 0.6
            obj.u_werte = Nichtwohngebäude.get_u_werte_cls(obj.category, obj.koordinaten)
            obj.u_wert_avg = (obj.u_werte["Wand"] * obj.wandfläche + obj.u_werte["Dach"] * obj.dachfläche) / (obj.wandfläche + obj.dachfläche)  # Durchschnittlicher U-Wert für Wand und Dach
            obj.heizbedarf = Nichtwohngebäude.get_heizbedarf_cls(obj.u_werte, obj.geometrie, obj.gf, obj.wandfläche, obj.dachfläche, obj.weather_obj, obj.category, obj.nutzfläche, obj.höhe)[0]
            obj.kühlbedarf = Nichtwohngebäude.get_kühlbedarf_cls(obj.u_werte, obj.geometrie, obj.gf, obj.wandfläche, obj.dachfläche, obj.weather_obj, obj.category, obj.nutzfläche, obj.höhe)[0]
            obj.rel_heizbedarf = obj.heizbedarf / obj.nutzfläche
            obj.rel_kühlbedarf = obj.kühlbedarf / obj.nutzfläche
            obj.heizbedarf_zeitreihe = Nichtwohngebäude.get_heizbedarf_cls(obj.u_werte, obj.geometrie, obj.gf, obj.wandfläche, obj.dachfläche, obj.weather_obj, obj.category, obj.nutzfläche, obj.höhe)[1]
            obj.kühlbedarf_zeitreihe = Nichtwohngebäude.get_kühlbedarf_cls(obj.u_werte, obj.geometrie, obj.gf, obj.wandfläche, obj.dachfläche, obj.weather_obj, obj.category, obj.nutzfläche, obj.höhe)[1]
            obj.max_heizbedarf = max(obj.heizbedarf_zeitreihe)  # Maximaler Heizbedarf in der Zeitreihe
            obj.max_kühlbedarf = min(obj.kühlbedarf_zeitreihe)  
            result[0] = obj
            root.quit()
            return obj
        elif height.get() or area.get() or levels.get():
            obj.höhe = float(height.get()) if height.get() else obj.höhe
            obj.umfang = obj.umfang * sqrt(float(area.get()) / obj.gf) if area.get() else obj.umfang
            obj.gf = float(area.get()) if area.get() else obj.gf
            obj.stockwerke = float(levels.get()) if levels.get() else obj.stockwerke
            obj.dachfläche = obj.gf / cos(float(obj.neigung) * pi / 180)
            obj.wandfläche = float(obj.umfang) * float(obj.höhe)
            obj.nutzfläche = obj.gf * np.sum(obj.stockwerke) * 0.65
            try:
                obj.heizen = Nichtwohngebäude.get_heizbedarf_cls(obj.u_werte, obj.geometrie, obj.gf, obj.wandfläche, obj.dachfläche, obj.weather_obj, obj.category, obj.nutzfläche, obj.höhe)
            except:
                obj.heizfläche = 0.25*obj.nutzfläche/0.65 if obj.gebaeudetyp == "EFH" else 0.15*obj.nutzfläche/0.65
                obj.heizen = obj.get_heizbedarf()
                print("test")
            obj.heizbedarf = obj.heizen[0]
            obj.heizbedarf_zeitreihe = obj.heizen[1]
            
            try:
                obj.kühlen = Nichtwohngebäude.get_kühlbedarf_cls(obj.u_werte, obj.geometrie, obj.gf, obj.wandfläche, obj.dachfläche, obj.weather_obj, obj.category, obj.nutzfläche, obj.höhe)
            except:
                obj.kühlen = obj.get_kühlbedarf()
            obj.kühlbedarf = obj.kühlen[0]
            obj.kühlbedarf_zeitreihe = obj.kühlen[1]
            obj.rel_heizbedarf = obj.heizbedarf / obj.nutzfläche
            obj.rel_kühlbedarf = obj.kühlbedarf / obj.nutzfläche
            obj.max_heizbedarf = max(obj.heizbedarf_zeitreihe)
            obj.max_kühlbedarf = min(obj.kühlbedarf_zeitreihe)
            result[0] = obj
            root.quit()
            return obj
        elif cooling_requirement.get() or heating_requirement.get():
            obj.kühlbedarf_zeitreihe = np.array(obj.kühlbedarf_zeitreihe) * (float(cooling_requirement.get())/obj.kühlbedarf) if cooling_requirement.get() else obj.kühlbedarf_zeitreihe
            obj.heizbedarf_zeitreihe = np.array(obj.heizbedarf_zeitreihe) * (float(heating_requirement.get())/obj.heizbedarf) if heating_requirement.get() else obj.heizbedarf_zeitreihe
            obj.kühlbedarf = float(cooling_requirement.get()) if cooling_requirement.get() else obj.kühlbedarf
            obj.heizbedarf = float(heating_requirement.get()) if heating_requirement.get() else obj.heizbedarf
            obj.rel_heizbedarf = obj.heizbedarf / obj.nutzfläche
            obj.rel_kühlbedarf = obj.kühlbedarf / obj.nutzfläche
            obj.max_heizbedarf = max(obj.heizbedarf_zeitreihe)
            obj.max_kühlbedarf = min(obj.kühlbedarf_zeitreihe)
            result[0] = obj
            root.quit()
            return obj
        elif heating_requirement_rel.get() or cooling_requirement_rel.get():
            obj.heizbedarf_zeitreihe = np.array(obj.heizbedarf_zeitreihe) * (float(heating_requirement_rel.get())/obj.rel_heizbedarf) if heating_requirement_rel.get() else obj.heizbedarf_zeitreihe
            obj.kühlbedarf_zeitreihe = np.array(obj.kühlbedarf_zeitreihe) * (float(cooling_requirement_rel.get())/obj.rel_kühlbedarf) if cooling_requirement_rel.get() else obj.kühlbedarf_zeitreihe
            obj.rel_kühlbedarf = float(cooling_requirement_rel.get()) if cooling_requirement_rel.get() else obj.rel_kühlbedarf
            obj.rel_heizbedarf = float(heating_requirement_rel.get()) if heating_requirement_rel.get() else obj.rel_heizbedarf
            obj.heizbedarf = obj.rel_heizbedarf * obj.nutzfläche
            obj.kühlbedarf = obj.rel_kühlbedarf * obj.nutzfläche
            obj.max_heizbedarf = max(obj.heizbedarf_zeitreihe)
            obj.max_kühlbedarf = min(obj.kühlbedarf_zeitreihe)
            result[0] = obj
            root.quit()
            return obj

    # Funktion zum Plotten des Wärmebedarfs
    def plot_heizbedarf():
        # Erstelle einen Energieplot
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(obj.heizbedarf_zeitreihe, label="Endenergiebedarf heizen (kWh)", color="red")
        ax.plot(obj.kühlbedarf_zeitreihe, label="Endenergiebedarf kühlen (kWh)", color="blue")
        ax.set_title("Stündlicher Endenergiebedarf über das Jahr")
        ax.set_xlabel("Stunden")
        ax.set_ylabel("Endenergiebedarf (kWh)")
        ax.legend()

        # Binde die Figure in das tkinter-Fenster ein
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=15, column=0, columnspan=2, padx=10, pady=10)    

    # Funktion zum Einschränken der Auswahl gleichzeitiger Eingabefelder
    def check_entries(event=None):
        if building_type.get():
            height.grid_remove()
            area.grid_remove()
            levels.grid_remove()
            cooling_requirement.grid_remove()
            heating_requirement.grid_remove()
            heating_requirement_rel.grid_remove()
            cooling_requirement_rel.grid_remove()
        elif height.get() or area.get() or levels.get():
            building_type.grid_remove()
            cooling_requirement.grid_remove()
            heating_requirement.grid_remove()
            heating_requirement_rel.grid_remove()
            cooling_requirement_rel.grid_remove()
        elif cooling_requirement.get() or heating_requirement.get():
            building_type.grid_remove()
            height.grid_remove()
            area.grid_remove()
            levels.grid_remove()
            heating_requirement_rel.grid_remove()
            cooling_requirement_rel.grid_remove()
        elif heating_requirement_rel.get() or cooling_requirement_rel.get():
            heating_requirement.grid_remove()
            building_type.grid_remove()
            height.grid_remove()
            area.grid_remove()
            levels.grid_remove()
            cooling_requirement.grid_remove()
        else:
            building_type.grid()
            height.grid()
            area.grid()
            levels.grid()
            cooling_requirement.grid()
            heating_requirement.grid()
            heating_requirement_rel.grid()
            cooling_requirement_rel.grid()

    def entferne_objekt():
        result[0] = None
        root.quit()

    # Hauptfenster erstellen
    root = tk.Tk()
    root.title(f"Building Information {obj.adresse}" if  not obj.adresse == None else "Building Information")
    root.geometry("1200x800")

    # Anzeigen der aktuellen Gebäudedaten im Hauptfenster
    tk.Label(root, text=f"Gebäudeart: {obj.category}").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    building_type = ttk.Combobox(root, values = ["Verwaltung", "Hochschule", "Gesundheit", "Schule", "Freizeit", "Sport", "Industrie", "Handel"])
    building_type.grid(row=0, column=1, padx=10, pady=10)
    building_type.bind("<KeyRelease>", check_entries)
    tk.Label(root, text=f"Baujahr: {round(obj.baujahr)}").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text=f"Höhe [m]: {round(float(obj.höhe))}").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    height = tk.Entry(root)
    height.grid(row=2, column=1, padx=10, pady=10)
    height.bind("<KeyRelease>", check_entries)

    tk.Label(root, text=f"Koordinaten [EPSG:25832]: {obj.koordinaten}").grid(row=3, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text=f"Grundfläche [m²]: {round(float(obj.gf))}").grid(row=4, column=0, padx=10, pady=10, sticky="w")
    area = tk.Entry(root)
    area.grid(row=4, column=1, padx=10, pady=10)
    area.bind("<KeyRelease>", check_entries)

    tk.Label(root, text=f"Stockwerke: {obj.stockwerke}").grid(row=5, column=0, padx=10, pady=10, sticky="w")
    levels = tk.Entry(root)
    levels.grid(row=5, column=1, padx=10, pady=10)
    levels.bind("<KeyRelease>", check_entries)

    tk.Label(root, text=f"Neigung [°]: {round(float(obj.neigung))}").grid(row=6, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text=f"Dachfläche [m²]: {round(float(obj.dachfläche))}").grid(row=7, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text=f"Wandfläche [m²]: {round(float(obj.wandfläche))}").grid(row=8, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text=f"U-Werte [W/(m²K)]: {obj.u_werte}").grid(row=9, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text=f"Endenergiebedarf pro Jahr (kühlen) [KWh/a]: {round(float(obj.kühlbedarf))}").grid(row=10, column=0, padx=10, pady=10, sticky="w")
    cooling_requirement = tk.Entry(root)
    cooling_requirement.grid(row=10, column=1, padx=10, pady=10)
    cooling_requirement.bind("<KeyRelease>", check_entries)
    
    tk.Label(root, text=f"relativer Endenergiebedarf pro m² Nutzfläche und Jahr (kühlen) [KWh/(m²a)]: {round(float(obj.rel_kühlbedarf), 2)}").grid(row=11, column=0, padx=10, pady=10, sticky="w")
    cooling_requirement_rel = tk.Entry(root)
    cooling_requirement_rel.grid(row=11, column=1, padx=10, pady=10)
    cooling_requirement_rel.bind("<KeyRelease>", check_entries)
    tk.Label(root, text=f"Maximaler Endenergiebedarf kühlen [kWh/h]: {round(float(obj.max_kühlbedarf), 2)}").grid(row=12, column=0, padx=10, pady=10, sticky="w")

    tk.Label(root, text=f"Endenergiebedarf pro Jahr (heizen) [KWh/a]: {round(float(obj.heizbedarf))}").grid(row=13, column=0, padx=10, pady=10, sticky="w")
    heating_requirement = tk.Entry(root)
    heating_requirement.grid(row=13, column=1, padx=10, pady=10)
    heating_requirement.bind("<KeyRelease>", check_entries)

    tk.Label(root, text=f"relativer Endenergiebedarf pro m² Nutzfläche und Jahr (heizen) [KWh/(m²a)]: {round(float(obj.rel_heizbedarf), 2)}").grid(row=14, column=0, padx=10, pady=10, sticky="w")
    heating_requirement_rel = tk.Entry(root)
    heating_requirement_rel.grid(row=14, column=1, padx=10, pady=10)
    heating_requirement_rel.bind("<KeyRelease>", check_entries)
    tk.Label(root, text=f"Maximaler Endenergiebedarf heizen [kWh/h]: {round(float(obj.max_heizbedarf), 2)}").grid(row=15, column=0, padx=10, pady=10, sticky="w")


    # Button zum Plotten des Wärmebedarfs
    btn_plot = tk.Button(root, text="Wärme- und Kältebedarf plotten", command=plot_heizbedarf)
    btn_plot.grid(row=16, column=0, padx=10, pady=10)
    

    # Button zum Speichern der Eingabe
    btn_save = tk.Button(root, text="Speichern", command=save_data)
    btn_save.grid(row=16, column=1, padx=10, pady=10)

    btn_plot = tk.Button(root, text="Gebäude entfernen", command=entferne_objekt)
    btn_plot.grid(row=16, column=2, padx=10, pady=10)

    # Hauptloop starten
    root.mainloop()

    root.destroy()

    return result[0]