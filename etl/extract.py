import zipfile
from datetime import date, timedelta
from pathlib import Path
from typing import List

import geopandas as gpd
from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson
from shapely import wkt

from api.sentinel_api import download, query


def _get_date():
    end_date = date.today() - timedelta(days=5)
    start_date = end_date - timedelta(days=30)

    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")


def get_available_products(api: SentinelAPI, footprint_path: Path) -> list:
    footprint = geojson_to_wkt(read_geojson(footprint_path))
    start_date, end_date = _get_date()
    products = query(api, footprint, start_date, end_date, cloudcoverpercentage=(0, 50))

    if len(products) == 0:
        raise ValueError("No products found")

    products_rows = []

    for product_id, product_info in products.items():
        row = {
            "id": product_id,
            "date": product_info["beginposition"],
            "geometry": wkt.loads(product_info["footprint"]),
            "cloudcoverpercentage": product_info["cloudcoverpercentage"],
            "size": product_info["size"],
        }

        products_rows.append(row)

    products_rows = sorted(products_rows, key=lambda k: k["cloudcoverpercentage"])

    return gpd.GeoDataFrame(products_rows, geometry="geometry", crs="EPSG:4326")


def _calculate_intersecting_products(
    footprint_aoi: wkt, products_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Calculate intersecting products.

    This function calculates the intersecting products between the area of interest (AOI) and the products GeoDataFrame.

    Parameters:
    footprint_aoi (wkt): The footprint of the area of interest.
    products_gdf (gpd.GeoDataFrame): The products GeoDataFrame.

    Returns:
    gpd.GeoDataFrame: The GeoDataFrame of intersecting products.
    """
    remaining_aoi = footprint_aoi
    intersecting_products = []

    for _, product in products_gdf.iterrows():
        intersection = remaining_aoi.intersection(product["geometry"])

        if intersection.area == 0:
            continue

        remaining_aoi = remaining_aoi.difference(intersection)

        intersecting_products.append(product)

        if remaining_aoi.area == 0:
            break

    if remaining_aoi.area > 0:
        print(
            "WARNING: There are still areas of interest"
            + "that are not covered by the available products"
        )

    return gpd.GeoDataFrame(intersecting_products, crs="EPSG:4326")


def get_intersecting_products(
    footprint_path: Path, products_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Get intersecting products.

    This function gets the intersecting products between the area of interest (AOI) and the products GeoDataFrame.

    Parameters:
    footprint_path (Path): The path to the footprint of the area of interest.
    products_gdf (gpd.GeoDataFrame): The products GeoDataFrame.

    Returns:
    gpd.GeoDataFrame: The GeoDataFrame of intersecting products.
    """
    footprint = geojson_to_wkt(read_geojson(footprint_path))
    footprint_aoi = wkt.loads(footprint)
    return _calculate_intersecting_products(footprint_aoi, products_gdf)


def download_and_unzip_files(
    api: SentinelAPI, products_gdf: gpd.GeoDataFrame, download_dir: Path
) -> None:
    download(api, products_gdf["id"].tolist(), download_dir)

    zip_files = [f for f in download_dir.iterdir() if f.suffix == ".zip"]

    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(download_dir)

        zip_file.unlink()


def gather_img_paths(
    download_dir: Path, important_bands: List[str] = ["B02", "B03", "B04", "B08"]
) -> List[Path]:
    image_paths = []

    for downloaded_dir in download_dir.iterdir():
        if downloaded_dir.is_file():
            continue

        image_globs = list(downloaded_dir.glob("GRANULE/**/IMG_DATA/*.jp2"))

        for image_path in image_globs:
            if image_path.stem.split("_")[2] in important_bands:
                image_paths.append(image_path)

    return image_paths
