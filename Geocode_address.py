import osmnx as ox

def geocode_address(adresse):
    gdf = ox.geocode_to_gdf(adresse)
    if not gdf.empty:
        gdf = gdf.to_crs("EPSG:3035")
        point = gdf['geometry'].iloc[0].centroid
        print(f"Koordinaten: {point.x}, {point.y}")
        return (point.y, point.x)
    else:
        raise ValueError(f'Adresse "{adresse}" konnte nicht geocodiert werden.')