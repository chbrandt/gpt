import os
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject

from . import log

# Default resampling method
_RESAMPLING = Resampling.bilinear


def open(filename):
    """
    Return Rasterio object from (tiff) 'filename'
    """
    return rasterio.open(filename)
    
def resample(filename_in, filename_out, scale_factor=0.5):

    with rasterio.open(filename_in) as src:

        transform, width, height = scale_transform(src.transform,
                                                    src.width, src.height,
                                                    scale_factor=scale_factor)

        # resample data to target shape
        data = src.read(
            out_shape=(src.count, height, width),
            resampling=_RESAMPLING
        )

        # copy src metadata, update as necessary for 'dst'
        kwargs = src.meta.copy()
        kwargs.update({
            'transform': transform,
            'width': width,
            'height': height
        })

        # reproject "src" to "dst"
        with rasterio.open(filename_out, 'w', **kwargs) as dst:
            for i, band in enumerate(data, 1):
                dst.write(band, i)

        return filename_out


def scale_transform(transform_src, width_src, height_src, scale_factor=0.5):
    src_transform = transform_src
    src_height = height_src
    src_width = width_src

    # compute "dst" sizes
    height = int(src_height * scale_factor)
    width = int(src_width * scale_factor)

    # scale image transform
    transform = src_transform * src_transform.scale(
        # (src.width / data.shape[-1]),
        # (src.height / data.shape[-2])
        (src_width / width),
        (src_height / height)
    )

    return (transform, width, height)


def warp(fileinname, fileoutname, dst_crs='EPSG:4326', scale_factor=None):

    with rasterio.open(fileinname) as src:

        # compute transform and boundaries for new CRS
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)

        if scale_factor:
            transform, width, height = scale_transform(transform,
                                                       width, height,
                                                       scale_factor)

        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        # reproject "src" to "dst"
        with rasterio.open(fileoutname, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=_RESAMPLING
                )

    return fileoutname


def to_tiff(filename_in, filename_out, format_in, cog=False):
    """
    For accepted formats (in): https://gdal.org/drivers/raster/index.html
    """
    format_in = 'ISIS3' if format_in == 'ISIS' else format_in
    if cog:
        return to_cog(filename_in, filename_out, format_in)
    else:
        with rasterio.open(filename_in, 'r', driver=format_in) as src:
            # Get a copy of the source dataset's profile. Thus our
            # destination dataset will have the same dimensions,
            # number of bands, data type, and georeferencing as the
            # source dataset.
            kwds = src.profile
            kwds['driver'] = 'GTiff'
            # Add GeoTIFF-specific keyword arguments.
            with rasterio.open(filename_out, 'w', **kwds) as dst:
                    dst.write(src.read())

        return filename_out


def to_cog(filename_in, filename_out, format_in):

    format_in = 'ISIS3' if format_in == 'ISIS' else format_in
    with rasterio.Env(GDAL_TIFF_OVR_BLOCKSIZE=512):
        with rasterio.open(filename_in, 'r', driver=format_in) as src:
            # Get a copy of the source dataset's profile. Thus our
            # destination dataset will have the same dimensions,
            # number of bands, data type, and georeferencing as the
            # source dataset.
            kwds = src.profile
            kwds['driver'] = 'GTiff'
            # Add GeoTIFF-specific keyword arguments.
            kwds['tiled'] = True
            kwds['blockxsize'] = 512
            kwds['blockysize'] = 512
            kwds['compress'] = 'LZW'
            kwds['copy_src_overviews'] = True
            with rasterio.open(filename_out, 'w', **kwds) as dst:
                    dst.write(src.read())

    return filename_out


def tiff2cog(filename_in, filename_out):
    """
    Transform GeoTIFF in COG
    """
    # from npt.isis import sh
    # gdal_cmd = sh.wrap('gdal_translate')
    # cog_args = """
    #     -co TILED=YES -co COMPRESS=LZW -co BLOCKXSIZE=512 -co BLOCKYSIZE=512
    #     -co COPY_SRC_OVERVIEWS=YES --config GDAL_TIFF_OVR_BLOCKSIZE 512
    # """.split()
    # res = gdal_cmd(filename_in, filename_out, *cog_args)
    return to_cog(filename_in, filename_out, format_in='GTiff')
