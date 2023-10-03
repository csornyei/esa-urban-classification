from etl import extract  # noqa: F401


def test__calculate_intersecting_products_no_intersecting_products():
    # the resulting gdf should be empty
    pass


def test__calculate_intersecting_products_not_covering_whole_footprint():
    # the resulting gdf should contains some rows
    # it should also print a warning
    pass


def test__calculate_intersecting_products_covering_whole_footprint():
    # the resulting gdf should contains some rows
    # it should not print a warning
    pass
