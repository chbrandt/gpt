from .formatters import geojson_2_geodataframe, products_2_geojson, json_2_geojson

import json

from . import log

def read(filename):
    """
    Return 'features' from GeoJSON
    """
    with open(filename, 'r') as fp:
        js = json.load(fp)
        features = js['features']
    return features


def to_geodataframe(records):
    assert isinstance(records, list), "Expected a list [{}], instead got {}".format(type(records))
    gpdrecs = []
    for rec in records:
        geom = rec['geometry']
        if isinstance(geom, str):
            try:
                # rec['geometry'] = shapely.wkt.loads(rec['geometry'])
                geom = shapely.wkt.loads(geom)
            except Exception as err:
                log.error(err)
                raise err
        else:
            try:
                geom = shapely.geometry.asShape(geom)
            except Exception as err:
                log.error(err)
                raise err
        gpdrec = rec['properties']
        gpdrec['geometry'] = geom
        gpdrecs.append(gpdrec)
    gdf = gpd.GeoDataFrame(gpdrecs)
    return gdf
