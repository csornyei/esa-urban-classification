from pathlib import Path
from datetime import date, timedelta

from sentinelhub import (
    SHConfig,
    CRS,
    BBox,
    DataCollection,
    MimeType,
    MosaickingOrder,
    SentinelHubRequest,
    bbox_to_dimensions,
)
from shapely import Polygon


def create_config(client_id: str, client_secret: str) -> SHConfig:
    config = SHConfig()

    config.sh_client_id = client_id
    config.sh_client_secret = client_secret

    return config


def get_bbox_from_polygon(polygon: Polygon) -> BBox:
    coords = polygon.bounds
    return BBox(bbox=coords, crs=CRS.WGS84)


def get_bbox_size(bbox: BBox, resolution: int = 10) -> tuple:
    w, h = bbox_to_dimensions(bbox=bbox, resolution=resolution)
    w = min(w, 2500)
    h = min(h, 2500)
    return (w, h)


def _get_time_interval():
    end_date = date.today().replace(day=1)
    start_date = end_date - timedelta(days=30)

    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")


def request_true_color_image(
    config: SHConfig, bbox: BBox, size: tuple, data_folder: Path
) -> None:
    evalscript_tci = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04", "B08"],
                units: "DN"
            }],
            output: {
                bands: 4,
                sampleType: "INT16"
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B04, sample.B03, sample.B02, sample.B08];
    }
    """

    request = SentinelHubRequest(
        data_folder=data_folder,
        evalscript=evalscript_tci,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=_get_time_interval(),
                mosaicking_order=MosaickingOrder.LEAST_CC,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        size=size,
        config=config,
    )

    request.get_data(save_data=True)
