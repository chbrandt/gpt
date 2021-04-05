from dataclasses import dataclass, make_dataclass, field, asdict
from typing import List, Dict

# from gpt import Geopkg
import gpt

meta_json = {
    "project": (
        str,
        field( default="GM" )
    ),
    "name": (
        str,
        field( default="package" )
    ),
    "body": (
        str,
        field( default="target" )
    ),
    "type": (
        str,
        field( default="geological" )
    ),
    "description": (
        str,
        field( default = '' )
    ),
    "crs": (
        str,
        field( default='' )
    ),
    "outline": (
        str,
        field( default='' )
    ),
    "bounding_box": (
        Dict[str,float],
        field( default_factory = lambda:{'minlat':0,'maxlat':0,'westlon':0,'eastlon':0} )
    ),
    "references": (
        List[str],
        field( default_factory = lambda:["GMAP project"] )
    ),
    "attribution": (
        str,
        field( default = "[GMAP project](www.europlanet-gmap.eu)" )
    )
}


_meta = tuple((k,*v) for k,v in meta_json.items())


@dataclass
class _GMetaBase:
    def check(self, messages=None, treat_warnings_as_errors=False):
        msgs = {}
        ok = True
        if not self.body:
            msgs['WARNING'] = msgs.get('WARNING', []) + ['Body not defined']
            ok *= not treat_warnings_as_errors
        if not self.crs:
            msgs['WARNING'] = msgs.get('WARNING', []) + ['CRS not defined']
            ok *= not treat_warnings_as_errors
        if not self.bounding_box:
            msgs['WARNING'] = msgs.get('WARNING', []) + ['Bounding-box not defined']
            ok *= not treat_warnings_as_errors
        if not self.name:
            msgs['WARNING'] = msgs.get('WARNING', []) + ['Name not defined']
            ok *= not treat_warnings_as_errors
        if not self.project:
            msgs['WARNING'] = msgs.get('WARNING', []) + ['Project not defined']
            ok *= not treat_warnings_as_errors
        if isinstance(messages, dict):
            messages.update(msgs)
        return ok


_GMeta = make_dataclass('_GMeta', _meta,
                         namespace = {
                             'id': lambda self: f"{self.project}_{self.body}_{self.type}_{self.name}"
                         },
                        bases=(_GMetaBase,)
                       )


class GPkg(object):
    """
    Holds a GMAP package layout

    Members:
        - id
        - meta
        - vector
        - raster
    """
    _meta = None
    _vector = None
    _raster = None

    def __init__(self, meta=None):
        self._meta = _GMeta() if not meta else _GMeta(**meta)

#     def __bool__(self):
#         return bool(self._meta) + bool(self._vector) + bool(self._raster)

    @property
    def id(self):
        return self._meta.id()

    def check(self, treat_warnings_as_errors=True):
        def print_messages(msgs, title='messages'):
            """
            Print messages like:
            msgs = {
                'warning': ['some message', 'another'],
                'error': [],
                'info': ['summary something']
            }
            """
            if not msgs:
                return None
            print(f"\n{title}\n{'-'*len(title)}")
            for lvl in msgs.keys():
                print(f"{lvl}S")
                for msg in msgs[lvl]:
                    print(f'- {msg}')

        meta_msgs = {}
        meta_ok = self._meta.check(messages=meta_msgs)
        print_messages(meta_msgs, 'Package metadata')

        data_msgs = {}
        if self._vector is None:
            data_msgs['WARNING'] = data_msgs.get('WARNING', []) + ['vector data is empty']
            vector_ok = not treat_warnings_as_errors
        else:
            vector_ok = bool(self._vector.check())

        if self._raster is None:
            data_msgs['WARNING'] = data_msgs.get('WARNING', []) + ['raster data is empty']
            raster_ok = not treat_warnings_as_errors
        else:
            raster_ok = bool(self._raster.check())

        data_ok = vector_ok and raster_ok
        print_messages(data_msgs, 'Package data (vector,raster)')

        ok = meta_ok and data_ok
        print("OK",ok)
        print("OK-meta",meta_ok)
        print("OK-data",data_ok)
        print("OK-data-vector",vector_ok)
        print("OK-data-raster",raster_ok)
        if treat_warnings_as_errors:
            _ld = len(data_msgs.get('WARNING',[]))
            _lm = len(meta_msgs.get('WARNING',[]))
            ok &= bool(_ld+_lm)

        return ok

    def load_gpkg(self, filename):
        """
        Load vector layers from 'filename' to the list of vector data
        """
        vec = gpt.load_gpkg(filename)
        self._vector = vec

    def load_tiff(self, filename):
        """
        Load raster array from 'filename' to the list of raster data
        """
        rst = gpt.load_tiff(filename)
        self._raster = rst
