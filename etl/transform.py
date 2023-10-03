import rasterio
import numpy as np
import geopandas as gpd

from pathlib import Path
from rasterio.merge import merge
from rasterio.features import geometry_window

def crop_image_to_footprint(
    footprint_path: str,
    image_path: str,
    output_path: str
) -> None:
    
    footprint_gdf = gpd.read_file(footprint_path)
    
    with rasterio.open(image_path) as img_src:
        crs = img_src.crs
        footprint_gdf = footprint_gdf.to_crs(crs)
        
        footprint_geometry = footprint_gdf['geometry'].iloc[0]
        
        window = geometry_window(img_src, footprint_geometry)
        
        subset = img_src.read(window=window)
        
        profile = img_src.profile
        profile.update({
            'height': subset.shape[1],
            'width': subset.shape[2],
            'transform': rasterio.windows.transform(window, img_src.transform)
        })
        
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(subset)
        

def merge_images(
    input_folder: str,
    output_path: str
) -> None:
    try:
        datasets = [rasterio.open(f) for f in Path(input_folder).iterdir()]
        crs = datasets[0].crs
        
        for dataset in datasets:
            if dataset.crs != crs:
                raise ValueError("CRS of all datasets must be the same")
        
        merged, out_transform = merge(datasets)
        
        out_meta = datasets[0].meta.copy()
        out_meta.update({
            "height": merged.shape[1],
            "width": merged.shape[2],
            "transform": out_transform
        })
        
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(merged)
    except Exception as e:
        print(e)
    finally:
        for dataset in datasets:
            dataset.close()


def generate_tci_image(
    red_band_path: str,
    green_band_path: str,
    blue_band_path: str,
    output_path: str
) -> None:
    with rasterio.open(red_band_path) as red_band:
        red = red_band.read(1)
        meta = red_band.meta
    with rasterio.open(green_band_path) as green_band:
        green = green_band.read(1)
    with rasterio.open(blue_band_path) as blue_band:
        blue = blue_band.read(1)
        
    red_band = ((red / 65535) * 255).astype(np.uint8)
    green_band = ((green / 65535) * 255).astype(np.uint8)
    blue_band = ((blue / 65535) * 255).astype(np.uint8)
    
    tci = np.dstack((red_band, green_band, blue_band))
    
    meta.update(count=3, dtype=np.uint8)
    
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(tci.transpose(2, 0, 1))
