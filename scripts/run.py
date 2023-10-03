from pathlib import Path

from api.sentinel_api import init_api
from etl.extract import (
    get_available_products, 
    get_intersecting_products, 
    download_and_unzip_files, 
    gather_img_paths
)
from etl.transform import (
    crop_image_to_footprint,
    merge_images,
    generate_tci_image
)

folder = Path(__file__).parent.parent

api = init_api(folder / ".env")

budapest_footprint = folder / "footprints" / "budapest.geojson"

products = get_available_products(api, budapest_footprint)

products = get_intersecting_products(budapest_footprint, products)

download_dir_path = folder / "data" / "budapest"

if not download_dir_path.exists():
    download_dir_path.mkdir(parents=True)

download_and_unzip_files(api, products, download_dir_path)

important_bands = ['B02', 'B03', 'B04', 'B08', 'TCI']

image_paths = list(gather_img_paths(download_dir_path, important_bands))

cropped_images_dir = folder / "data" / "budapest" / "cropped"

if not cropped_images_dir.exists():
    cropped_images_dir.mkdir(parents=True)

for band in important_bands:
    p = cropped_images_dir / band
    if not p.exists():
        p.mkdir(parents=True)

for image_path in image_paths:
    band = image_path.stem.split("_")[-1]
    crop_image_to_footprint(
        budapest_footprint, 
        image_path, 
        cropped_images_dir / band / f"{image_path.stem}_cropped{image_path.suffix}"
    )

for dir in cropped_images_dir.iterdir():
    print(dir)
    merge_images(dir, cropped_images_dir / f"merged_{dir.stem}.tif")
    
generate_tci_image(
    cropped_images_dir / "merged_B04.tif",
    cropped_images_dir / "merged_B03.tif",
    cropped_images_dir / "merged_B02.tif",
    cropped_images_dir / "merged_generated_tci.tif"
)
