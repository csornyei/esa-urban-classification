from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window


def split_image_to_squares(
    image: Path,
    output_dir: Path,
    square_size: int = 25,
) -> None:
    with rasterio.open(image) as src:
        metadata = src.meta
        transform = src.transform

        image = src.read()

        num_bands, height, width = image.shape

        x_splits = width // square_size + (1 if width % square_size > 0 else 0)
        y_splits = height // square_size + (1 if height % square_size > 0 else 0)

        metadata = {
            **metadata,
            "height": square_size,
            "width": square_size,
            "count": num_bands,
            "driver": "GTiff",
            "compress": "LZW",
        }

        for i in range(x_splits):
            for j in range(y_splits):
                window = Window(
                    i * square_size,
                    j * square_size,
                    min(square_size, width - i * square_size),
                    min(square_size, height - j * square_size),
                )

                split_image = image[
                    :,
                    window.row_off : window.row_off + window.height,
                    window.col_off : window.col_off + window.width,
                ]

                if (
                    split_image.shape[1] < square_size
                    or split_image.shape[2] < square_size
                ):
                    padding = (
                        (0, 0),
                        (0, square_size - split_image.shape[1]),
                        (0, square_size - split_image.shape[2]),
                    )
                    split_image = np.pad(split_image, padding, mode="constant")

                new_transform = rasterio.windows.transform(window, transform)

                metadata["transform"] = new_transform

                file_path = output_dir / f"{i}_{j}.tif"
                with rasterio.open(
                    file_path,
                    "w",
                    **metadata,
                ) as dst:
                    for band in range(1, num_bands + 1):
                        dst.write(split_image[band - 1, :, :], band)
