import io
import requests
import argparse
import pandas as pd
import shapely.geometry
import geopandas as gpd
import matplotlib.pyplot as plt

from zipfile import ZipFile
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon


def download_population_data(verbose=False):
    url = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/" \
          "BulkDownloadListing?file=data/demo_r_pjangrp3.tsv.gz"
    if verbose:
        print(f"Downloading {url}")
    
    df = pd.read_csv(url, delimiter='\t', low_memory=False)
    df = df.rename(columns={df.columns[0]: 'nuts_id'})
    df = df[df['nuts_id'].str.startswith('T,NR,TOTAL')]
    df['nuts_id'] = df['nuts_id'].str.split(',').str[-1]
    df = df.set_index('nuts_id')

    df.columns = [c.strip() for c in df.columns]
    df = df.applymap(lambda item: 
            float(item.split()[0]) if ':' not in item else None)
    df = df.fillna(method='backfill', axis=1)

    return df


def download_nuts_regions(resolution="60m", verbose=False):
    if resolution not in ["01m", "03m", "10m", "20m", "60m"]:
        raise ValueError("resolution not available")
    
    base_url = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/download/"

    gdf_list = []
    for year in ['2013', '2016']:
        url = base_url + f"ref-nuts-{year}-{resolution}.geojson.zip"
        if verbose:
            print(f"Downloading {url}")
        
        r = requests.get(url, verify=True)
        r.raise_for_status()
        with ZipFile(io.BytesIO(r.content)) as z:
            for nuts_level in range(4):
                filename = f"NUTS_RG_{resolution.upper()}_{year}_4326_LEVL_{nuts_level}.geojson"
                if verbose:
                    print(f"\tExtracting {filename}")
                
                with z.open(filename) as f:
                    gdf_list.append(gpd.read_file(f, driver='GeoJSON'))

    gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=False), crs=gdf_list[0].crs)
    gdf = gdf.drop_duplicates(subset=['NUTS_ID'], keep='first')
    gdf.columns = [c.lower() for c in gdf.columns]
    
    return gdf


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Download and prepare Eurostat NUTS regions with population data")
    parser.add_argument(
        'filepath', type=str, help='destination filepath')
    parser.add_argument(
        '-r', '--resolution', type=str, action='store', default='60m',
        help='set NUTS region resolution (01m, 03m, 10m, 20m, 60m)')
    parser.add_argument(
        '-v', '--verbose', action='store_true', 
        help='verbose output')
    args = parser.parse_args()
    
    if not any(args.filepath.endswith(ext) for ext in [".json", '.geojson', '.gpkg']):
        print("File extension not supported")
        exit(-1)
    
    if args.resolution not in ["01m", "03m", "10m", "20m", "60m"]:
        print("File extension not supported")
        exit(-1)
    
    # Download data
    df_pop = download_population_data(verbose=args.verbose)
    gdf_nuts = download_nuts_regions(args.resolution, verbose=args.verbose)
    
    # Merge data
    s_pop = df_pop['2020'].dropna()
    s_pop.name = 'population'
    gdf = gdf_nuts.join(s_pop, on='nuts_id')
    gdf = gdf.drop(columns=['mount_type', 'urbn_type', 'coast_type', 'id', 'fid'])
    
    # Convert Polygons to Multipolygons
    gdf.geometry = gdf.geometry.apply(
        lambda geom: MultiPolygon([geom]) if isinstance(geom, Polygon) else geom)
    
    if args.verbose:
        gdf.info(memory_usage='deep')
    
    # Save data
    if args.filepath.endswith(".gpkg"):
        gdf.to_file(args.filepath, driver="GPKG", index=False)
    elif args.filepath.endswith(".geojson") or args.filepath.endswith(".json"):
        gdf.to_file(args.filepath, driver="GeoJSON", index=False)
