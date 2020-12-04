import os
import sys

from . import _base
from . import utils
from .log import *
from .styling import (fix_qml_style_on_field_name_change,
                      fix_sld_style_on_field_name_change,
                      ensure_just_one_default_style)


class Geopkg(_base.GeopkgBase):
    """
    Data:
     - _tempdir [None] temporary directory if needed for data caching
    """
    _tempdir = None

    def __init__(self, data=None, file=None, tempdir=None):
        """
        Dictionary-like structure to handle multi-layered geo data tables

        Input:
         - data: dict
            Layers/tables with geodata; Format: {'label': GeoDataFrame, ...}
         - file: string
            Geopackage filename to read data from (has precedence over 'data')
         - tempdir: string
            Path/directory to use for occasional data caching
        """
        if tempdir is not None:
            assert os.path.isdir(tempdir), print("Expected to find 'tempdir'")
            self._tempdir = {'path':tempdir, 'generated':False}
        else:
            self._tempdir = {'path':utils.create_tempdir(), 'generated':True}
        if file is not None:
            data = self._read_gpkg(file)
        super().__init__(data)

    def __del__(self):
        try:
            self._remove_tempdir()
        except Exception as err:
            print("{!s}".format(err), file=sys.stderr)
        try:
            super().__del__()
        except:
            pass

    # @property
    # def layer_names(self):
    #     return tuple(self.keys())

    # @property
    # def layer_tables(self):
    #     return tuple(self.values())

    @property
    def layers(self):
        return self.items()

    def info(self):
        for k,v in self.layers():
            print("{!s}:".format(k))
            print("\tCRS:{!s}".format(v.crs))
            print()

    def _fix_style_layer_name_changed(self:_base.GeopkgBase, oldname, newname):
        styles = self["layer_styles"]
        styles.loc[styles["f_table_name"] == oldname, "f_table_name"] = newname

    def rename_layer(self, name_old, name_new):
        # TODO: remove reference to 'data'; this class doesn't know about 'data'
        #
        self.data[name_new] = self.data[name_old]
        del self.data[name_old]
        self._fix_style_layer_name_changed(name_old, name_new)
        return self

    def rename_field(self: _base.GeopkgBase, layer_name, old_field_name, new_field_name):
        # classical change
        layer = self[layer_name]
        layer.rename(columns={old_field_name: new_field_name}, inplace=True)

        # fix the style table
        styles = self["layer_styles"]  # extract the style table - we should check whether it exists or not btw

        # these would not be needed actually, just an useful check
        # ensure_just_one_default_style(styles, layer_name)

        # now we want to alter the qml/sld content for all the styles connected with this layers
        ids = list(styles.loc[styles["f_table_name"] == layer_name].index)
        for id in ids:  # we dont know beforehand if the specific field was used or not. we cycle on all
            qml = styles.loc[id, "styleQML"]
            newstyle = fix_qml_style_on_field_name_change(qml, old_field_name, new_field_name)
            styles.loc[id, "styleQML"] = newstyle

            sld = styles.loc[id, "styleSLD"]
            newstyle = fix_sld_style_on_field_name_change(sld, old_field_name, new_field_name)
            styles.loc[id, "styleSLD"] = newstyle
            return self


    def _read_gpkg(self, filename):
        assert all(a in self._tempdir for a in ['path','generated'])
        tempdir = self._tempdir
        if utils.is_url(filename):
            try:
                local_filename = utils.download(filename, dst=tempdir['path'])
            except:
                self._remove_tempdir()
                raise
        else:
            local_filename = filename
        data = utils.read_gpkg(local_filename, layers='all')
        return data

    def _remove_tempdir(self):
        """
        Remove (if created) instance' temp dir. Called during object deletion.
        """
        if self._tempdir:
            assert all(a in self._tempdir for a in ['path','generated'])
            # Don't want to 'assert' but that should be true:
            # os.path.exists() and os.path.isdir()
            if self._tempdir['generated']:
                utils.remove_dir(self._tempdir['path'])
