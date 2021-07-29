"""
Define functions/Ojects to interact with ODE REST API (http://oderest.rsl.wustl.edu/)
"""
import requests
import pandas

# ODE REST-API endpoint
_API_URL = 'https://oderest.rsl.wustl.edu/live2'


class Search(object):
    _response = None
    _dataset = None

    def __init__(self, target, ihid, iid, pt):
        self._dataset = {
            'target': target,
            'ihid': ihid,
            'iid': iid,
            'pt': pt
        }

    def __repr__(self):
        return '{cls}({args})'.format(
                    cls=self.__class__.__name__,
                    args=','.join([f'{k}="{v}"' for k,v in self._dataset.items()])
                )

    def __str__(self):
        import json
        return json.dumps(self._response)

    def available_datasets(self):
        import re
        ds = self._dataset
        df = available_datasets(target=ds['target'])
        orig_index = df.index.names
        _df = df.reset_index()
        _ihid = _df['IHID'].str.match(ds['ihid'], flags=re.IGNORECASE)
        _iid = _df['IID'].str.match(ds['iid'], flags=re.IGNORECASE)
        _pt = _df['PT'].str.match(ds['pt'], flags=re.IGNORECASE)
        df = _df.loc[_ihid & _iid & _pt]
        return df.set_index(orig_index)

    def search(self, bbox, match='contain'):
        ds = self._dataset
        response = search(bbox, match=match,
                            target=ds['target'], ihid=ds['ihid'],
                            iid=ds['iid'], pt=ds['pt'])
        self._response = response
        return Results(self._response)



class Results(object):
    _products = None

    def __init__(self, response: list):
        self._products = parse_products(response)
        self._df = self.to_geodataframe()

    def __repr__(self):
        return repr(self._products)

    def __str__(self):
        return str(self._products)

    def __len__(self):
        return len(self._products)

    def show(self, what='unique'):
        if what == 'unique':
            describe_unique(self._df)

    def unstack(self, field, func=None):
        products = unstack(self._products, field, func)
        self._products
        return self

    def to_geodataframe(self, geometry_field='Footprint_C0_geometry',
                        meta_selectors=None, data_selectors=None,
                        meta_select_how='exclude', data_select_how='all'):
        products = parse_products(self._products,
                                    meta_selectors=meta_selectors,
                                    data_selectors=data_selectors,
                                    meta_select_how=meta_select_how,
                                    data_select_how=data_select_how,
                                    include_notes=False, include_footprints=True)
        df = to_geodataframe(products,
                                geometry_field=geometry_field,
                                exclude_footprints=True,
                                unstack_field='product_files',
                                unstack_function=None)
        self._df = df
        return df

    # def to_geojson(self, output_filename, **kwargs):
    #     gdf = self.to_geodataframe(**kwargs)
    #     gjs = geodataframe_to_geojson(gdf, output_filename)
    #     return gjs

    def plot(self, legend_column='pdsid'):
        if self._df is None:
            df = self.to_geodataframe()
        else:
            df = self._df
        if not legend_column or legend_column not in df.columns:
            return df.plot(alpha=0.25, edgecolor='red', figsize=(12,8))
        else:
            df = df[[legend_column, 'geometry']].drop_duplicates(ignore_index=True)
            return df.plot(alpha=0.25, edgecolor='red',
                            legend=True, column=legend_column,
                            legend_kwds={'loc': 'upper left', 'bbox_to_anchor': (1, 1)},
                            figsize=(12,8))


def describe_unique(df):
    size = len(df)
    unique_columns = {}
    redundant_columns = {}
    important_columns = {}
    erroneous_columns = {}
    for col in df.columns:
        try:
            uniq_vals = df[col].unique()
            if len(uniq_vals)/size >= 0.5:
                if len(uniq_vals) == size:
                    msg = "All values are unique, important stuff"
                    unique_columns.update({col:msg})
                else:
                    msg = "Big variance of values (>=50%), looks important."
                    important_columns.update({col:msg})
            else:
                msg = str(uniq_vals)
                redundant_columns.update({col:msg})
        except Exception as err:
            msg = "Could not evaluate the values"
            erroneous_columns.update({col:msg})

    def print_kv(cols: dict):
        for k,v in cols.items():
            print('{:10}: {}'.format(k,v))

    print("\nImportant columns:")
    print_kv(important_columns)

    print("\nUnique columns:")
    print_kv(unique_columns)

    print("\nErroneous columns:")
    print_kv(erroneous_columns)

    print("\nRedundant columns:")
    print_kv(redundant_columns)


