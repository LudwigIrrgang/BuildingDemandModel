from openpyxl import load_workbook
Gebäudetypen = {
#"Beispiel" : [[Zeilen aus excel, die U-Werte enthalten], [Nutzungsbeginn, Nutzungsende, abwärmeerzeugung in Wh pro m² Nutzfläche und Tag, Wochennutzungstage](lt.:Leitfaden Energetische Gebäudebilanzierung nach DIN V 18599), [Trinkwarmwasser in Wh pro m² Nutzfläche und Tag]]   
"Verwaltung" : [[7, 25, 43], [7, 19, 73, 5],[35.1]], # Trinkwarmwasser gem. ÖNORM B 8110-5 * 2 wegen Verteilverlusten
"Hochschule" : [[8, 26, 44], [8, 19, 120, 5],[16.4]], # Trinkwarmwasser nach nPro
"Gesundheit" : [[9, 27, 45], [0, 24, 262, 7],[140.3]], # abwärme für Gesundheit nicht bekannt, daher 120 Wh/m²d von Hochschule extrapoliert auf 24h; Trinkwarmwasser gem. ÖNORM B 8110-5 * 2 wegen Verteilverlusten
"Schule" : [[10, 28, 46], [8, 15, 120, 5],[16.4]], # Trinkwarmmwasser nach nPro
"Freizeit" : [[11, 29, 47], [10, 18, 28, 5],[0]],
"Sport" : [[12, 30, 48], [8, 23, 63, 7],[16.4]], # Annahme wie Schule
"Industrie" : [[14, 32, 50], [8, 20, 108, 6],[90]], # abwärme nicht bekannt, daher gleich wie Handel, Trinkwarmwasser gem. DIN V 18599 8
"Handel" : [[15, 33, 51], [8, 20, 108, 6],[10]], # abwärme für Handel ohne Lebensmittelabteilung mit Kühlprodukten
"EFH" : [[0, 0, 0], [0, 24, 45, 7],[87.7]], # Abwärme in Einfamilienhäusern; Trinkwarmwasser HeizkostenV
"MFH" : [[0, 0, 0], [0, 24, 90, 7],[87.7]]} # Abwärme in Mehrfamilienhäusern; Trinkwarmwasser HeizkostenV


def get_waste_heat(type):
    values = Gebäudetypen[type][1]
    hourly_waste_heat = values[2]/(values[1]-values[0]) # Umrechnung von Wh/m²d auf W/m²
    yearly_course = []
    for i in range(365):
        wochentag = i % 7
        if wochentag < values[3]:
            for j in range(24):
                if j < values[0] or j > values[1]:
                    yearly_course.append(0)
                else:
                    yearly_course.append(hourly_waste_heat)
        else:
            for j in range(24):
                yearly_course.append(0)
    return yearly_course

#x = get_waste_heat("Verwaltung")
#print(x[0:24], len(x))

def get_hot_drinking_water(type):
    time_values = Gebäudetypen[type][1]
    heat_value = Gebäudetypen[type][2]  # Wh/m²d
    hourly_hot_water = float(heat_value[0])/(time_values[1]-time_values[0]) # Umrechnung von Wh/m²d auf W/m²
    yearly_course = []
    for i in range(365):
        wochentag = i % 7
        if wochentag < time_values[3]:
            for j in range(24):
                if j < time_values[0] or j > time_values[1]:
                    yearly_course.append(0)
                else:
                    yearly_course.append(hourly_hot_water)
        else:
            for j in range(24):
                yearly_course.append(0)
    return yearly_course

def get_u_values(type):
    lines = Gebäudetypen[type][0]
    
    
    # Hier wird die xlsm-Datei geöffnet und die entsprechenden Zeilen für U-Werte gelesen
    wb = load_workbook(filename="NWG/NWG_typologie_20250416.xlsx", data_only=True)
    sheet = wb["NWG_typologie"]
    u_value_roof = []
    u_value_wall = []   
    for line in lines:
        u_value_wall_opaque = sheet.cell(row=line, column=12).value
        u_value_wall_transparent = sheet.cell(row=line, column=15).value
        u_value_roof_opaque = sheet.cell(row=line, column=17).value
        u_value_roof_transparent = sheet.cell(row=line, column=20).value
        area_share_wall_opaque = 1- sheet.cell(row=line, column=14).value
        area_share_wall_transparent = sheet.cell(row=line, column=14).value
        area_share_roof_opaque = 1 - sheet.cell(row=line, column=19).value
        area_share_roof_transparent = sheet.cell(row=line, column=19).value
        u_value_roof.append(u_value_roof_opaque * area_share_roof_opaque + u_value_roof_transparent * area_share_roof_transparent)
        u_value_wall.append(u_value_wall_opaque * area_share_wall_opaque + u_value_wall_transparent * area_share_wall_transparent)
    return (u_value_roof, u_value_wall, area_share_wall_transparent)

#u1 = get_u_values("Verwaltung")
#print(u1[0])