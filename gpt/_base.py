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
        layers = self.data.keys()
        if sort:
            layers = sorted(layers)
        return list(layers)

    def write_file(self, filename, overwrite=False):
        """Write to geopackage"""
        self.do_write(filename)

    def do_write(self, filename):
        """Write to file, overwritting if already there"""
        for name,gdf in self.data.items():
            gdf.to_file(filename,
                        driver='GPKG',
                        layer=name)
