# BuildingDemandModel

[English](README.md) | **Deutsch**

Ein Python-Werkzeug mit grafischer Oberfläche, das den **stündlichen Endenergiebedarf für Heizen und Kühlen** aller Gebäude in einem frei wählbaren Gebiet abschätzt (z. B. dem Einzugsgebiet eines Wärme-/Kältenetzes). Dafür werden offene Geodaten kombiniert:

| Eingangsdaten | Quelle | Verwendung |
|---|---|---|
| Gebäudegrundrisse und Nutzungsarten | OpenStreetMap (über `osmnx`) | Geometrie, Grundfläche, Umfang, Gebäudekategorie |
| LoD2-3D-Gebäudemodelle (Bayern) | Bayerische Vermessungsverwaltung (OpenData) | Gebäudehöhe, Dachneigung, Adresse |
| Zensus 2022 – Gebäude nach Baujahr (100-m-Gitter) | Zensus 2022 / Destatis | Baualtersverteilung → U-Werte |
| Testreferenzjahre (TRY 2015 / 2045) | Deutscher Wetterdienst (DWD) | Stündliche Außentemperatur und Solarstrahlung |
| Nichtwohngebäude-Typologie | `NWG/NWG_typologie_20250416.xlsx` | U-Werte von Nichtwohngebäuden |

Die Ergebnisse werden als Excel-Datei (Gebäudedaten, Karte, Lastgang) und als CSV-Dateien mit dem stündlichen Heiz- und Kühlbedarf (8760 h) des gesamten Gebiets ausgegeben.

> Das Modell wurde 2024–2025 im Rahmen einer studentischen Abschlussarbeit entwickelt, die von Ludwig Irrgang betreut wurde; er pflegt dieses Repository.

---

## 1. Installation

Benötigt Python ≥ 3.10 (entwickelt mit Python 3.12). `tkinter` ist in den Standard-Installern für Windows und macOS enthalten; unter Linux separat installieren (z. B. `sudo apt install python3-tk`).

