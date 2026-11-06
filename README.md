# BuildingDemandModel

**English** | [Deutsch](README.de.md)

A Python tool with a graphical user interface that estimates the **hourly heating and cooling final energy demand** of all buildings in a user-defined area (e.g. the catchment area of a heating/cooling network). It combines open geodata:

| Input | Source | Used for |
|---|---|---|
| Building footprints and use types | OpenStreetMap (via `osmnx`) | Geometry, floor area, perimeter, building category |
| LoD2 3D building models (Bavaria) | Bayerische Vermessungsverwaltung (OpenData) | Building height, roof pitch, street address |
| Census 2022 – buildings by year of construction (100 m grid) | Zensus 2022 / Destatis | Construction-age distribution → U-values |
| Test reference years (TRY 2015 / 2045) | Deutscher Wetterdienst (DWD) | Hourly outdoor temperature and solar irradiance |
| Non-residential building typology | `NWG/NWG_typologie_20250416.xlsx` | U-values of non-residential buildings |

Results are exported as an Excel workbook (per-building data, map, load profile) and as CSV files with the hourly heating and cooling demand (8760 h) of the whole area.

> The model was developed in 2024–2025 as part of a student thesis supervised by Ludwig Irrgang, who maintains this repository.

---

## 1. Installation

Requires Python ≥ 3.10 (developed with Python 3.12). `tkinter` ships with the standard Python installers for Windows and macOS; on Linux install it separately (e.g. `sudo apt install python3-tk`).

