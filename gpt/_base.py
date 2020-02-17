def _nie():
    raise NotImplementedError


class GeopkgBase:
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
