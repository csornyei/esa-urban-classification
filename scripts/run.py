import argparse
import glob
import shutil
import tqdm
from pathlib import Path
from typing import List

from api.sentinel_api import init_api
from api.secrets import create_client, read_secret
from etl.extract import (
    download_and_unzip_files,
    gather_img_paths,
    get_available_products,
    get_intersecting_products,
)
from etl.transform import (
    crop_image_to_footprint,
    crop_image_with_window,
    merge_images,
    generate_tci_image,
)
from utils.env import VAULT_ADDR, VAULT_TOKEN


def run(geojson_files: List[str], generate_tci: bool):
    folder = Path(__file__).parent.parent

    client = create_client(url=VAULT_ADDR, token=VAULT_TOKEN)

    secret = read_secret(client=client, path="data/scihub")

    api = init_api(secret["USERNAME"], secret["PASSWORD"])

    important_bands = ["B02", "B03", "B04", "B08", "TCI"]

    for geojson_file in geojson_files:
        try:
            print(f"Processing {geojson_file}.geojson")
            geojson_path = folder / "footprints" / f"{geojson_file}.geojson"
            if not geojson_path.exists():
                raise FileNotFoundError(
                    f"{geojson_file}.geojson does not exist in the footprints directory."
                )

            products = get_available_products(api, geojson_path)
            products = get_intersecting_products(geojson_path, products)

            download_dir_path = folder / "data" / geojson_file / "raw"
            if download_dir_path.exists():
                shutil.rmtree(download_dir_path)
            download_dir_path.mkdir(parents=True)

            download_and_unzip_files(api, products, download_dir_path)
            image_paths_by_prod_id = gather_img_paths(
                download_dir_path, important_bands
            )

            # create folders for cropped results
            cropped_images_dir = download_dir_path / "cropped"
            if not cropped_images_dir.exists():
                cropped_images_dir.mkdir(parents=True)

            for band in important_bands:
                p = cropped_images_dir / band
                if not p.exists():
                    p.mkdir(parents=True)

            for project, content in tqdm.tqdm(
                image_paths_by_prod_id.items(), desc="Cropping images", position=0
            ):
                window = None
                for band, image_path in tqdm.tqdm(
                    content.items(), desc=f"Project {project}", position=1, leave=False
                ):
                    if window is None:
                        window = crop_image_to_footprint(
                            geojson_path,
                            image_path,
                            cropped_images_dir
                            / band
                            / f"{image_path.stem}_cropped{image_path.suffix}",
                        )
                    else:
                        crop_image_with_window(
                            window,
                            image_path,
                            cropped_images_dir
                            / band
                            / f"{image_path.stem}_cropped{image_path.suffix}",
                        )

            # create folder for merged results
            merged_images_dir = download_dir_path / "merged"
            if not merged_images_dir.exists():
                merged_images_dir.mkdir(parents=True)

            for dir in cropped_images_dir.iterdir():
                merge_images(dir, merged_images_dir / f"merged_{dir.stem}.tif")

            if generate_tci:
                print("Generating TCI image")
                generate_tci_image(
                    cropped_images_dir / "merged_B04.tif",
                    cropped_images_dir / "merged_B03.tif",
                    cropped_images_dir / "merged_B02.tif",
                    cropped_images_dir / "merged_generated_tci.tif",
                )

            # move everything to results folder
            results_dir_path = folder / "data" / geojson_file / "results"
            if results_dir_path.exists():
                shutil.rmtree(results_dir_path)
            results_dir_path.mkdir(parents=True)

            for file in merged_images_dir.iterdir():
                shutil.move(file, results_dir_path)

            # clean up data folder
            shutil.rmtree(download_dir_path)

        except Exception as e:
            if len(geojson_files) == 1:
                raise Exception(f"Error processing {geojson_file}.geojson") from e
            else:
                print(e)
                print(f"Error processing {geojson_file}.geojson")
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--geojson", help="Name of the geojson file to process")
    parser.add_argument("--tci", help="Generate TCI image", action="store_true")
    args = parser.parse_args()

    if args.geojson:
        run([args.geojson], args.tci)
    else:
        geojson_files = [Path(f).stem for f in glob.glob("footprints/*.geojson")]
        run(geojson_files, args.tci)