def available_datasets(target='Mars', ihid=None, iid=None, minimal=False):
    """
    Return ~pandas.DataFrame with ODE's table of available datasets

    Output table contains only a subset of retrieve data from ODE.
    Columns with statistics and flags are droped (unless 'return_all' is True)

    Input:
        - target : string
            Planetary body (Default: 'Mars')
        - ihid : string
            Mission (Instrument Host ID) to filter datasets list
        - iid : string
            Instrument (Instrument ID) to filter datasets list.
            Note: works only if 'ihid' is also specified.
        - minimal : bool
            If True, return a subset of data, otherwise return everything
    Output:
        Return ~pandas.DataFrame with IIPT results, otherwise None
    """
    assert isinstance(target, str)

    target = target.upper()
    if ihid:
        ihid = ihid.upper()
    if iid:
        iid = iid.upper()

    params = { 'query' : 'iipt' }
    if target.strip():
        params.update({ 'odemetadb': target })

    # res = requests.get('http://oderest.rsl.wustl.edu/live2?query=iipt&output=JSON&odemetadb=mars')
    resjs = _request(_API_URL, params)
    if not resjs:
        return None

    datasets = resjs['ODEResults']['IIPTSets']['IIPTSet']

    id_columns = 'ODEMetaDB IHID IID PT'.split()
    ok_columns = 'DataSetId IHName IName PTName'.split()
    n_column = ['NumberProducts']

    df = pandas.DataFrame(datasets)[id_columns + ok_columns + n_column]
    df[id_columns] = df[id_columns].applymap(str.upper)
    df = df.set_index(id_columns)
    df = df.loc[target]
    if ihid:
        df = df.loc[ihid]
        if iid:
            df = df.loc[iid]
    if minimal:
        # return df.index.unique().to_frame().reset_index(drop=True)
        return df.drop(ok_columns, axis=1)
    return df


def search(bbox, target, ihid, iid, pt, match='contain'):
    resjs = _search(bbox, target, ihid, iid, pt, match)
    try:
        out = _get_ps(resjs)
    except:
        return None
    else:
        return out


def _get_ps(resjs):
    if not resjs:
        return None
    products = resjs['ODEResults']['Products']['Product']
    # If only one data product is found, 'products' is not a list; fix this
    products = products if isinstance(products, (list,tuple)) else [products]
    return products


def _search(bbox, target, ihid, iid, pt, match='contain'):
    from gpt.helpers import Bbox

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

    resjs = _request(_API_URL, params)
    return resjs


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

    res = requests.get(_API_URL, _params)

    # If response is not a round 200, fail it
    if res.status_code != 200:
        print('Request response failed:', str(res))
        return None

    js = res.json()

    # If response is valid (200) but ODE itself failed to respond the query, alert user
    if js['ODEResults']['Status'].lower() != 'success':
        print("Returned result says 'ODEResults'/'Status' != 'success'. Check for more info.")

    return js


def unstack(products: list, field: str, products_mapping=None):
    mapping = products_mapping
    _products = []
    for product in products:
        _product = {k:v for k,v in product.items() if k not in field}
        if mapping is None:
            content_to_unstack = product[field]
        elif isinstance(mapping, dict):
            files = product[field]
            _d_ = {v[0]:ff[v[1]] for ff in files for k,v in mapping.items() if ff[k[0]]==k[1]}
            content_to_unstack = [_d_]
        else:
            assert callable(products_mapping)
            content_to_unstack = [products_mapping(product[field])]

        _products.extend([ dict(_product, **ukw) for ukw in content_to_unstack ])

    return _products


def to_geodataframe(products: list, geometry_field='Footprint_C0_geometry',
                    exclude_footprints=True, unstack_field='product_files',
                    unstack_function=None):
    import geopandas
    import shapely

    assert isinstance(products, list)

    _products = []
    for product in products:

        fields_to_exclude = set()
        content_to_unstack = None
        # if unstack_field:
        #     content_to_unstack = product[unstack_field]
        #     fields_to_exclude.add(unstack_field)
        if exclude_footprints:
            fields_to_exclude.update(set(filter(lambda f:'footprint' in f.lower(), product.keys())))

        _product = {k:v for k,v in product.items() if k not in fields_to_exclude}

        if geometry_field and geometry_field in product:
            geometry = product[geometry_field]
            try:
                geometry = shapely.wkt.loads(geometry)
            except TypeError as err:
                raise err
            _product['geometry'] = geometry

        if content_to_unstack:
            assert False
            assert isinstance(content_to_unstack, list)
            _products.extend([ dict(_product, **ukw) for ukw in content_to_unstack ])
        else:
            _products.append(_product)

    if unstack_field:
        _products = unstack(_products, unstack_field, unstack_function)

    gdf = geopandas.GeoDataFrame(_products)
    return gdf


