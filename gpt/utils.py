import os
import sys
import shutil

import geopandas as gpd

from .log import *

def filebasename(path, isurl=False):
    if isurl:
        return path.split('/')
    else:
        return os.path.basename(path)


def download(url, dst=None, overwrite=False):
    """
    @param: url to download file
    @param: dst place to put the file
    @param: overwrite 'dst' if already there
    """
    import requests
    try:
        from tqdm import tqdm
    except:
        tqdm = None

    if dst is None or dst.strip() == '':
        dst = filebasename(url)
    elif os.path.isdir(dst):
        dst = os.path.join(dst, filebasename(url))

    file_size = int(requests.head(url).headers["Content-Length"])
    if os.path.exists(dst):
        if overwrite:
            os.remove(dst)
        else:
            first_byte = os.path.getsize(dst)
    else:
        first_byte = 0

    if first_byte >= file_size:
        msg = "File '{}', size '{}' bytes, was already there."
        log(msg.format(dst, first_byte))
    else:
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
        if tqdm:
            pbar = tqdm(total=file_size, initial=first_byte,
                        unit='B', unit_scale=True, desc=dst)
        else:
            pbar = None
        req = requests.get(url, headers=header, stream=True)
        with(open(dst, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    if pbar:
                        pbar.update(1024)
        if pbar:
            pbar.close()

        msg = "File named '{}', sized {} bytes, downloaded succesfully."
        log(msg.format(dst, file_size))

    return dst


def is_url(filename):
    return 'http' in filename[:4].lower()


def _listlayers(fname):
    import fiona
    return fiona.listlayers(fname)

def list_layers(filename, temp_dir=None):
    if is_url(filename):
        if temp_dir is None:
            from tempfile import mkdtemp
            temp_dir = mkdtemp()
        local_filename = download(filename, dst=temp_dir)
    else:
        local_filename = filename
    return _listlayers(local_filename)

def read_gpkg(filename, layers='all', features_only=False):
    """
    Return dict with gpkg content, by default 'all' layers are loaded
    """
    if layers == 'all':
        layers = list_layers(filename)
    out = {}
    for layer in layers:
        try:
            _data = gpd.read_file(filename, layer=layer, driver='GPKG')
        except Exception as err:
            msg = "Layer '{!s}' from '{!s}' could not be read."
            log(msg.format(layer, filebasename(filename)))
            logerr("{!s}".format(err))
        else:
            out[layer] = _data
    return out

def remove_dir(path):
    try:
        shutil.rmtree(path)
    except Exception as err:
        msg = "Something went wrong while cleaning '{!s}' temp directory:"
        log(msg.format(path))
        logerr("{!s}".format(err))

def create_tempdir():
    import tempfile
    tempdir = tempfile.mkdtemp()
    return tempdir
