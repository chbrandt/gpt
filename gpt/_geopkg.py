import os
import sys
import shutil
import collections

import fiona
import geopandas

from . import _base
from . import utils
from .log import *


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
            logerr("{!s}".format(err))
        try:
            super().__del__()
        except:
            pass

    def layers(self):
        return self.data.items()

    def info(self):
        for k,v in self.layers():
            print("{!s}:".format(k))
            print("\tCRS:{!s}".format(v.crs))
            print()

    def _fix_style_layer_name_changed(self:_base.GeopkgBase, oldname, newname):
        styles = self["layer_styles"]
        styles.loc[styles["f_table_name"] == oldname, "f_table_name"] = newname

    def rename_layer(self, name_old, name_new):
        self.data[name_new] = self.data[name_old]
        del self.data[name_old]
        self._fix_style_layer_name_changed(name_old, name_new)
        return self

    def _ensure_just_one_default_style(style_table, layer_name):
        """perform some checks on the style table and clean if possible"""
        ids = list(styles.loc[styles["f_table_name"] == layer_name].index) # ids of the possible style for this layer
        defaults = list(styles.loc[ ids, "useAsDefault"]) # the default flag for these rows
        
        if len(ids) == 0:
            log.error("no style for this layer found")
            return
        
        if len(ids) == 1:
            id = ids[0] # use that as style
            
        else: # we select the first style that is also set as default
            try:
                first_default  = defaults.index(True)
                id = ids[first_default]
            except: # no style set as default
                log.warning("No styles with default flag. using as style the last inserted. may be a problem!")
                id = ids[-1] # chose the last inserted
        
        styles.loc[ids, "useAsDefault"] = False # clear default flags, just to be sure, we may actually want to delete those unused styles
        styles.loc[id, "useAsDefault"] = True # now set the default style
        
    
    def rename_field(self:_base.GeopkgBase, layer_name, old_field_name, new_field_name):
        # classical change
        layer = self[layer_name]
        layer.rename(columns={old_field_name:new_field_name}, inplace=True)
        
        # fix the style table
        styles = self["layer_styles"] # extract the style table - we should check whether it exists or not btw
        
        # these would not be needed actually, just an useful check
        _ensure_just_one_default_style(styles, layer_name)
        
        # now we want to alter the qml content for all the styles connected with this layers
        ids = list(styles.loc[styles["f_table_name"] == layer_name].index)
        for id in ids:
            qml = styles.loc[id, "styleQML"]
    
            import xml.etree.ElementTree as ET
            tree = ET.fromstring(qml)
            renderer = tree.find("renderer-v2")
            
            if renderer.attrib["attr"] == old_field_name: # the field was used in this style
                renderer.attrib["attr"] = new_field_name
                newstyle = str(ET.tostring(tree, encoding='unicode', method='xml'))
                styles.loc[id,"styleQML"] = newstyle
            else: # nothing to do - not affected
                log.debug("the field were not used as filter for the style")
                return self
    
            # clear this because we cannot grant 1 to 1 with qml for now
            styles.loc[id, "styleSLD"] = ' '
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
