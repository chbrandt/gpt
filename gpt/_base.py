def _nie():
    raise NotImplementedError


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

    def list(self, sort=True):
        """
        Return list of layer names

        Input:
        - sort : bool
            If True, return a sorted (ascending) list
        """
        layers = self.data.keys()
        if sort:
            layers = sorted(layers)
        return list(layers)

    def to_gpkg(self, filename, overwrite=False):
        """Write to geopackage"""
        self._do_write(filename)

    def _do_write(self, filename, layers=None):
        """Write to file, overwritting if already there"""
        for name,gdf in self.data.items():
            if layers is None or name in layers:
                gdf.to_file(filename,
                            driver='GPKG',
                            layer=name)
