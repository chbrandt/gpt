import os
import json
from collections import UserDict

from gpt.helpers import Collection
from gpt.download import download


def from_geojson(filename):
    return Sources.from_geojson(filename)


class Sources(Collection):
    def __init__(self, features, *args, **kwargs):
        super().__init__(features, *args, **kwargs)

    def download(self, url_column, file_column, path=None, make_dirs=False):
        """
        Return collection with path to downloaded file

        Input:
            - url_column : string
                Column name contains URLs to download files from.
            - file_column : string
                Column (name) to add with downloaded files path/location
        Output:
            Collection object with new meta refering to fresh downloaded files
        """
        if not path:
            path = '.'
        paths = list(self.deref(path))
        urls = list(self._get_field(url_column))
        filenames = [url.split('/')[-1] for url in urls]
        filenames = [os.path.join(path, name) for path,name in zip(paths,filenames)]
        assert len(filenames) == len(urls), "List of 'filenames' must match length of 'urls'"

        filenames = download(urls, filenames, make_dirs=make_dirs)

        return self._add_field(file_column, filenames, inplace=True)



class Products(Collection):
    def __init__(self, products: list, *args, **kwargs):
        products = [Product(p) for p in products]
        super().__init__(products, *args, **kwargs)



class Product(UserDict):
    def __init__(self, data: dict):
        super().__init__(data)


def make_products(features: list) -> list:
    return Products(features)
