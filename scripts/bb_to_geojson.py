from pathlib import Path

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

geojson_file = Path(
    "/home/matecsornyei/repos/esa-urban-classification/footprints.geojson"
)

gdf = gpd.read_file(geojson_file)

get_input = True

new_rows = []

while get_input:
    next_id = int(gdf["id"].max()) + 1

    city_name = input("City name: ")

    coords = input("Coordinates (lng_1,lat_1,lng_2,lat_2): ").split(",")

    lng_1 = float(coords[0])
    lat_1 = float(coords[1])
    lng_2 = float(coords[2])
    lat_2 = float(coords[3])

    # Top left
    top_left = (lng_1, lat_1)
    # Top right
    top_right = (lng_2, lat_1)
    # Bottom right
    bottom_right = (lng_2, lat_2)
    # Bottom left
    bottom_left = (lng_1, lat_2)

    polygon = Polygon([top_left, top_right, bottom_right, bottom_left, top_left])

    new_rows.append({"id": next_id, "name": city_name, "geometry": polygon})

    get_input = input("Continue? (y/n) ") == "y"

new_gdf = gpd.GeoDataFrame(new_rows, crs=gdf.crs, geometry="geometry")

gdf = pd.concat([gdf, new_gdf])

gdf.to_file(geojson_file, driver="GeoJSON")
