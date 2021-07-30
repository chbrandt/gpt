from ._download import download_files, download_file
from . import sources


def download(URLs, filenames=None, progress_on=False, make_dirs=False):
    if isinstance(URLs, (list,tuple)):
        assert filenames is None or isinstance(filenames, (list, tuple))
        return download_files(URLs, filenames, progress_on, make_dirs)
    else:
        assert isinstance(URLs, str)
        assert filenames is None or isinstance(filenames, str)
        return download_file(URLs, filenames, progress_on, make_dirs)

def from_geojson(filename, property, to_dir='./data', to_property='download_path', to_geojson='download.geojson', 
                 make_dirs=True):
    gjson_sources = sources.from_geojson(filename)
    gjson_sources.download(property, to_property, path=to_dir, make_dirs=make_dirs)
    if to_geojson:
        gjson_sources.to_geojson(to_geojson)
    else:
        print(gjson_sources)
