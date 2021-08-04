import logging
from collections import OrderedDict

WORLD = {
    'minlat': -90,
    'maxlat': 90,
    'westlon': -180,
    'eastlon': 180
}

class Latitude(object):
    min_limit = WORLD['minlat']
    max_limit = WORLD['maxlat']
    def __init__(self, min, max):
        self.min = min
        self.max = max


class Longitude(object):
    west_limit = WORLD['westlon']
    east_limit = WORLD['eastlon']
    def __init__(self, west, east):
        self.west = west
        self.east = east


class Bbox(object):
    # bbox is either None or 
    # a structure with 'lons' (Longitude) and 'lats' (Latitude) keys (e.g, Dict)
    # self._bbox = None

    def __init__(self, bbox):
        """
        Return a bounding-box representation.

        'bbox' can be represented either as a string, dict, list (or tuple).

        * "as dict":
            - {'minlat': ymin, 'maxlat': ymax, 'westlon': xmin, 'eastlon': xmax}
            - {'ymin': ymin, 'ymax': ymax, 'xmin': xmin, 'xmax': xmax}
        * "as list/tuple":
            - [xmin, ymin, xmax, ymax]
        * "as string":
            - 'xmin ymin xmax ymax'
            - 'xmin,ymin,xmax,ymax'
            - 'xmin, ymin, xmax, ymax'

        See https://wiki.openstreetmap.org/wiki/Bounding_Box
        """
        if isinstance(bbox, (dict, OrderedDict)):
            vals = parse_dict(bbox)
        elif isinstance(bbox, (list,tuple)):
            vals = parse_array(bbox)
        elif isinstance(bbox, str):
            vals = parse_string(bbox)
        else:
            msg_none = ("None argument given, expected either 'dict', 'list' or 'string'",
                        "See this object's 'help' for input format.",
                        "In the meantime, a string like this will do:",
                        "'west_lon min_lat east_lon max_lat'.")
            raise Exception(msg_none)
        lons,lats = vals
        self.lons = lons
        self.lats = lats

    def to_dict(self):
        return {
            'westlon': self.lons.west,
            'eastlon': self.lons.east,
            'minlat': self.lats.min,
            'maxlat': self.lats.max
        }


def parse_string(stg):
    cln = stg.strip().replace(',',' ').replace(' '*2, ' ')
    arr = [float(cs) for cs in cln.split()]
    return parse_array(arr)


def parse_array(arr):
    assert len(arr) == 4, f"Expecting length-4 array of coordinates, instead got {len(arr)} ({arr})"
    lons = Longitude(west=arr[0], east=arr[2])
    lats = Latitude(min=arr[1], max=arr[3])
    return (lons,lats)


def parse_dict(dct):
    clr_keys = ('westlon','minlat','eastlon','maxlat')
    amb_keys = ('xmin','ymin','xmax','ymax')
    if all([k in dct for k in clr_keys]):
        return parse_array([ dct[k] for k in clr_keys ])
    elif all([k in dct for k in amb_keys]):
        return parse_array([ dct[k] for k in amb_keys ])
    else:
        raise Exception(
            f"Expecting dictionary to have keys '{clr_keys}' or '{amb_keys}', got {dct.keys()} instead"
        )
    return None # Should never get here anyways...but I like a final 'return'
