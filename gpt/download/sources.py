import json
from collections import UserList, UserDict



def from_geojson(filename):
    with open(filename, 'r') as fp:
        gjs = json.load(fp)
    return Sources(gjs)
    


class Sources(UserList):
    def __init__(self, geojson: dict):
        features = make_products(geojson['features'])
        super().__init__(features)



class Products(UserList):
    def __init__(self, products: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extend([Product(p) for p in products])



class Product(UserDict):
    def __init__(self, data: dict):
        super().__init__(data)


def make_products(features: list) -> list:
    return Products(features)
