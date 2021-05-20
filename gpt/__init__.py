"""
Geo-P Tools - utilities for handling (planetary) geospatial data
"""
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from . import log

from pyproj import CRS
from ._geopkg import Geopkg
from ._rasterpkg import Rasterpkg
from ._gpkg import GPkg

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


def load_tiff(filename):
    """
    Load data from geotiff at 'filename'

    Input:
        filename: string: E.g, 'data.tiff'
    Output:
        ~gpt.Rasterpkg instance
    """
    return Rasterpkg(file=filename)

read_geopackage = load_gpkg
