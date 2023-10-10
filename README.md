# ESA Urban Classification Project

In this project my goal is to classify some European metropolitan area as "urban", "nature" and "water" and compare how these areas changes over time in different metropolitan areas.

The data used in this project is the Sentinel 2 satellite images from the [Copernicus Open Access Hub](https://scihub.copernicus.eu/).

The metropolitan areas that I will focus on in this project are:
- Amsterdam
- Athens
- Barcelona
- Berlin
- Milan
- Paris
- Prague
- Rome
- Rotterdam
- Vienna
- Zurich

## Dependencies

I use `poetry` to manage the dependencies of this project.

The main dependecies are:
- `numpy`
- `geopandas`
- `rasterio`
- `sentinelsat`

## Data collection

I downloaded the data from the [Copernicus Open Access Hub](https://scihub.copernicus.eu/) using the [Sentinelsat](https://sentinelsat.readthedocs.io/en/stable/) package. As I want to run the script from time to time to compare the changes the script download the images from the last 30 days. 

For collecting the images I've separated my scripts into `extract.py` and `transform.py` files. `extract` is responsible for downloading the correct images and unzipping them. `transform` is responsible for cropping and merging the images to correctly cover the footprint of the metropolitan areas.

### Running

There is one run script to download satellite images for a footprint. It expects a geojson file's name and the geojson file needs to be in the *footprints* folder. If not filename was provided it will download the images for all the footprints.

```bash
    python -m scripts.run -g <geojson_filename>
```

### Challenges

Initially I wanted to include some other cities like Budapest and Warsaw. Unfortunately as they are close to their UTM zone's border some images are taken with different geometry. This made it really hard to merge and I decieded that this is not my current goal to solve so I had to remove these cities from my list.