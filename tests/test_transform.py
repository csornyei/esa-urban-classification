import numpy as np
from PIL import Image

from etl.transform import _calculate_cropped_image, generate_tci_image


def test__calculate_cropped_image_crops_correctly():
    # the resulting image should be cropped correctly
    from rasterio import open as rio_open

    test_image = rio_open("tests/data/test_image.tif")
    test_crop_box = (25, 25, 75, 75)
    expected_result = test_image.read().crop(test_crop_box)
    result = _calculate_cropped_image(test_image, test_crop_box)
    np.testing.assert_array_equal(result, expected_result)


def test__calculate_cropped_image_no_intersection():
    # the resulting image should be empty

    from rasterio import open as rio_open

    test_image = rio_open("tests/data/test_image.tif")
    test_image.crs = {"init": "epsg:4326"}
    test_crop_box = (101, 101, 200, 200)
    expected_result = Image.new("RGB", (0, 0))
    result = _calculate_cropped_image(test_image, test_crop_box)
    np.testing.assert_array_equal(result, expected_result)


def test_generate_tci_image(tmpdir):
    # generate 3 .jp2 files to temp dir (red, green, blue)
    red = np.random.randint(0, 255, (100, 100)).astype("uint8")
    green = np.random.randint(0, 255, (100, 100)).astype("uint8")
    blue = np.random.randint(0, 255, (100, 100)).astype("uint8")
    Image.fromarray(red).save(tmpdir / "red.jp2")
    Image.fromarray(green).save(tmpdir / "green.jp2")
    Image.fromarray(blue).save(tmpdir / "blue.jp2")
    # generate tci image
    tci_image = generate_tci_image(tmpdir)
    # compare generated image with expected image
    expected_image = Image.merge(
        "RGB", [Image.fromarray(channel) for channel in [red, green, blue]]
    )
    np.testing.assert_array_equal(tci_image, expected_image)
