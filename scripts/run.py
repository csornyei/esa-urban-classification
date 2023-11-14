import argparse
import shutil
from pathlib import Path
from typing import List

from tqdm import tqdm
import geopandas as gpd

from etl.extract import (
    create_config,
    get_bbox_from_polygon,
    get_bbox_size,
    request_true_color_image,
)
from etl.transform import split_image_to_squares
from utils.secrets import create_client, read_secret
from utils.env import VAULT_ADDR, VAULT_TOKEN


def run(city_names: List[str]):
    folder = Path(__file__).parent.parent

    client = create_client(url=VAULT_ADDR, token=VAULT_TOKEN)

    secret = read_secret(client=client, path="data/scihub")

    config = create_config(
        client_id=secret["CLIENT_ID"],
        client_secret=secret["CLIENT_SECRET"],
    )

    footprints = gpd.read_file(folder / "footprints.geojson")

    if len(city_names) != 0:
        footprints = footprints[footprints["name"].isin(city_names)]

    for _, row in tqdm(footprints.iterrows(), total=len(footprints), desc="Cities"):
        name, geometry = row["name"], row["geometry"]

        bbox = get_bbox_from_polygon(geometry)

        size = get_bbox_size(bbox)

        data_folder = folder / "data" / name.lower() / "raw"

        print(f"Downloading data for {name}")
        request_true_color_image(
            config=config,
            bbox=bbox,
            size=size,
            data_folder=data_folder,
        )

        raw_tif_paths = data_folder.glob("**/*.tiff")

        splits_folder = folder / "data" / name.lower() / "splits"

        if splits_folder.exists():
            shutil.rmtree(splits_folder)
        splits_folder.mkdir(parents=True)

        print(f"Splitting images for {name}")
        for raw_tif_path in raw_tif_paths:
            split_image_to_squares(
                raw_tif_path,
                splits_folder,
                square_size=25,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--cities", help="Name of the cities to process separated by comma"
    )
    args = parser.parse_args()

    if args.cities:
        cities = args.cities.split(",")
        run(cities)
    else:
        run([])
