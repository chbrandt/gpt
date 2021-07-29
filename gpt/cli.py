import click

import gpt.search 


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    Gpt command-line interface to search and handle planetary data
    """
    pass

@cli.command()
@click.argument('api', required=False)
@click.argument('target', required=False)
@click.option('--list', is_flag=True, default=False, help="List the available arguments for api/target")
@click.option('--bbox', is_flag=False, default=None, help="Bounding-box '[westLon, minLat, eastLon, maxLat]'")
@click.pass_context
def search(ctx, api:str, target:str, list:bool, bbox:str):
    """
    Search-related commands, query 'api' for data products

    API and TARGET arguments are fundamental for data products search,
    but to know which APIs are available, use the "list" option flag without those arguments:
    ```
    search --list
    ```

    Target is a planetary body name or a dataset designation.
    Datasets are written like "mars/mro/ctx/edr" and define the specific dataset you want
    to make products search (e.g, "bbox")
    """
    if target is None:
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

    target_array = target.split('/')
    assert 1 <= len(target_array) <= 4

    body = ihid = iid = pt = None

    if len(target_array) > 1:
        if len(target_array) >= 2:
            ihid = target_array[1]
        if len(target_array) >= 3:
            iid = target_array[2]
        if len(target_array) >= 4:
            pt = target_array[3]
    body = target_array[0]

    assert hasattr(gpt.search, api), f"Got '{api}', expected one of {gpt.search.available_apis()}"
    search_api = getattr(gpt.search, api)

    complete = body and ihid and iid and pt
    if list or not complete:
        dsets = search_api.available_datasets(body,ihid,iid, minimal=True)
        click.echo(dsets.to_csv(sep=' '))
        return True

    if bbox is None:
        click.echo("Define a bounding-box to search in the dataset. E.g, '[-1,-1,1,1]'")
        return False

    bbox = bbox.replace('[','').replace(']','')
    click.echo(search_api.search(bbox,body,ihid,iid,pt))
    