def to_geojson(products: list, geometry_field='Footprint_C0_geometry',
                exclude_footprints=True, unstack_field='product_files',
                output_filename=None):
    import json
    gdf = to_geodataframe(products, geometry_field, exclude_footprints, unstack_field)
    return geodataframe_to_geojson(gdf, output_filename)


def geodataframe_to_geojson(gdf, output_filename=None):
    gjs = gdf.to_json()
    assert isinstance(gjs, str)
    if output_filename:
        with open(output_filename, 'w') as fp:
            fp.write(gjs)
        return output_filename
    else:
        return json.loads(gjs)


def parse_products(resjs, meta_selectors=None, data_selectors=None,
                    meta_select_how='keep', data_select_how='all',
                    include_notes=True, include_footprints=True):
    """
    Apply filters and remove exceeding object nesting from ODE results or already parsed results

    This function also accepts already parsed products (output from this function).

    This function was primarily meant to remove the exceeding nesting levels of
    'Products_files' and 'ODE_notes' from ODE-REST results. Then grew to filter
    or exclude certain fields ('meta_selectors', 'include_notes/footprints'),
    and select data files according to some criteria ('data_selectors','data_select_how').

    Input:
        resjs : list
            Content from ODE-REST result' ['ODEResults']['Products']['Product'].
        meta_selectors : list [string,]
            List of fields to keep or remove, according to 'meta_select_how'.
            Does not apply for "footprint_*" fields, "Product files" or "Notes",
            see 'include_notes' and 'include_footprints' for those.
        meta_select_how : string ('keep', 'exclude')
            What to do to/if given 'meta_selectors'. Options are ['keep','exclude'].
        data_selectors : dictionary {string:string}
            Applys to "Product files", for filtering data/files of interest.
            Which fields to consider (key) and which regular expression to look for (value).
            Values can be a string of list of strings.
        data_select_how : string ('any', 'all')
            If 'all', select data/files matching all 'data_selectors' keys.
            If 'any', select data/files matching any 'data_selectors' key.
        include_notes : bool
            If True, keep 'ODE_notes' or 'notes', and rename it to 'notes'
        include_footprints : bool
            If True, keep 'footprint_*' fields.

    Output:
        List of products with filter applied, if any, ['Product_files']['Products']
        as ['product_files'] and ['ODE_notes']['notes'] as ['notes']
    """

    assert meta_select_how in ('keep','exclude'), f"Expected 'keep' or 'exclude', got {meta_select_how} instead."
    assert data_select_how in ('any','all'), "Expected to have 'all' or 'any' for 'match_selector'"

    selectors_not_found= set()
    products = []
    for product in resjs:
        meta = {}
        notes = None if 'notes' not in product else product['notes']
        files = None if 'product_files' not in product else product['product_files']
        for key,value in product.items():
            if include_footprints and 'footprint' in key.lower():
                meta[key] = value
                continue
            if key == 'Product_files' or key == 'product_files':
                files = product[key]['Product_file'] if files is None else files
                if data_selectors:
                    match_all = True if data_select_how == 'all' else False
                    files = select_files(files, data_selectors, match_all)
                continue
            if key == 'ODE_notes':
                notes = product[key]['ODE_note']
                continue
            if meta_selectors:
                assert isinstance(meta_selectors, (list,tuple))
                selectors_not_found.update(set(filter(lambda f:f not in product, meta_selectors)))
            if (meta_selectors is None
                or (key in meta_selectors and meta_select_how == 'keep')
                or (key not in meta_selectors and meta_select_how == 'exclude')):
                    meta[key] = value

        if not files:
            continue
        meta['product_files'] = files
        if include_notes:
            meta['notes'] = notes
        products.append(meta)

    if selectors_not_found:
        print("WARNING: selectors not found:", list(selectors_not_found))

    return products


def select_files(product_files: list, data_selectors: dict, match_all=True) -> list:
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



# def _set_payload(bbox, target=None, host=None, instr=None, ptype=None, how='intersect'):
#     payload = dict(
#         query='product',
#         results='fmpc',
#         output='JSON',
#         loc='f',
#         minlat=bbox['minlat'],
#         maxlat=bbox['maxlat'],
#         westlon=bbox['westlon'],
#         eastlon=bbox['eastlon']
#     )
#
#     if target:
#         payload.update({'target':target})
#     if host:
#         payload.update({'ihid':host})
#     if instr:
#         payload.update({'iid':instr})
#         if ptype:
#             payload.update({'pt':ptype})
#
#     if 'contain' in how:
#         payload.update({'loc':'o'})
#
#     return payload
