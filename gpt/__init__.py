from .geopkg import Geopkg


def read_gpkg(filename):
    """
    Return Geopkg from geopackage 'filename'
    """
    return Geopkg(file=filename)

load_geopackage = read_gpkg