```bash
git clone https://github.com/LudwigIrrgang/BuildingDemandModel.git
cd BuildingDemandModel
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Eingangsdaten herunterladen

Die großen Datensätze sind aus Größen- und Lizenzgründen **nicht** im Repository enthalten. Vor dem ersten Start herunterladen und in die folgenden Ordner legen. Jeder Ordner enthält eine kurze `README.md` mit derselben Anleitung.

### 2.1 Wetterdaten – DWD-Testreferenzjahre → `Wetterdaten/`
- Portal: <https://kunden.dwd.de/obt/index.jsp> → Beratungsleistung *„Testreferenzjahre TRY“* (kostenlose Registrierung).
- Die 1 km × 1 km-Kacheln herunterladen, die das gesamte Untersuchungsgebiet abdecken.
- Ordnerstruktur (ein Unterordner pro Kachel):
  ```
  Wetterdaten/TRY_481399115778/TRY2015_481399115778_Jahr.dat
                               TRY2015_481399115778_Somm.dat
                               TRY2015_481399115778_Wint.dat
                               TRY2045_481399115778_Jahr.dat
                               TRY2045_481399115778_Somm.dat
                               TRY2045_481399115778_Wint.dat
  ```
  Die Ziffern sind Breiten- und Längengrad × 10 000 (hier 48,1399° N, 11,5778° O). Das Programm wählt die Kachel, die der eingegebenen Adresse am nächsten liegt.

### 2.2 3D-Gebäudemodelle (LoD2) → `Gebäudehöhe/`
- Portal: <https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=lod2>
- Das Programm arbeitet mit den **2 km × 2 km-Kacheln** (CityGML). Die Dateien müssen `xxx_xxxx.gml` heißen (z. B. `690_5334.gml`, linke untere Ecke in km, EPSG:25832) und das gesamte Gebiet abdecken. Andere Dateien in diesem Ordner werden ignoriert.
- Getestet wurden nur LoD2-Daten aus Bayern.

### 2.3 Zensus 2022 – Baujahr → `Baujahr/`
- Quelle: Zensus-2022-Gitterdaten, Tabelle *„Gebäude nach Baujahr in Mikrozensus-Klassen in Gitterzellen“* (<https://www.zensus2022.de>, Bereich Ergebnisse / Gitterdaten).
- Entpacken und die CSV des **100-m-Gitters** unter genau diesem Namen ablegen:
  `Baujahr/Zensus2022_Gebaeude_nach_Baujahr_in_Mikrozensus_Klassen_100m-Gitter.csv` (semikolongetrennt, ca. 190 MB).

## 3. Bedienung

Das Programm **aus dem Repository-Ordner heraus** starten (alle Datenpfade sind relativ):

```bash
python main.py
```

1. **Adresse** und **Umkreis** in Metern eingeben. Optional die Mindestraumtemperatur im Winter (Standard 21 °C) und die Höchstraumtemperatur im Sommer (Standard 25 °C) angeben.
2. **Testreferenzjahr** wählen: 2015 oder 2045, jeweils *Normal*, *Heiß* (Sommer) oder *Kalt* (Winter).
3. Optional *„Nur Nichtwohngebäude anzeigen“* ankreuzen.
4. **„Gebäude anzeigen“** klicken. Erscheint keine Karte, liegt entweder kein Gebäudegrundriss im Gebiet oder OpenStreetMap konnte die Adresse nicht geokodieren – Programm neu starten und die Adresse variieren (z. B. mit/ohne PLZ und Ort; bewährt hat sich *„Musterstraße 1, 12345 Musterstadt“*).
5. Mit dem Mausrad zoomen, durch Ziehen verschieben. Optional ein Polygon zeichnen, um ein Teilgebiet auszuwählen: Linksklick setzt Eckpunkte, Rechtsklick schließt das Polygon.
6. **„Eigenschaften berechnen“** klicken. Je nach Gebäudeanzahl kann das dauern; alle 25 Gebäude wird eine Sicherung (`Gebäudedaten_backup.txt`) geschrieben.
7. **Gebäude korrigieren:** Klick auf ein Gebäude öffnet ein Fenster, in dem Kategorie, Höhe, Grundfläche, Stockwerke oder der absolute/spezifische Heiz- und Kühlbedarf angepasst oder das Gebäude entfernt werden kann. Dort lässt sich auch der stündliche Lastgang des Gebäudes anzeigen.
8. **Gebäude hinzufügen:** *„Gebäude hinzufügen“* ankreuzen und in die Karte klicken, um ein Platzhaltergebäude (Wohnhaus, 3 Stockwerke) einzufügen; danach Haken entfernen und das Gebäude anklicken, um die Daten anzupassen.
9. **„Daten speichern“** klicken und einen Dateinamen wählen. Erzeugt werden:
   - `<name>.xlsx` – Übersicht des Einzugsgebiets, Karte, Lastgang und Tabelle aller Gebäude
   - `<name>_heizen.csv` – stündlicher Endenergiebedarf Heizen des Gebiets [kWh/h]
   - `<name>_kühlen.csv` – stündlicher Endenergiebedarf Kühlen des Gebiets [kWh/h] (negatives Vorzeichen)

Die ursprüngliche Bedienungsanleitung mit Screenshots liegt unter [`docs/Bedienungsanleitung_20250830.pdf`](docs/Bedienungsanleitung_20250830.pdf).

## 4. Methodik (Überblick)

Für jedes Gebäude und jede Stunde des Jahres:

- **Geometrie:** Grundfläche und Umfang aus OSM; Höhe, Dachneigung und Adresse vom nächstgelegenen LoD2-Gebäude. Stockwerke = Höhe / 3 m (sofern nicht in OSM hinterlegt). Wandfläche = Umfang × Höhe; Dachfläche = Grundfläche / cos(Neigung) (Flachdach bzw. keine Neigung in LoD2: Dachfläche = Grundfläche).
- **Nutzfläche:** Grundfläche × Stockwerke × 0,65 (Wohngebäude, VDI 3807) bzw. × 0,6 (Nichtwohngebäude). Wohngebäude unter 344 m² Nutzfläche gelten als Einfamilienhaus (EFH), sonst als Mehrfamilienhaus (MFH).
- **U-Werte:** aus den Anteilen der Baualtersklassen in der Zensus-100-m-Zelle. Wohngebäude: Werte nach *Bekanntmachung BMVBS NWG Datenerfassung 2009*; Nichtwohngebäude: aus der Typologietabelle in `NWG/` (Baualtersklassen vor 1978 / 1978–2010 / nach 2010).
- **Transmission:** ΔT(t) × Σ(U·A) für Wand und Dach, ΔT aus TRY-Außentemperatur und den Raumtemperaturen.
- **Solare Gewinne:** direkte und diffuse Strahlung aus dem TRY, Sonnenstand über `pvlib`, projiziert auf die Fassadennormalen des Grundrisses, mit Annahmen zu Fensteranteil und g-Wert.
- **Interne Gewinne und Trinkwarmwasser:** Nutzungsprofile (Stunden, Wochentage, Wh/(m²·d)) je Kategorie nach DIN V 18599 bzw. Leitfäden (siehe Kommentare in `NWG/Dämmwerte_NWG.py`).
- **Heizbedarf** = max(Transmission − Solar − interne Gewinne + TWW, TWW); **Kühlbedarf** = min(Transmission − Solar − interne Gewinne, 0).

Die Ergebnisse sind eine Abschätzung für die Planung von Wärme-/Kältenetzen und ersetzen keine Gebäudesimulation.

## 5. Aufbau des Repositorys

```
main.py                      Oberfläche und Ablauf (Startpunkt)
Gebäude.py                   Klassen für Wohn- und Nichtwohngebäude (Bedarfsberechnung)
Wetter_stündlich.py          Einlesen der TRY-Daten, Temperaturdifferenzen, solare Gewinne
Strahlungswinkel.py          Stündliche Sonnenstandsvektoren (pvlib)
Berechne_normalenvektoren.py Fassadennormalen aus dem Grundrisspolygon
Baujahr_100mGrid.py          Baualtersverteilung und U-Werte Wohngebäude aus Zensusdaten
Gebaeudehoehe.py             Höhe, Dachneigung und Adresse aus LoD2-CityGML
clickable_plot.py            Interaktive Karte (Zoom, Verschieben, Polygonauswahl, Klicks)
open_building_data.py        Fenster zum Prüfen und Korrigieren eines Gebäudes
Einzugsgebiet_klasse.py      Aggregation über das Gebiet, Lastgang-Grafik
Geocode_address.py           Hilfsfunktion zur Geokodierung (von main.py nicht genutzt)
NWG/                         Nichtwohngebäude-Typologie (U-Werte, Nutzungsprofile)
docs/                        Originale Bedienungsanleitung (PDF)
Wetterdaten/ Gebäudehöhe/ Baujahr/   Eingangsdaten (herunterzuladen, siehe Abschnitt 2)
```

## 6. Änderungen gegenüber dem Originalcode

Es wurden nur minimale Korrekturen vorgenommen; abgesehen von der Dachfläche ist die Modelllogik unverändert:

- `Gebäude.py`: Die Wohngebäude-Klasse rief `Baujahr()` mit einem nicht vorgesehenen Argument auf und griff auf ein nicht existierendes Attribut (`u_wert`) zu, wodurch die Berechnung bei jedem Wohn- oder nicht klassifizierten Gebäude abbrach. Wohngebäude verwenden jetzt – analog zur Nichtwohngebäude-Klasse – den zensusbasierten U-Wert der Wand für die Wandfläche und den des (massiven) Dachs für die Dachfläche.
- `Wetter_stündlich.py`, `Gebaeudehoehe.py`: Dateien in den Datenordnern, die keine TRY-Ordner bzw. `.gml`-Kacheln sind (z. B. die `README.md`), werden übersprungen statt einen Absturz auszulösen.
- `Baujahr_100mGrid.py`: Tippfehler beim U-Wert für Holzdächer (`Z2+1.4` → `Z2*1.4`).
- Dachfläche: korrigiert von Grundfläche / sin(Neigung) auf Grundfläche / cos(Neigung). Die alte Formel überschätzte geneigte Dächer (z. B. Faktor 1,74 statt 1,22 bei 35°) und brach bei Flachdächern oder Gebäuden ohne Neigungsangabe ab; diese werden jetzt als Flachdach behandelt. Gilt auch beim Bearbeiten eines Gebäudes im Dialogfenster.
- Temporäre Dateien, Caches und Git-LFS-Verweise auf die Eingangsdaten entfernt; Dokumentation, `requirements.txt` und `.gitignore` ergänzt.

## 7. Bekannte Einschränkungen

- Die Datenpfade sind relativ – `main.py` aus dem Repository-Ordner starten.
- Die Erkennung der Kopfzeilenlänge der TRY-Dateien in `Wetter_stündlich.py` hängt vom genauen Pfadformat ab.
- Unterstützt werden nur LoD2-Daten aus Bayern (2-km-Kacheln).

## 8. Lizenz und Datenquellen

Code: [MIT-Lizenz](LICENSE), © 2025 Ludwig Irrgang.

Bei Veröffentlichung von Ergebnissen die Datenquellen angeben: © OpenStreetMap-Mitwirkende (ODbL); © Bayerische Vermessungsverwaltung (LoD2, CC BY 4.0); © Statistisches Bundesamt (Destatis), Zensus 2022; Deutscher Wetterdienst (TRY).

Fragen zum Modell bitte über die Issues dieses Repositorys.
