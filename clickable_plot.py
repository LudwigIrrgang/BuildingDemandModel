import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from shapely.geometry import Point
from open_building_data import obj_data
import pandas as pd
from shapely.geometry import Polygon
import geopandas as gpd
import copy
from Gebäude import Gebaeude


class PlotObj:
    def __init__(self, buildings_gdf, input_address, frame_map, building_types_dict, weather_obj=None):
        self.buildings_gdf = buildings_gdf
        self.building_types = buildings_gdf['building'].unique()
        self.input_address = input_address
        self.frame_map = frame_map
        self.building_types_dict = building_types_dict
        self.weather_obj = weather_obj
        self.category_colors = {
            "nicht klassifiziert": "black",
            "Wohnhaus": "blue",
            "Verwaltung": "green",
            "Hochschule": "orange",
            "Gesundheit": "red",
            "Schule": "purple",
            "Freizeit": "yellow",
            "Sport": "cyan",
            "Industrie": "magenta",
            "Handel": "brown",
            "nicht relevant": "gray"
        }
        self.legend_handles = []  # List to store legend handles
        self.clickable = False  # Attribut, das steuert, ob die Karte anklickbar ist
        self.fig = None  # Speichere figure als Instanzvariable
        self.ax = None   # Speichere axes als Instanzvariable
        self.image_path = "Gebäudeplot.png"
        self.building_obj_dict = {}
        self.hinzufügen = False
        self.mpl_cid = None
        self.area = None  # Attribut für die Fläche des gezeichneten Polygons


    def enable_clickable(self):
        self.clickable = True



    
    def plot_map(self):
        def on_click(event):
            print("\nClick Event wurde ausgelöst")  # Debug print
            # Überprüfen, ob die Karte anklickbar ist
            if not self.clickable:
                print("Karte ist nicht anklickbar.")
                return
            click_coords = (event.xdata, event.ydata)
            print(f"Click Koordinaten: {click_coords}")  # Debug print
            if click_coords is None:
                print("Keine gültigen Koordinaten")
                return
            if not self.building_obj_dict == {}:
                self.legend_handles = []  # Leere die Legende, bevor sie neu erstellt wird
                for idx, row in self.buildings_gdf.iterrows():
                    if row['geometry'].contains(Point(click_coords)):
                        obj = self.building_obj_dict[row['id']]
                        obj = obj_data(obj)
                        
                        if obj is None:
                            del self.building_obj_dict[row['id']]
                            self.buildings_gdf = self.buildings_gdf.drop(idx)
                            del row
                        else:
                            self.buildings_gdf.loc[idx, 'building'] = obj.category
                            print(f"Aktualisiere Objekt zu: {row['building']}")
                            self.building_obj_dict[row['id']] = obj
                self.building_types = self.buildings_gdf['building'].unique()
                self.legend_handles = []
                plot(self)  # Korrigierter Aufruf
        
        
            

        def add_building_obj(event):
            x = event.xdata
            y = event.ydata
            new_coords = next(iter(self.building_obj_dict.values())).koordinaten
            coords = [(x-0.00005, y-0.00005), (x+0.00005, y-0.00005), (x+0.00005, y+0.00005), (x-0.00005, y+0.00005), (x-0.00005, y-0.00005)]
            new_geometry = Polygon(coords)
            
            new_id = len(self.building_obj_dict) + 1
            while new_id in self.buildings_gdf['id'].values:
                new_id += 1
            new_area = 22.3 * 11.1 
            new_floors = 3
            new_circumference = 2* (22.3 + 11.1)
            new_category = "Wohnhaus"

            building_obj = Gebaeude(new_id, new_coords, new_area, new_geometry, new_floors, new_circumference, self.weather_obj, new_category)
            tmp = gpd.GeoDataFrame([{
                "geometry": new_geometry,
                "building": "Wohnhaus",
                "id": new_id,
                "name": "neues Gebäude",
                "area": new_area
            }], geometry="geometry", crs="EPSG:4326")

            self.building_obj_dict[new_id] = building_obj            
            self.buildings_gdf = pd.concat([self.buildings_gdf, tmp], ignore_index=True)
            self.building_types = self.buildings_gdf['building'].unique()
            self.legend_handles = []
            plot(self)


        
        def plot(self):

            # Entferne das alte Canvas-Widget, falls es existiert
            for widget in self.frame_map.winfo_children():
                widget.destroy()
            # Plotten der Gebäude auf einer Karte mit Farbkodierung nach Typ
            self.fig, self.ax = plt.subplots(figsize=(10, 10))

            # Zuordnung der Gebäudetypen zu Kategorien
            for building_type in self.building_types:
                subset = self.buildings_gdf[self.buildings_gdf['building'] == building_type]
                if subset.empty:
                    continue
                if building_type in self.building_types_dict["nicht_klassifiziert"]:
                    category = "nicht klassifiziert"
                elif building_type in self.building_types_dict["Wohnhaus"]:
                    category = "Wohnhaus"
                elif building_type in self.building_types_dict["Verwaltung"]:
                    category = "Verwaltung"
                elif building_type in self.building_types_dict["Hochschule"]:
                    category = "Hochschule"
                elif building_type in self.building_types_dict["Gesundheit"]:
                    category = "Gesundheit"
                elif building_type in self.building_types_dict["Schule"]:
                    category = "Schule"
                elif building_type in self.building_types_dict["Freizeit"]:
                    category = "Freizeit"
                elif building_type in self.building_types_dict["Sport"]:
                    category = "Sport"
                elif building_type in self.building_types_dict["Industrie"]:
                    category = "Industrie"
                elif building_type in self.building_types_dict["Handel"]:
                    category = "Handel"
                else:
                    category = "nicht relevant"

                # Filtern der Gebäude nach Typ
                subset = self.buildings_gdf[self.buildings_gdf['building'] == building_type]
                color = self.category_colors[category]
                subset.plot(ax=self.ax, color=color, label=category, picker = True)

                # Nur einmalige Legenden-Einträge hinzufügen
                if category not in [handle.get_label() for handle in self.legend_handles]:
                    self.legend_handles.append(plt.Line2D([0], [0], color=color, lw=4, label=category))

                #for idx, row in self.buildings_gdf.iterrows():
                #    if row['geometry'].geom_type == 'Polygon':
                #        centroid = row['geometry'].centroid
                #        x, y = centroid.x, centroid.y
                #        self.ax.annotate(
                #            text=str(row["id"]),
                #            xy=(x, y),
                #            color='gray',
                #            fontsize=6,
                #            ha='center',
                #            va='center',
                #        )

            self.ax.set_title(f'Gebäude in der Nähe von {self.input_address}')

            # Erstellen einer Legende für die Farben der Gebäudetypen
            self.ax.legend(handles=self.legend_handles, title='Gebäudetypen', loc='upper right')



            # Anzeigen des Plots im GUI
            canvas = FigureCanvasTkAgg(self.fig, master=self.frame_map)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)

            # Binde das Scrollen an die Zoom-Funktion
            canvas_widget.bind("<MouseWheel>", self.zoom)

            # Binde Maus-Events für Dragging
            canvas_widget.bind("<ButtonPress-1>", self.start_pan)
            canvas_widget.bind("<B1-Motion>", self.pan_plot)
            canvas_widget.bind("<ButtonRelease-1>", self.end_pan)

            canvas.draw()
            canvas.get_tk_widget().pack()
            self.enable_clickable()  # Aktiviere Klickbarkeit
            self.fig.savefig(self.image_path)
            # Event verbinden
            if self.mpl_cid is not None:
                self.fig.canvas.mpl_disconnect(self.mpl_cid)
            if self.hinzufügen:
                self.mpl_cid = self.fig.canvas.mpl_connect('button_press_event', add_building_obj)
            else:
                self.mpl_cid = self.fig.canvas.mpl_connect('button_press_event', on_click)
            

    
        plot(self)

    def draw_area(self, area_callback=None):
        self.polygon_points = []  
        self.polygon_line = None 

        def onclick(event):
            if event.button == 1 and event.xdata and event.ydata:
                self.polygon_points.append((event.xdata, event.ydata))
                xs, ys = zip(*self.polygon_points)
                if self.polygon_line:
                    self.polygon_line.set_data(xs, ys)
                else:
                    self.polygon_line, = self.ax.plot(xs, ys, 'r-', marker='o')
                self.fig.canvas.draw_idle()
            elif event.button == 3 and len(self.polygon_points) >= 3:
                poly = Polygon(self.polygon_points)
                self.area = poly.area
                self.ax.fill(*zip(*self.polygon_points), alpha=0.2, color='red')
                self.fig.canvas.draw_idle()
                mask = self.buildings_gdf['geometry'].apply(lambda geom: geom.centroid.within(poly))
                self.buildings_gdf = self.buildings_gdf[mask].reset_index(drop=True)
                self.fig.canvas.mpl_disconnect(cid)
                self.plot_map()
                

        cid = self.fig.canvas.mpl_connect('button_press_event', onclick)

        




    def zoom(self, event):
        # Zoom-Faktor
        base_scale = 1.1
        if event.delta > 0:  # Scroll nach oben -> Vergrößern
            scale_factor = base_scale
        else:  # Scroll nach unten -> Verkleinern
            scale_factor = 1 / base_scale

        # Achsenlimits anpassen
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        new_xlim = [
            x_center - (x_center - xlim[0]) * (1/scale_factor),
            x_center + (xlim[1] - x_center) * (1/scale_factor),
        ]
        new_ylim = [
            y_center - (y_center - ylim[0]) * (1/scale_factor),
            y_center + (ylim[1] - y_center) * (1/scale_factor),
        ]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Plot aktualisieren
        self.fig.canvas.draw_idle()

        # Aktualisiere Legende
        self.ax.legend(handles=self.legend_handles, title='Gebäudetypen', loc='upper right')
        self.ax.set_title(f'Gebäude in der Nähe von {self.input_address}')
        
        # Aktualisiere Plot
        self.fig.canvas.draw_idle()

    def start_pan(self, event):
        """Speichert die Startposition der Maus beim Drücken der linken Maustaste."""
        self.pan_start = (event.x, event.y)  # Speichere die Mausposition
        self.ax_start_xlim = self.ax.get_xlim()  # Speichere die aktuellen Achsenlimits
        self.ax_start_ylim = self.ax.get_ylim()

    def pan_plot(self, event):
        """Verschiebt den Plot basierend auf der Mausbewegung."""
        if not hasattr(self, 'pan_start'):
            return  # Falls kein Startpunkt gespeichert ist, nichts tun

        # Berechne die Verschiebung
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        # Berechne die neuen Achsenlimits
        xlim = self.ax_start_xlim
        ylim = self.ax_start_ylim
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]

        new_xlim = [xlim[0] - dx * x_range / self.fig.get_size_inches()[0] / self.fig.dpi,
                    xlim[1] - dx * x_range / self.fig.get_size_inches()[0] / self.fig.dpi]
        new_ylim = [ylim[0] + dy * y_range / self.fig.get_size_inches()[1] / self.fig.dpi,
                    ylim[1] + dy * y_range / self.fig.get_size_inches()[1] / self.fig.dpi]

        # Setze die neuen Achsenlimits
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Aktualisiere den Plot
        self.fig.canvas.draw_idle()

    def end_pan(self, event):
        """Beendet das Dragging."""
        if hasattr(self, 'pan_start'):
            del self.pan_start  # Entferne den Startpunkt




