# Geo-Planetary Tools

> This is under development

## Modules

### Search

GPT's `search` API provides search capabilities to geo-located (planetery) data services.
The following databases are currently supported:

- USGS's ODE REST interface

#### CLI

List available service APIs:

```bash
$ gpt search --list-apis
'ode'
```

List ODE's available Martian datasets:

```bash
$ gpt search ode Mars --list-datasets
...
MRO/CTX/EDR
MRO/HIRISE/RDRV11
...
```

Query ODE for martian datasets:

```bash
$ gpt search ode Mars/MRO/CTX/EDR --bbox "[-1,-1,1,1]" --no-intersect 
15 products found.
Output written to 'output.gjsn'
```

### GeoJSON

List GeoJSON feature properties:

```bash
$ gpt geojson 'collection.gjsn' --list-properties
file_url  (21/42 features)
label_url (21/42 features)
description
```

### Download

Utils to download files.

#### CLI

Download files from URLs given after `fileurl` in GeoJSON features:

```bash
$ gpt download --from-geojson 'products.geojson' --from-field 'fileurl' --to-geojson 'download.gjsn' --to-dir './data/' 
...
21 files downloaded from field 'fileurl'.
21 features excluded.
Output written to 'download.gjsn'
```

Download files from URLs at `fileurl` with a filter at `description`:

```bash
$ gpt download --from-geojson 'products.geojson' --from-field 'fileurl' --filter-field 'description' --filter-with 'label'
42 features excluded.
Output written to 'output.geojson'
```

Tools for daily operations on geo-(planetary)-sciences.

## Developers

### Install

```
# pip install -e .
```


/.\
