from pyproj import CRS
from geopandas import GeoDataFrame


def _nie():
    raise NotImplementedError

def _tout(s):
    return "{!s}\n".format(s)

def _tout_df(gdf):
    from pandas import option_context
    with option_context('display.max_rows', 6,
                        'display.max_columns', 0):
        out = str(gdf)
    return _tout(out)


class GeopkgBase(object):
    def __init__(self, data=None, crs=None):
        """
        Input:
            - data: Dict[str,Any]
            - crs: str
        """
        self.data = self._check_data(data)
        self.crs = self._check_crs(crs)
        if self.data:
            if self.crs:
                self.data = _to_crs(self.data, self.crs)
            else:
                assert self.crs == None, "CRS should be 'None' here"
                wkts = {}
                for crs in [gdf.crs for gdf in self.data.values() if gdf.crs]:
                    wkt = crs.to_wkt()
                    wkts[wkt] = 1 + wkts.get(wkt, 0)
                if len(wkts) == 1:
                    self.crs = CRS(list(wkts.keys())[0])
                else:
                    print("WARNING: not all layer CRSs are the same:", wkts)
                    print("WARNING: leaving 'crs = None'")
                    print("WARNING: fix that with .to_crs(dst_crs)")
                    # pick_crs = sorted(d.items(), key=lambda kv:kv[1])
                    # pick_crs = pick_crs.pop()[0] # Pick the one with highest count.
                    # print("WARNING: will pick one CRS to define package:", pick_crs)
                    # self.data = self._to_crs(pick_crs)
                    # self.crs = pick_crs


    def _check_data(self, data):
        if data is None or not data:
            return {}
        is_dct = isinstance(data, dict)
        assert is_dct, "Expecting type(data)==dict"
        return data

    def _check_crs(self, crs):
        if crs is None or not crs:
            return None
        return CRS(crs)

    def check(self):
        return self._check_crs(self.crs) and self._check_data(self.data)

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError as err:
            raise AttributeError(str(err))

    def __getitem__(self, name):
        return self.data[name]

    def __setitem__(self, name, value):
        self.data[name] = value

    def __str__(self):
        out = ""
        for lyr, gdf in self.items():
            out += _tout(lyr)
            out += _tout("-" * len(lyr))
            if len(gdf) > 10:
                out += _tout_df(gdf)
            else:
                out += _tout_df(gdf)
            out += "\n"
        return out

    def __repr__(self):
        return str(self.items())

    def __contains__(self, name):
        return name in self.data

    def __len__(self):
        return len(self.data)

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def list(self, sort=True):
        """
        Return list of layer names

        Input:
        - sort : bool
            If True, return a sorted (ascending) list
        """
        keys = self.keys()
        if sort:
            keys = sorted(keys)
        return list(keys)

    def to_gpkg(self, filename, overwrite=False):
        """Write to geopackage"""
        self._do_write(filename)

    def to_dict(self):
        """Dump a json"""
        return {name:df.to_dict() for name,df in self.items() }

    def to_json(self):
        """Dump a json"""
        return {name:df.to_json() for name,df in self.items() }

    def _do_write(self, filename, layers=None):
        """Write to file, overwritting if already there"""
        for name, gdf in self.items():
            if layers is None or name in layers:
                try:
                    gdf.to_file(filename,
                                driver='GPKG',
                                layer=name)
                except Exception as err:
                    print('Error writing layer', name)
                    raise err

    def to_crs(self, dst_crs):
        """
        Return new Geopkg with all layers to 'dst_crs'
        """
        crs = CRS(dst_crs)
        data = _to_crs(self.data, crs)
        gpkg = self.__class__(data=data, crs=crs)
        return gpkg


def _to_crs(data, dst_crs):
    return {name:gdf.to_crs(dst_crs) for name,gdf in data.items() if gdf.crs}