```bash
git clone https://github.com/LudwigIrrgang/BuildingDemandModel.git
cd BuildingDemandModel
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Download the input data

The large data sets are **not** part of this repository (size and licence reasons). Download them before the first run and place them in the folders below. Each folder contains a short `README.md` with the same instructions.

### 2.1 Weather data – DWD test reference years → `Wetterdaten/`
- Portal: <https://kunden.dwd.de/obt/index.jsp> → service *"Testreferenzjahre TRY"* (free registration).
- Download the 1 km × 1 km tiles that cover the whole study area.
- Folder structure (one sub-folder per tile):
  ```
  Wetterdaten/TRY_481399115778/TRY2015_481399115778_Jahr.dat
                               TRY2015_481399115778_Somm.dat
                               TRY2015_481399115778_Wint.dat
                               TRY2045_481399115778_Jahr.dat
                               TRY2045_481399115778_Somm.dat
                               TRY2045_481399115778_Wint.dat
  ```
  The digits are latitude and longitude ×10 000 (here 48.1399° N, 11.5778° E). The program picks the tile closest to the entered address.

### 2.2 3D building models (LoD2) → `Gebäudehöhe/`
- Portal: <https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=lod2>
- The program works with the **2 km × 2 km tiles** (CityGML). Files must be named `xxx_xxxx.gml` (e.g. `690_5334.gml`, lower-left corner in km, EPSG:25832) and must cover the entire study area. Other files in this folder are ignored.
- Only Bavarian LoD2 data have been tested.

### 2.3 Census 2022 – year of construction → `Baujahr/`
- Source: Zensus 2022 grid data, table *"Gebäude nach Baujahr in Mikrozensus-Klassen in Gitterzellen"* (<https://www.zensus2022.de>, section results / grid data).
- Unzip and place the **100 m grid** CSV here under the exact name
  `Baujahr/Zensus2022_Gebaeude_nach_Baujahr_in_Mikrozensus_Klassen_100m-Gitter.csv` (semicolon-separated, ≈ 190 MB).

## 3. Usage

Start the program **from the repository folder** (all data paths are relative):

```bash
python main.py
```

1. Enter an **address** and a **radius** in metres. Optionally enter the minimum room temperature in winter (default 21 °C) and the maximum room temperature in summer (default 25 °C).
2. Choose the **test reference year**: 2015 or 2045, each *normal*, *hot* (summer) or *cold* (winter).
3. Optionally tick *"Nur Nichtwohngebäude anzeigen"* to show non-residential buildings only.
4. Click **"Gebäude anzeigen"** (show buildings). If no map appears, either the area contains no building footprint or OpenStreetMap could not geocode the address – restart and vary the address (e.g. with/without postcode and city; the format *"Street 1, 12345 City"* works best).
5. Zoom with the mouse wheel and pan by dragging. Optionally draw a polygon to restrict the area to a sub-area: left-click to add vertices, right-click to close the polygon.
6. Click **"Eigenschaften berechnen"** (calculate properties). Depending on the number of buildings this may take a while; a backup (`Gebäudedaten_backup.txt`) is written every 25 buildings.
7. **Correct buildings:** click on a building to open a dialog where you can change its category, height, footprint, number of storeys, or overwrite the absolute/specific heating and cooling demand, or remove the building. The dialog can also plot the building's hourly load profile.
8. **Add buildings:** tick *"Gebäude hinzufügen"* and click on the map to place a placeholder building (residential, 3 storeys); untick and click on it to adjust its data.
9. Click **"Daten speichern"** (save data) and choose a file name. Created files:
   - `<name>.xlsx` – area summary, map, load profile and table of all buildings
   - `<name>_heizen.csv` – hourly heating final energy demand of the area [kWh/h]
   - `<name>_kühlen.csv` – hourly cooling final energy demand of the area [kWh/h] (negative sign)

The original German user manual with screenshots is in [`docs/Bedienungsanleitung_20250830.pdf`](docs/Bedienungsanleitung_20250830.pdf).

## 4. Method (overview)

For every building and every hour of the year:

- **Geometry:** footprint area and perimeter from OSM; height, roof pitch and address from the nearest LoD2 building. Storeys = height / 3 m (unless tagged in OSM). Wall area = perimeter × height; roof area = footprint / cos(pitch) (flat roof or no pitch in LoD2: roof area = footprint).
- **Usable floor area:** footprint × storeys × 0.65 (residential, VDI 3807) or × 0.6 (non-residential). Residential buildings below 344 m² usable area are treated as single-family houses (EFH), otherwise as multi-family houses (MFH).
- **U-values:** from the share of construction-age classes in the census 100 m cell. Residential: values from *Bekanntmachung BMVBS NWG Datenerfassung 2009*; non-residential: from the typology table in `NWG/` (age classes before 1978 / 1978–2010 / after 2010).
- **Transmission:** ΔT(t) × Σ(U·A) for walls and roof, with ΔT from the TRY outdoor temperature and the set room temperatures.
- **Solar gains:** direct and diffuse irradiance from the TRY, sun position from `pvlib`, projected onto the façade normals of the footprint, with window share and g-value assumptions.
- **Internal gains and domestic hot water:** usage profiles (hours, days per week, Wh/(m²·d)) per building category according to DIN V 18599 / guidance documents (see comments in `NWG/Dämmwerte_NWG.py`).
- **Heating demand** = max(transmission − solar − internal gains + DHW, DHW); **cooling demand** = min(transmission − solar − internal gains, 0).

The results are a screening-level estimate for planning heating/cooling networks, not a replacement for a building energy simulation.

## 5. Repository structure

```
main.py                      GUI and workflow (entry point)
Gebäude.py                   Classes for residential and non-residential buildings (demand calculation)
Wetter_stündlich.py          Reading TRY data, temperature differences, solar gains
Strahlungswinkel.py          Hourly sun position vectors (pvlib)
Berechne_normalenvektoren.py Façade normal vectors from the footprint polygon
Baujahr_100mGrid.py          Construction-age distribution and residential U-values from census data
Gebaeudehoehe.py             Height, roof pitch and address from LoD2 CityGML
clickable_plot.py            Interactive map (zoom, pan, polygon selection, click events)
open_building_data.py        Dialog to inspect and correct a single building
Einzugsgebiet_klasse.py      Aggregation over the area, load profile plot
Geocode_address.py           Helper for geocoding (not used by main.py)
NWG/                         Non-residential typology (U-values, usage profiles)
docs/                        Original user manual (German, PDF)
Wetterdaten/ Gebäudehöhe/ Baujahr/   Input data (to be downloaded, see section 2)
```

## 6. Changes compared to the original code

Only minimal fixes were applied; apart from the roof area the model logic is unchanged:

- `Gebäude.py`: the residential class called `Baujahr()` with an argument it does not accept and accessed a non-existent attribute (`u_wert`), so the calculation crashed for every residential or unclassified building. Residential buildings now use the census-based wall U-value for walls and the (solid) roof U-value for the roof, analogous to the non-residential class.
- `Wetter_stündlich.py`, `Gebaeudehoehe.py`: files in the data folders that are not TRY folders or `.gml` tiles (e.g. the `README.md`) are skipped instead of causing a crash.
- `Baujahr_100mGrid.py`: typo in the timber-roof U-value (`Z2+1.4` → `Z2*1.4`).
- Roof area: corrected from footprint / sin(pitch) to footprint / cos(pitch). The old formula overestimated pitched roofs (e.g. ×1.74 instead of ×1.22 at 35°) and crashed for flat roofs or buildings without a pitch attribute; these are now treated as flat roofs. Also applied when editing a building in the dialog.
- Removed temporary files, caches and Git LFS pointers to the input data; added documentation, `requirements.txt` and `.gitignore`.

## 7. Known limitations

- Data paths are relative – start `main.py` from the repository folder.
- The detection of the TRY header length in `Wetter_stündlich.py` depends on the exact file path format.
- Only LoD2 data from Bavaria (2 km tiles) are supported.

## 8. Licence and data attribution

Code: [MIT licence](LICENSE), © 2025 Ludwig Irrgang.

When publishing results, cite the data sources: © OpenStreetMap contributors (ODbL); © Bayerische Vermessungsverwaltung (LoD2, CC BY 4.0); © Statistisches Bundesamt (Destatis), Zensus 2022; Deutscher Wetterdienst (TRY).

Questions about the model: please open an issue in this repository.
