import fiona
import geopandas


def _nie():
    raise NotImplementedError


class utils:
    @staticmethod
    def read_geopackage(filename):
        layers = fiona.listlayers(filename)
        data = {}
        for layer in layers:
            data[layer] = geopandas.read_file(filename,
                                              driver='GPKG',
                                              layer=layer)
        return data


class _GeopkgInterface:
    def list(self):
        _nie()

    @staticmethod
    def read_file(filename):
        _nie()

    def write_file(self, filename, overwrite=False):
        """Write to geopackage"""
        _nie()

    def do_write(self, filename):
        """Write to file, overwritting if already there"""
        _nie()


class Geopkg(_GeopkgInterface):
    def __init__(self, data=None):
        super().__init__()
        self.data = data

    # def __getattribute__(self, attr):
    #     if attr in self.data.keys():
    #         return self.data.__getitem__(attr)
    #     else:
    #         return

    @staticmethod
    def read_file(filename):
        data = utils.read_geopackage(filename)
        return Geopkg(data)

    def list(self, sort=True):
        layers = self.data.keys()
        if sort:
            layers = sorted(layers)
        return list(layers)

    def rename_layer(self, name_old, name_new):
        self.data[name_new] = self.data[name_old]
        del self.data[name_old]
