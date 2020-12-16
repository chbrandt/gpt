from . import log

def string_2_dict(bbox):
    """
    Convert bbox in comma-sep string to bbox dictionary

    Input bbox (string) is as 'minlat,maxlat,westlon,eastlon'
    """
    _lbl = ['minlat','maxlat','westlon','eastlon']
    _bbx = [float(c) for c in bbox.split(',')]
    bounding_box = {k:v for k,v in zip(_lbl,_bbx)}
    return bounding_box
