"""
Define functions/Ojects to interact with ODE REST API (http://oderest.rsl.wustl.edu/)
"""
import requests
import pandas

# ODE REST-API endpoint
API_URL = 'https://oderest.rsl.wustl.edu/live2'

def available_datasets(target=None, summary=False):
    """
    Return ~pandas.DataFrame with ODE's table of available datasets

    Output table contains only a subset of retrieve data from ODE.
    Columns with statistics and flags are droped (unless 'return_all' is True)

    Input:
        - target : string
            Planetary body
        - return_all : bool
            If True, return all columns from ODE/IIPT, otherwise just the important ones
    Output:
        Return ~pandas.DataFrame with IIPT results, otherwise None
    """
    params = { 'query' : 'iipt' }
    if target.strip():
        params.update({ 'odemetadb':'mars' })

    # res = requests.get('http://oderest.rsl.wustl.edu/live2?query=iipt&output=JSON&odemetadb=mars')
    resjs = _request(API_URL, params)
    if not resjs:
        return None

    datasets = resjs['ODEResults']['IIPTSets']['IIPTSet']

    id_columns = 'ODEMetaDB IHID IID PT'.split()
    ok_columns = 'DataSetId IHName IName PTName NumberProducts'.split()

    df = pandas.DataFrame(datasets)[id_columns + ok_columns]
    df = df.set_index(id_columns)
    if summary:
        return df.index.unique().to_frame().reset_index(drop=True)
    return df


def search(bbox, target, ihid, iid, pt, match='contain'):
    from npt.utils.bbox import Bbox
    bbox = Bbox(bbox).to_dict()

    params = dict(
        query='product',
        results='fmpc',
        output='JSON',
        loc='f',
        minlat=bbox['minlat'],
        maxlat=bbox['maxlat'],
        westlon=bbox['westlon'],
        eastlon=bbox['eastlon']
    )

    if target:
        params.update({'target':target})
    if ihid:
        params.update({'ihid':ihid})
    if iid:
        params.update({'iid':iid})
        if pt:
            params.update({'pt':pt})

    if 'contain' in match:
        params.update({'loc':'o'})

    resjs = _request(API_URL, params)
    if not resjs:
        return None

    products = resjs['ODEResults']['Products']['Product']
    # If only one data product is found, 'products' is not a list; fix this
    products = products if isinstance(products, (list,tuple)) else [products]

    return products


def parse_products(resjs, meta_selectors=None, data_selectors=None, exclude_notes=True):
    products = []
    for product in resjs:
        meta = {}
        notes = None
        files = None
        for key,value in product.items():
            if key == 'Product_files':
                files = product[key]['Product_file']
                if data_selectors:
                    files = select_files(files, data_selectors)
                continue
            if key == 'ODE_notes':
                notes = product[key]['ODE_note']
                continue
            if not meta_selectors:
                meta[key] = value
            else:
                if key in meta_selectors:
                    meta[key] = value

        meta['product_files'] = files
        if not exclude_notes:
            meta['notes'] = notes
        products.append(meta)

    return products


def select_files(product_files: list, data_selectors: dict) -> list:
    try:
        match_all = data_selectors.pop('match_selector')
    except:
        match_all = True
    else:
        assert match_all in ('all','any'), "Expected to have 'all' or 'any' for 'match_selector'"
        match_all = True if match_all == 'all' else False

    selected_files = []
    for product_file in product_files:
        matches = [ _match_selector(field,value,product_file) for field,value in data_selectors.items() ]
        if (match_all and all(matches)) or (any(matches) and not match_all):
                selected_files.append(product_file)

    return selected_files


def _match_selector(selector_field, selector_value, product_file):
    import re

    supported_selectors = ('Description', 'FileName', 'Type')

    if selector_field not in supported_selectors:
        print(f"Data selector field '{selector_field}' not supported '{supported_selectors}'")
        return False

    if isinstance(selector_value, (list,tuple)):
        return any([ _match_selector(selector_field, _v, product_file) for _v in selector_value ])

    regex = re.compile(selector_value, re.IGNORECASE)
    search_value = product_file[selector_field]
    return regex.search(search_value)


def _request(url, params):
    """
    Return JSON from GET request at 'url' for 'params' queried

    Input:
        - url : string
            API endpoint (http url)
        - params : dict
            parameters for the GET request
    Output:
        JSON object/dict if response is valid (code=200), otherwise, None
    """
    import requests

    # Let's guarantee that we hava JSON as result
    _params = params.copy()
    _params.update({ 'output':'JSON' })

    res = requests.get(API_URL, _params)

    # If response is not a round 200, fail it
    if res.status_code != 200:
        print('Request response failed:', str(res))
        return None

    js = res.json()

    # If response is valid (200) but ODE itself failed to respond the query, alert user
    if js['ODEResults']['Status'].lower() != 'success':
        print("Returned result says 'ODEResults'/'Status' != 'success'. Check for more info.")

    return js



def _set_payload(bbox, target=None, host=None, instr=None, ptype=None, how='intersect'):
    payload = dict(
        query='product',
        results='fmpc',
        output='JSON',
        loc='f',
        minlat=bbox['minlat'],
        maxlat=bbox['maxlat'],
        westlon=bbox['westlon'],
        eastlon=bbox['eastlon']
    )

    if target:
        payload.update({'target':target})
    if host:
        payload.update({'ihid':host})
    if instr:
        payload.update({'iid':instr})
        if ptype:
            payload.update({'pt':ptype})

    if 'contain' in how:
        payload.update({'loc':'o'})

    return payload
