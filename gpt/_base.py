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
    def __init__(self, data):
        self.data = dict(data) if data is not None else {}

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
        for lyr, gdf in self.data.items():
            out += _tout(lyr)
            out += _tout("-" * len(lyr))
            if len(gdf) > 10:
                out += _tout_df(gdf)
            else:
                out += _tout_df(gdf)
            out += "\n"
        return out

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
        for name, gdf in self.data.items():
            if layers is None or name in layers:
                try:
                    gdf.to_file(filename,
                                driver='GPKG',
                                layer=name)
                except Exception as err:
                    print('Error writing layer', name)
                    raise err
