import os
import sys
import shutil
import requests

from gpt import log


def download_files(urls, filenames=None, progress_on=False, make_dirs=False):
    assert isinstance(urls, (list, tuple))

    if path and path.strip():
        os.makedirs(path)
    else:
        path = '.'

    if not filenames:
        filenames = [ url.split('/')[-1] for url in urls ]
    assert len(filenames) == len(urls), "List of 'filenames' must match length of 'urls'"

    files_downloaded = []
    for url, filename in zip(urls, filenames):
        try:
            _fn = download_file(url, filename, progress_on, make_dirs)
        except Exception as err:
            _fn = None
            print(err)
            print("If, moving next")
        files_downloaded.append(_fn)

    return files_downloaded


def download_file(url, filename=None, progress_on=False, make_dirs=True):
    if not filename:
        local_filename = os.path.join('.', url.split('/')[-1])
    else:
        local_filename = filename

    if _is_downloaded(url, local_filename):
        log.debug("File '{}' from '{}' already downloaded".format(local_filename, url))
        return local_filename

    _path = os.path.dirname(local_filename)
    if not os.path.isdir(_path):
        if make_dirs:
            os.makedirs(_path, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(_path))
            return None

    print('--> Downloading file {} ..'.format(local_filename))
    if progress_on:
        download_file_progress(url, local_filename)
    else:
        download_file_silent(url, local_filename)
    print('--> File downloaded.'.format(local_filename))

    return local_filename


def _is_downloaded(url, filename):
    if not os.path.isfile(filename):
        log.debug("File '{}' does not exist.".format(filename))
        return False

    log.debug("File '{}' exist.".format(filename))
    try:
        r = requests.get(url, stream=True)
        remote_size = int(r.headers['Content-Length'])
        local_size = int(os.path.getsize(filename))
    except Exception as err:
        log.error(err)
        return False
    log.debug("Remote file size: " + str(remote_size))
    log.debug("Local file size: " + str(local_size))
    return local_size == remote_size


def download_file_silent(url, filename):
    """
    Download file (silently)

    Usage:
        download_file_silent('http://web4host.net/5MB.zip', 'local_filename.zip')
    """
    try:
        r = requests.get(url)
        with open(filename,'wb') as f:
            f.write(r.content)
    except Exception as err:
        log.error(err)
        return False

    return True


def download_file_progress(url, filename, verbose=False):
    """
    Download file with progress-bar

    Usage:
        download_file_progress('http://web4host.net/5MB.zip', 'local_filename.zip')
    """
    import tqdm
    try:
        r = requests.get(url, stream=True)
        file_size = int(r.headers['Content-Length'])
        chunk = 1
        chunk_size=1024
        num_bars = int(file_size / chunk_size)
        if verbose:
            print(dict(file_size=file_size))
            print(dict(num_bars=num_bars))

        with open(filename, 'wb') as fp:
            for chunk in tqdm.tqdm(
                                        r.iter_content(chunk_size=chunk_size)
                                        , total= num_bars
                                        , unit = 'KB'
                                        , desc = filename
                                        , leave = True # progressbar stays
                                    ):
                fp.write(chunk)
    except Exception as err:
        log.error(err)
        return False

    return True
