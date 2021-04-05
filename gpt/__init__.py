"""
Geo-P Tools - utilities for handling (planetary) geospatial data
"""
from pyproj import CRS
from ._geopkg import Geopkg


def load_gpkg(filename):
    """
    Load data from geopackage in 'filename'

    Input:
        filename: string: E.g, 'data.gpkg'
    Output:
        ~gpt.Geopkg instance
    """
    return Geopkg(file=filename)

read_geopackage = load_gpkg

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
