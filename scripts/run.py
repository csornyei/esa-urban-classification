import argparse
import glob
import shutil
from pathlib import Path

from api.sentinel_api import init_api
from etl.extract import (
    download_and_unzip_files,
    gather_img_paths,
    get_available_products,
    get_intersecting_products,
)
from etl.transform import crop_image_to_footprint, generate_tci_image, merge_images


def run(geojson_files):
    folder = Path(__file__).parent.parent
    api = init_api(folder / ".env")
    important_bands = ["B02", "B03", "B04", "B08", "TCI"]

    for geojson_file in geojson_files:
        geojson_path = folder / "footprints" / f"{geojson_file}.geojson"
        if not geojson_path.exists():
            raise FileNotFoundError(
                f"{geojson_file}.geojson does not exist in the footprints directory."
            )

        products = get_available_products(api, geojson_path)
        products = get_intersecting_products(geojson_path, products)

        download_dir_path = folder / "data" / geojson_file
        if not download_dir_path.exists():
            shutil.rmtree(download_dir_path)
            download_dir_path.mkdir(parents=True)

        download_and_unzip_files(api, products, download_dir_path)
        image_paths = list(gather_img_paths(download_dir_path, important_bands))

        cropped_images_dir = download_dir_path / "cropped"
        if not cropped_images_dir.exists():
            cropped_images_dir.mkdir(parents=True)

        for band in important_bands:
            p = cropped_images_dir / band
            if not p.exists():
                p.mkdir(parents=True)

        for image_path in image_paths:
            band = image_path.stem.split("_")[-1]
            crop_image_to_footprint(
                geojson_path,
                image_path,
                cropped_images_dir
                / band
                / f"{image_path.stem}_cropped{image_path.suffix}",
            )

        for dir in cropped_images_dir.iterdir():
            merge_images(dir, cropped_images_dir / f"merged_{dir.stem}.tif")

        generate_tci_image(
            cropped_images_dir / "merged_B04.tif",
            cropped_images_dir / "merged_B03.tif",
            cropped_images_dir / "merged_B02.tif",
            cropped_images_dir / "merged_generated_tci.tif",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--geojson", help="Name of the geojson file to process")
    args = parser.parse_args()

    if args.geojson:
        run([args.geojson])
    else:
        geojson_files = [Path(f).stem for f in glob.glob("footprints/*.geojson")]
        run(geojson_files)
