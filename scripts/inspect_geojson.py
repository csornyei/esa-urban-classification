import argparse
from pathlib import Path
import geopandas as gpd

parser = argparse.ArgumentParser()

parser.add_argument("-p", "--path", required=True, type=Path)

args = parser.parse_args()

file_path = args.path

geojson_file = gpd.read_file(file_path)

print(geojson_file.head())

print(geojson_file["label"].unique())
