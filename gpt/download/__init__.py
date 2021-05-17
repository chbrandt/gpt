from ._download import download_files, download_file

def download(URLs, filenames=None, progress_on=False, make_dirs=False):
    if isinstance(URLs, (list,tuple)):
        assert filenames is None or isinstance(filenames, (list, tuple))
        return download_files(URLs, filenames, progress_on, make_dirs)
    else:
        assert isinstance(URLs, str)
        assert filenames is None or isinstance(filenames, str)
        return download_file(URLs, filenames, progress_on, make_dirs)
