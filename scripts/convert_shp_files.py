from pathlib import Path

import geopandas as gpd

footprints_path = Path(__file__).parent.parent / "footprints"

shapefiles = [f for f in footprints_path.glob("**/*.shp") if f.is_file()]

geojsons = [f for f in footprints_path.glob("**/*.geojson") if f.is_file()]

geojson_file_names = [f.stem for f in geojsons]

for shp in shapefiles:
    file_name = shp.stem
    if file_name in geojson_file_names:
        print(f"{file_name}.geojson already exists")
    else:
        print(f"Converting {file_name}.shp to {file_name}.geojson")
        gdf = gpd.read_file(shp)
        gdf.to_file(footprints_path / f"{file_name}.geojson", driver="GeoJSON")
