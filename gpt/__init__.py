from ._geopkg import Geopkg


def load_gpkg(filename):
    """
    Load data from geopackage in 'filename'
    """
    return Geopkg(file=filename)
    
read_file = load_gpkg
