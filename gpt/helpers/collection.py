import json
import geopandas as gpd
from collections import UserList



def from_geojson(filename):
    return Collection.from_geojson(filename)


class Collection(object):
    _gdf = None

    def __init__(self, features, index=None):
        if isinstance(features, list):
            self._set_data(gpd.GeoDataFrame.from_features(features))
        elif isinstance(features, gpd.GeoDataFrame):
            self._set_data(features)
        else:
            raise TypeError(f"Type '{type(features)}' for 'features' not understood.")
        if index:
            self.data.set_index(index)


    def _set_data(self, data):
        self._gdf = data

    @property
    def data(self):
        return self._gdf

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, name):
        return self.data[name]

    # def __setitem__(self, name, value):
    #     self.data[name] = value
    #
    # def __delitem__(self, name):
    #     del self.data[name]

    def _get_field(self, column):
        return self.data[column]

    def _get_record(self, row):
        return self.data.loc[row]

    @property
    def fields(self):
        return self.data.columns

    def _add_field(self, name, data, inplace=True):
        df = self.data
        df[name] = data
        if inplace:
            self._gdf = df
        else:
            return self.__class__(df)

    def deref(self, expr: str):
        df = self.data
        res = df.apply(lambda row:expr.format(**{k:v for k,v in row.items()}),
                       axis=1)
        return res

    def to_geojson(self, filename=None):
        if not filename:
            return json.loads(self.data.to_json())

        self.data.to_file(filename, driver='GeoJSON')
        return filename

    @classmethod
    def from_geojson(cls, filename):
        with open(filename, 'r') as fp:
            gjs = json.load(fp)
        return cls(gjs['features'])
