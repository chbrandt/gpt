import click

import gpt.search 
import gpt.download


@click.group()
@click.pass_context
def cli(ctx):
    """
    Gpt command-line interface to search and handle planetary data
    """
    pass

@cli.command()
@click.argument('api', required=False)
@click.argument('dataset', required=False)
@click.option('--list', is_flag=True, default=False, help="List the available arguments for api/target")
@click.option('--bbox', is_flag=False, default=None, help="Bounding-box '[westLon, minLat, eastLon, maxLat]'")
@click.option('--intersect/--no-intersect', is_flag=True, default=True, help="Consider data products intersecting/not the bounding-box")
@click.option('--output', default='output_search.geojson')
@click.pass_context
def search(ctx, api:str, dataset:str, list:bool, bbox:str, intersect:bool, output:str):
    """
    Search-related commands, query 'api' for data products

    API and DATASET arguments are fundamental for data products search,
    but to know which APIs are available, use the "list" option flag without those arguments:
    ```
    search --list
    ```

    Dataset is a '/' separated string specifying anywhere from a planetary body name 
    or a dataset volume designation, like is ODE's. Possible values are given by the API.

    # ODE
    The 'ode' API needs at least a planet/sattelite name, eg 'Mars', (as 'dataset').
    And a complete specification of a 'dataset' is a size-4 string (eg, 'mars/mro/ctx/edr').
    All the possibilities of 'dataset' available can be listed using 'list=True'.
    
    Data products are search per dataset volume, complete specifiction, in the case of ODE
    datasets are defined all the way down to product-type (eg, 'mars/mro/hirise/rdrv11').
    """
    if dataset is None:
        if api is None:
            if list:
                apis = gpt.search.available_apis()
                click.echo(f"Available APIs:\n{apis}")
                return True
            else:
                click.echo(ctx.get_help())
                return False
        else:
            assert api
            if list:
                click.echo("Possible targets are 'mars', 'moon', 'mercury', etc.")
                return True
            else:
                # I'm gonna use the same message but could/should be different
                click.echo("Possible targets are 'mars', 'moon', 'mercury', etc.")
                return False


    search_init = gpt.search.get_api(api)
    search_api = search_init(dataset)

    if list:
        dsets = search_api.available_datasets(minimal=True)
        click.echo(dsets.to_csv(sep=' '))
        return True

    if not search_api.ready():
        click.echo("Dataset not fully defined, use '--list' to specify better")
        return False

    if bbox is None:
        click.echo("Define a bounding-box to search in the dataset. E.g, '[-1,-1,1,1]'")
        return False

    bbox = bbox.replace('[','').replace(']','')

    # The block above should all go inside an API -- ODE, for instance -- search function.
    # The code in here must go directly to calling the "bbox" function, for instance.
    #
    res = search_api.bbox(bbox, intersect)
    
    click.echo(f"{res.count} product(s) found.")

    res.to_geojson(output)

    return True


@cli.command()
@click.argument('geojson')
@click.argument('property')
@click.option('--to-dir', default='./data/', help="Directory to download data to")
@click.option('--to-property', required=False, default=None, help="Save the path where data products are downloaded")
@click.option('--to-geojson', required=False, default=None, help="Filename of output GeoJSON with updated properties")
@click.pass_context
def download(ctx, geojson, property, to_dir, to_property, to_geojson):
    """
    Download files from GeoJSON features' property providing URL paths.
    """ 
    gpt.download.from_geojson(geojson, property, to_dir, to_property, to_geojson)
    return True