from pathlib import Path
from sentinelsat import SentinelAPI


def init_api(scihub_username: str = "", scihub_password: str = "") -> SentinelAPI:
    if scihub_username == "" or scihub_password == "":
        raise ValueError("SCIHUB_USERNAME or SCIHUB_PASSWORD is empty")

    return SentinelAPI(
        scihub_username, scihub_password, "https://scihub.copernicus.eu/dhus"
    )


def query(
    api: SentinelAPI,
    footprint: str,
    start_date: str,
    end_date: str,
    cloudcoverpercentage: tuple = (0, 30),
) -> list:
    return api.query(
        footprint,
        date=(start_date, end_date),
        platformname="Sentinel-2",
        cloudcoverpercentage=cloudcoverpercentage,
    )


def download(api: SentinelAPI, products: list, download_dir: Path) -> None:
    for product_id in products:
        try:
            api.download(product_id, directory_path=str(download_dir))
        except Exception as e:
            print(f"Error downloading product {product_id}")
            print(e)
