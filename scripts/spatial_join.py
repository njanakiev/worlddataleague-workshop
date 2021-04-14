import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin


if __name__ == '__main__':
    amenity_filepath = "data/europe-amenity.csv.gz"
    nuts_filepath = "data/nuts_60m.gpkg"
    dst_filepath = "data/europe-amenity-counts.csv.gz"
    verbose = True

    # Read amenity locations
    gdf_amenity = pd.read_csv(
        amenity_filepath, 
        usecols=['amenity', 'lon', 'lat'])

    gdf_amenity = gpd.GeoDataFrame(
        gdf_amenity,
        geometry=gpd.points_from_xy(gdf_amenity.lon, gdf_amenity.lat), 
        crs="epsg:4326").drop(columns=['lon', 'lat'])
    gdf_amenity.sindex
    if verbose:
        gdf_amenity.info(memory_usage='deep')

    # Read nuts regions
    gdf_nuts = gpd.read_file(
        nuts_filepath, 
        ignore_fields=[
            'levl_code', 'cntr_code', 
            'name_latn', 'nuts_name',
            'population'],
        driver='GPKG')
    gdf_nuts.sindex
    if verbose:
        gdf_nuts.info(memory_usage='deep')

    # Spatial join
    gdf = sjoin(gdf_nuts, gdf_amenity, how='left')
    gdf.info(memory_usage='deep')

    # Group by and count
    s_counts = gdf.groupby(['nuts_id', 'amenity'])['geometry'].count()
    s_counts.name = "counts"
    df_counts = s_counts.reset_index()
    if verbose:
        df_counts.info(memory_usage='deep')

    # Save counts
    df_counts.to_csv(dst_filepath, compression='gzip', index=False)
