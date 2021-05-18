import json
import geopandas as gpd
from collections import UserList



class Collection(object):
    _gdf = None

    def __init__(self, features, index=None):
        if isinstance(features, list):
            self._gdf = gpd.GeoDataFrame.from_features(features)
        elif isinstance(features, gpd.GeoDataFrame):
            self._gdf = features
        else:
            raise TypeError(f"Type '{type(features)}' for 'features' not understood.")

        if index:
            self._gdf.set_index(index)

    def __repr__(self):
        return repr(self._gdf)

    def __str__(self):
        return str(self._gdf)

    def __len__(self):
        return len(self._gdf)

    def __iter__(self):
        return iter(self._gdf)


    def _get_field(self, column):
        return self._gdf[column]


    def _get_record(self, row):
        return self._gdf.loc[row]


    def _add_field(self, name, data, inplace=True):
        df = self._gdf
        df[name] = data
        if inplace:
            self._gdf = df
        else:
            return self.__class__(df)

    def deref(self, expr: str):
        df = self._gdf
        res = df.apply(lambda row:expr.format(**{k:v for k,v in row.items()}),
                       axis=1)
        return res

    @property
    def fields(self):
        return self._gdf.columns

    @classmethod
    def from_geojson(cls, filename):
        with open(filename, 'r') as fp:
            gjs = json.load(fp)
        return cls(gjs['features'])

    def to_geojson(self, filename=None):
        if not filename:
            return json.loads(self._gdf.to_json())

        self._gdf.to_file(filename, driver='GeoJSON')
        return filename
