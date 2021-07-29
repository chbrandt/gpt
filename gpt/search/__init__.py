"""
Functions and Classes to handle geo-spatial data search on DBs or REST/APIs
"""

from gpt.helpers import Bbox

from abc import ABC, abstractmethod

class SearchBase(ABC):
    @abstractmethod
    def bbox(self, bbox):
        pass


# -----------------------------------------
# Dynamic load module in current directory:
#
# DEPRECATED
#
import sys
import pkgutil
import importlib

pkg = sys.modules[__package__]

_mods = {}
for finder, namespace, ispkg in pkgutil.iter_modules(pkg.__path__, pkg.__name__+'.'):
    name = namespace.split('.')[-1]
    mod = importlib.import_module(namespace)
    _mods[name] = mod

del pkg, finder, name, ispkg, mod
del importlib, pkgutil, sys
#
# -----------------------------------------

def available_apis():
    # return [ m.__name__.split('.')[-1] for m in _mods.values() ]
    return list(_mods)

def get_api(name):
    """
    Return object implementing/inheriting from ~Search
    """
    mod = _mods[name]
    if hasattr(mod, 'Search'):
        api = getattr(mod, 'Search')
        assert issubclass(api, SearchBase)
    else:
        api = mod
    return api


def footprints(bbox, api='ode', db=None, match="intersect",
               target_body=None, mission=None, instrument=None, product_type=None):
    """
    Search for product/geometries in 'api' or 'db' matching 'bbox'

    Matching 'bbox'-x-"footprints" in api/db respects 'match' option.
    Input:
        - bbox : ~gpt.helpers.Bbox, list, string, dict
            Bounding-box object or compatible, see ~gpt.helpers.Bbox
        - api : string
            Name of available APIs
        - match : string
            Options are:
            * 'intersect', match product footprints intersecting 'bbox'
            * 'contain', match product footprints contained inside 'bbox'
        - db : not-implemented
    Output:
        Return ~gpt.helpers.Collection with the results
    """
    assert api or db, "Either 'api' or 'db' should be given. Check ~available_apis()"
    assert api in available_apis(), "Expected a value from ~available_apis()"

    from gpt.helpers import Bbox
    _bb = bbox if isinstance(bbox, Bbox) else Bbox(bbox)

    if api == 'ode':
        from . import ode
        resdf = ode.search(bbox=_bb, match=match,
                            target=target_body, ihid=mission,
                            iid=instrument, pt=product_type)

    return None
