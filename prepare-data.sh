set -e

# Install osmium-tool for later use
sudo apt update
sudo apt install osmium-tool

# Download planet OSM if it does not exist
# https://planet.openstreetmap.org/
if [ ! -f data/planet-latest.osm.pbf ]; then
  time wget https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf \
    --quiet -O data/planet-latest.osm.pbf
fi

# Filter by amenity tag with osmium-tool
# https://osmcode.org/osmium-tool/
if [ ! -f data/planet-amenity.osm.pbf ]; then
  time osmium tags-filter \
    data/planet-latest.osm.pbf amenity \
    -o data/planet-amenity.osm.pbf
fi

# Get the most popular tags from taginfo
# taginfo.openstreetmap.org/
if [ ! -f data/taginfo_amenity_counts.csv ]; then
  python scripts/taginfo.py -v amenity \
    data/taginfo_amenity_counts.csv
fi

# Download and prepare NUTS regions including population
if [ ! -f data/nuts_60m.gpkg ]; then
  python scripts/eurostat_nuts.py -v \
    --resolution 60m \
    data/nuts_60m.gpkg
fi

# Extract centroids from amenities
if [ ! -f data/europe-amenity.csv.gz ]; then
  python scripts/extract.py
fi

# Perform spatial join between amenities and NUTS regions
if [ ! -f data/europe-amenity-counts.csv.gz ]; then
  python scripts/spatial_join.py
fi

# Calculate normalized amenity features based on population
if [ ! -f data/europe-amenity-features.csv.gz ]; then
  python scripts/features.py
fi
