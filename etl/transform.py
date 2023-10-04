from pathlib import Path
from typing import Dict, List, Tuple

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import geometry_window
from rasterio.merge import merge
from rasterio.warp import Resampling, calculate_default_transform, reproject


def _calculate_cropped_image(
    footprint_gdf: gpd.GeoDataFrame, img_src: rasterio.io.DatasetReader
) -> Tuple[np.ndarray, Dict]:
    crs = img_src.crs
    footprint_gdf = footprint_gdf.to_crs(crs)

    footprint_geometry = footprint_gdf["geometry"]

    window = geometry_window(img_src, footprint_geometry)

    subset = img_src.read(window=window)

    profile = img_src.profile
    profile.update(
        {
            "height": subset.shape[1],
            "width": subset.shape[2],
            "transform": rasterio.windows.transform(window, img_src.transform),
        }
    )

    return subset, profile


def crop_image_to_footprint(
    footprint_path: Path, image_path: Path, output_path: Path
) -> None:
    footprint_gdf = gpd.read_file(footprint_path)

    with rasterio.open(image_path) as img_src:
        subset, profile = _calculate_cropped_image(footprint_gdf, img_src)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(subset)


def _reproject_images(dataset, dst_crs):
    transform, width, height = calculate_default_transform(
        dataset.crs, dst_crs, dataset.width, dataset.height, *dataset.bounds
    )
    reprojected_data = np.empty((dataset.count, height, width), dtype=dataset.dtypes[0])

    for i in range(1, dataset.count + 1):
        reproject(
            source=rasterio.band(dataset, i),
            destination=reprojected_data[i - 1],
            src_transform=dataset.transform,
            src_crs=dataset.crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            resampling=Resampling.nearest,
        )

    return reprojected_data, transform


def _calculate_merged_images(
    datasets: List[rasterio.io.DatasetReader], crs: rasterio.crs.CRS
) -> Tuple[np.ndarray, rasterio.Affine, Dict]:
    reprojected_data = []

    for dataset in datasets:
        if dataset.crs != crs:
            data, transform = _reproject_images(dataset, crs)
            reprojected_dataset = rasterio.MemoryFile().open(
                driver="GTiff",
                height=data.shape[1],
                width=data.shape[2],
                count=data.shape[0],
                dtype=data.dtype,
                crs=crs,
                transform=transform,
                nodata=dataset.nodata,
            )
            reprojected_dataset.write(data)
            reprojected_data.append(reprojected_dataset)
        else:
            reprojected_data.append(dataset)

    merged, out_transform = merge(reprojected_data)

    out_meta = datasets[0].meta.copy()
    out_meta.update(
        {
            "height": merged.shape[1],
            "width": merged.shape[2],
            "transform": out_transform,
        }
    )

    return merged, out_transform, out_meta


def merge_images(input_folder: Path, output_path: Path) -> None:
    try:
        datasets = [rasterio.open(f) for f in input_folder.iterdir()]
        crs = datasets[0].crs

        merged, out_transform, out_meta = _calculate_merged_images(datasets, crs)

        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(merged)
    except Exception as e:
        print(f"merge_images: {e}")
    finally:
        for dataset in datasets:
            dataset.close()


def _stretch_8bit(band: np.ndarray) -> np.ndarray:
    a = 0  # target minimum
    b = 255  # target maximum
    c = np.percentile(band, 2)  # actual minimum
    d = np.percentile(band, 98)  # actual maximum
    stretched = (band - c) * ((b - a) / (d - c)) + a
    stretched[stretched < a] = a
    stretched[stretched > b] = b
    return stretched.astype(np.uint8)


def generate_tci_image(
    red_band_path: Path, green_band_path: Path, blue_band_path: Path, output_path: Path
) -> None:
    with rasterio.open(red_band_path) as red_band:
        red = red_band.read(1)
        meta = red_band.meta
    with rasterio.open(green_band_path) as green_band:
        green = green_band.read(1)
    with rasterio.open(blue_band_path) as blue_band:
        blue = blue_band.read(1)

    red_band = _stretch_8bit(red)
    green_band = _stretch_8bit(green)
    blue_band = _stretch_8bit(blue)

    tci = np.dstack((red_band, green_band, blue_band))

    meta.update(count=3, dtype=np.uint8)

    with rasterio.open(output_path, "w", **meta) as dst:
        dst.write(tci)
