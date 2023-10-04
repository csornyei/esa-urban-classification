import pandas as pd
import pytest

from etl.extract import _calculate_intersecting_products


def test__calculate_intersecting_products_no_intersecting_products():
    products_gdf = pd.DataFrame(
        {
            "geometry": [
                "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
                "POLYGON ((2 2, 3 2, 3 3, 2 3, 2 2))",
            ]
        }
    )
    # the resulting gdf should be empty
    test_case = [
        {"geometry": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"},
        {"geometry": "POLYGON ((2 2, 3 2, 3 3, 2 3, 2 2))"},
    ]  # create a test case with no intersecting products
    products_gdf = pd.DataFrame(
        {
            "geometry": [
                "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
                "POLYGON ((2 2, 3 2, 3 3, 2 3, 2 2))",
            ]
        }
    )
    result = _calculate_intersecting_products(test_case, products_gdf)
    if not result.empty:
        pytest.fail(
            "Expected result to be empty"
        )  # assert that the result is an empty dataframe


def test__calculate_intersecting_products_not_covering_whole_footprint(caplog):
    products_gdf = pd.DataFrame(
        {
            "geometry": [
                "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
                "POLYGON ((2 2, 3 2, 3 3, 2 3, 2 2))",
            ]
        }
    )
    # the resulting gdf should contains some rows
    # it should also print a warning
    # create a test case where
    # the intersecting products do not cover the whole footprint
    test_case = [
        {"geometry": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"},
        {"geometry": "POLYGON ((0.5 0.5, 1.5 0.5, 1.5 1.5, 0.5 1.5, 0.5 0.5))"},
    ]
    products_gdf = pd.DataFrame(
        {
            "geometry": [
                "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
                "POLYGON ((2 2, 3 2, 3 3, 2 3, 2 2))",
            ]
        }
    )
    result = _calculate_intersecting_products(test_case, products_gdf)
    if result.empty:
        pytest.fail(
            "Expected result to not be empty"
        )  # assert that the result is a dataframe with some rows
    if "Warning: Not all products cover the whole footprint" not in caplog.text:
        pytest.fail(
            "Expected warning to be printed"
        )  # assert that a warning is printed


def test__calculate_intersecting_products_covering_whole_footprint(caplog):
    products_gdf = pd.DataFrame(
        {
            "geometry": [
                "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
                "POLYGON ((2 2, 3 2, 3 3, 2 3, 2 2))",
            ]
        }
    )
    # the resulting gdf should contains some rows
    # it should not print a warning
    test_case = (
        ...
    )  # create a test case where the intersecting products cover the whole footprint
    products_gdf = pd.DataFrame(
        {
            "geometry": [
                "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
                "POLYGON ((2 2, 3 2, 3 3, 2 3, 2 2))",
            ]
        }
    )
    result = _calculate_intersecting_products(test_case, products_gdf)
    if result.empty:
        pytest.fail(
            "Expected result to not be empty"
        )  # assert that the result is a dataframe with some rows
    if "Warning: Not all products cover the whole footprint" in caplog.text:
        pytest.fail(
            "Expected no warning to be printed"
        )  # assert that no warning is printed
