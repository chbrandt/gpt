from gpt import _base
from pathlib import Path

class Rasterpkg(_base.GeopkgBase):
    def __init__(self, file=None, data=None, crs=None):
        if file is not None:
            path = Path(file)
            tiff = self._read_tiff(path.as_posix())
            name = path.stem
            data = { name: tiff }
        print("RasterPkg data:",data)
        super().__init__(data=data, crs=crs)

    def _read_tiff(self, filename):
        import rasterio
        tif = rasterio.open(filename, 'r')
        return tif
