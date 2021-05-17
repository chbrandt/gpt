"""
Functions and Classes to handle geo-spatial data search on DBs or REST/APIs
"""

def available_apis():
    _apis = [
        'ode'
    ]
    return _apis


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
        resdf = ode.search(bbox=_bb, match=match,
                            target=target_body, ihid=mission,
                            iid=instrument, pt=product_type)

    return None
