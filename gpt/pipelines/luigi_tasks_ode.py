"""
Luigi runs a serial pipeline defined by _tasks_ based on files as I/O and as triggers.
"""
import luigi
import json
import logging

logger = logging.getLogger('luigi-interface')


class SearchProductTask(luigi.Task):
    """
    Parameters:
    - productid: str
    - dataset: str
        Example: 'mars/mro/ctx/edr' or 'mars/mex/hrsc/refdr3'
    - output_geojson: str
        Filename for search results, each data product as a feature
    """
    productid = luigi.Parameter()
    dataset = luigi.Parameter()
    output_geojson = luigi.Parameter()
    
    def output(self):
        return luigi.LocalTarget(self.output_geojson)
    
    def run(self):
        from gpt import search
    
        search.product('ode', 
                        productid=self.productid,
                        dataset=self.dataset,
                        output=self.output_geojson,
                        intersect=self.intersect
                    )
                    
class SearchBboxTask(luigi.Task):
    """
    Parameters:
    - bounding_box: str
        Format: '{westlon},{minlat},{eastlon},{maxlat}'
    - dataset: str
        Example: 'mars/mro/ctx/edr' or 'mars/mex/hrsc/refdr3'
    - output_geojson: str
        Filename for search results, each data product as a feature
    - intersect: bool
        If True, any footprint intersecting the bounding-box is considered,
        otherwise (False), consider only data product fully inside bounding-box.
    """
    bounding_box = luigi.DictParameter()
    dataset = luigi.Parameter()
    output_geojson = luigi.Parameter()
    intersect = luigi.BoolParameter(default=True)
    
    def output(self):
        return luigi.LocalTarget(self.output_geojson)
    
    def run(self):
        from gpt import search
        bounding_box = dict(self.bounding_box)
        logger.debug(f"{type(bounding_box)} : {self.bounding_box}")
        res = search.bbox(api='ode', 
                    bbox=bounding_box,
                    dataset=self.dataset,
                    intersect=self.intersect
                    )

        with self.output().open('w') as fp:
            json.dump(res, fp)
    
    
    
class DownloadProductTask(luigi.Task):
    """Download data products and resp. metadata
    
    Input:
    - productid: str
    - dataset: str
    - base_dir: str
    """
    productid = luigi.Parameter()
    dataset = luigi.Parameter()
    base_dir = luigi.Parameter()
    url_property = luigi.Parameter(default='image_url')
    filename_property = luigi.Parameter(default='image_path')

    def requires(self):
        """Require a search through an API/DB. Curently, USGS/ODE"""
        return SearchProductTask(productid=self.productid, dataset=self.dataset)

    def output(self):
        return luigi.LocalTarget()

    def run(self):
        """
        Download the product (image) from searching ODE'
        """
        from gpt import download
        geojson = json.loads(self.input().open('r'))
        feature = json.loads(self.geofeature)
        url = feature['properties'][self.url_property]
        filename = download.url(url, self.base_dir)
        new_feature = feature['properties'].copy()
        new_feature.update({self.filepath_property:filename})

        from gpt import download
        new_feature = download.feature(geofeature, self.base_dir, url_key=self.url_property, output_key=self.filename_property)
        
        with self.output().open('w') as ofile:
            json.dump(new_feature, ofile)

            
class DownloadFeatureTask(luigi.Task):
    """
    Input:
    - geofeature (from geojson): string
    - base_dir (base dir): string
    - url_property: str
        Product's URL, where to download from
    - filepath_property: str
        Product's path keyword to be added to the new feature
    
    Output:
    - (LocalTarget): name of updated 'feature.download.json' filename (at download_dir)
    """
    geofeature = luigi.Parameter()
    base_dir = luigi.Parameter()
    url_property = luigi.Parameter(default='image_url')
    filepath_property = luigi.Parameter(default='image_path')
    
    def output(self):
        # This code about 'prodid' should be better, remove at some point
        prodid = json.loads(self.geofeature)['properties']['id']
        print("# --- DOWNLOAD output")
        print("# - Task family:",self.get_task_family())
        print("# - Task namespace:",self.get_task_namespace())
        print("# - Task ID:",self.task_id)
        print("# Feature: ",self.geofeature)
        print("# - ProdID:",prodid)
        output_filename = self.base_dir +'/'+ prodid + '.download.json'
        return luigi.LocalTarget(output_filename)
    
    def run(self):
        """
        Download the product (image) from search's GeoJSON 'feature:properties:image_url'
        """
        from gpt import download
        feature = json.loads(self.geofeature)
        url = feature['properties'][self.url_property]
        filename = download.url(url, self.base_dir)
        new_feature = feature['properties'].copy()
        new_feature.update({self.filepath_property:filename})
        
        with self.output().open('w') as ofile:
            json.dump(new_feature, ofile)
    
class DownloadGeojsonTask(luigi.Task):
    """
    Download files in GeoJSON features (from ODE, for instance)
    
    Parameters:
    - input_geojson: str
    - output_geojson: str
    """
    input_geojson = luigi.Parameter()
    output_geojson = luigi.Parameter()
    base_dir = luigi.Parameter()
    url_property = luigi.Parameter(default='image_url')
    
    def requires(self):
        for feature in json.load(open(self.input_geojson,'r'))['features']:
            yield DownloadFeatureTask(json.dumps(feature))
    
    def output(self):
        return luigi.LocalTarget(self.output_geojson)
    
    def run(self):
        """Update input geojson features with 'image_path'"""
        geojson = [json.load(open(filename,'r').read()) for filename in self.input()]
    
class ReducedTask(luigi.Task):
    """
    Input:
    - feature (from geojson): string
    - reduced_dir (base dir): string
    
    Output:
    - (LocalTarget): name of updated 'feature.json' filename (at download_dir)
    """
    feature = luigi.Parameter()
    base_dir = luigi.Parameter()
    temp_dir = luigi.Parameter()
    datasetId = luigi.Parameter()
    
    def requires(self):
        print("# --- REDUCED requires")
        print("Task family:",self.get_task_family())
        print("Task namespace:",self.get_task_namespace())
        print("Task ID:",self.task_id)
        print(self.feature)
        return DownloadFeatureTask(self.feature, base_dir=self.base_dir)
    
    def output(self):
        print("# --- REDUCED output")
        print("# - Task family:",self.get_task_family())
        print("# - Task namespace:",self.get_task_namespace())
        print("# - Task ID:",self.task_id)
        print("#",self.feature)
#         prodid = '.'.join(json.load(self.input().open('r'))['properties']['image_url'].split('/')[-1].split('.')[:-1])
        prodid = json.loads(self.feature)['properties']['id']
        print("# - ProdID:",prodid)
        return luigi.LocalTarget(self.base_dir +'/'+ prodid + '.reduced.json')
    
    def run(self):
        #from npt import isis
        #isis.sh.set_docker('isis3', {'reduced_data': [base_data_path.as_posix(), '/data']})
        
        from npt.pipelines import processing
        new_feature = processing.run(json.load(self.input().open('r')), output_path=self.base_dir, tmpdir=self.temp_dir, datasetId=self.datasetId)
        
        with self.output().open('w') as ofile:
            json.dump(new_feature, ofile)
    