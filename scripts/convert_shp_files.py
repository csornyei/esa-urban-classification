from pathlib import Path

import geopandas as gpd

def convert_shp_files(shp_file_path: Path):
    if shp_file_path.is_file:
        print("Converting single shapefile")
        shapefiles = [shp_file_path]
        geojson_file_names = []
        geojsons = [shp_file_path.parent / (shp_file_path.stem + ".geojson")]
    else:
        print("Converting all shapefiles in folder")
        shapefiles = [f for f in shp_file_path.glob("**/*.shp") if f.is_file()]
        geojsons = [f for f in shp_file_path.glob("**/*.geojson") if f.is_file()]
        geojson_file_names = [f.stem for f in geojsons]

    for shp in shapefiles:
        file_name = shp.stem
        if file_name in geojson_file_names:
            print(f"{file_name}.geojson already exists")
        else:
            print(f"Converting {file_name}.shp to {file_name}.geojson")
            gdf = gpd.read_file(shp)
            gdf.to_file(shp_file_path.parent /  f"{file_name}.geojson", driver="GeoJSON")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--path", help="Path to the folder containing the shapefiles or to one shapefile", type=Path)

    parser.add_argument_group("-p", "--path")
    args = parser.parse_args()

    convert_shp_files(args.path)
