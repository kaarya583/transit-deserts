"""
GTFS data ingestion module.

Purpose: Load and clean GTFS feeds (bus + rail) to create stop GeoDataFrames.

Output: Clean stop GeoDataFrames with CRS normalization.
"""

import geopandas as gpd
import pandas as pd
import gtfs_kit as gk
from pathlib import Path
from zipfile import ZipFile
import warnings
warnings.filterwarnings('ignore')

# Import config - assume we're in src/ingest/, so go up two levels to project root
import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root / "src"))
import config


def load_gtfs_feeds(data_dir=None):
    """
    Load GTFS feeds from data_raw directory.
    
    Returns:
        dict: {'bus': gk.Feed, 'rail': gk.Feed} or None if not found
    """
    if data_dir is None:
        data_dir = config.DATA_RAW
    
    feeds = {}
    
    # Look for bus GTFS
    bus_files = list(data_dir.glob("*bus*gtfs*.zip"))
    if bus_files:
        feeds['bus'] = gk.read_feed(bus_files[0], dist_units='km')
        print(f"✓ Loaded bus GTFS: {bus_files[0].name}")
    
    # Look for rail GTFS
    rail_files = list(data_dir.glob("*rail*gtfs*.zip"))
    if rail_files:
        feeds['rail'] = gk.read_feed(rail_files[0], dist_units='km')
        print(f"✓ Loaded rail GTFS: {rail_files[0].name}")
    
    if not feeds:
        print("⚠ No GTFS files found")
        return None
    
    return feeds


def extract_stops(feeds):
    """
    Extract stops from GTFS feeds and combine into single GeoDataFrame.
    
    Args:
        feeds: dict of gk.Feed objects
        
    Returns:
        gpd.GeoDataFrame: All stops with geometry
    """
    all_stops = []
    
    for mode, feed in feeds.items():
        if feed.stops is not None and len(feed.stops) > 0:
            stops = feed.stops.copy()
            stops['mode'] = mode
            all_stops.append(stops)
    
    if not all_stops:
        raise ValueError("No stops found in GTFS feeds")
    
    # Combine
    stops_df = pd.concat(all_stops, ignore_index=True)
    
    # Create geometry from lat/lon
    stops_gdf = gpd.GeoDataFrame(
        stops_df,
        geometry=gpd.points_from_xy(
            stops_df['stop_lon'],
            stops_df['stop_lat'],
            crs=config.GEOGRAPHIC_CRS
        )
    )
    
    # Filter to LA County extent (rough bounding box)
    la_bbox = {
        'min_lon': -118.7,
        'max_lon': -117.9,
        'min_lat': 33.7,
        'max_lat': 34.8
    }
    
    stops_gdf = stops_gdf.cx[
        la_bbox['min_lon']:la_bbox['max_lon'],
        la_bbox['min_lat']:la_bbox['max_lat']
    ]
    
    print(f"✓ Extracted {len(stops_gdf):,} stops")
    print(f"  Bus stops: {(stops_gdf['mode'] == 'bus').sum():,}")
    print(f"  Rail stops: {(stops_gdf['mode'] == 'rail').sum():,}")
    
    return stops_gdf


def save_stops(stops_gdf, output_path=None):
    """
    Save stops GeoDataFrame to GeoJSON.
    
    Args:
        stops_gdf: GeoDataFrame of stops
        output_path: Path to save (default: data_processed/stops_all.geojson)
    """
    if output_path is None:
        output_path = config.DATA_PROCESSED / "stops_all.geojson"
    
    stops_gdf.to_file(output_path, driver='GeoJSON')
    print(f"✓ Saved stops to {output_path}")


def ingest_gtfs(data_dir=None, save=True):
    """
    Main function: Ingest GTFS data and return stops GeoDataFrame.
    
    Args:
        data_dir: Directory containing GTFS files (default: config.DATA_RAW)
        save: Whether to save output (default: True)
        
    Returns:
        gpd.GeoDataFrame: All transit stops
    """
    # Load feeds
    feeds = load_gtfs_feeds(data_dir)
    if feeds is None:
        raise FileNotFoundError("No GTFS feeds found")
    
    # Extract stops
    stops_gdf = extract_stops(feeds)
    
    # Save if requested
    if save:
        save_stops(stops_gdf)
    
    return stops_gdf


if __name__ == "__main__":
    # Test ingestion
    stops = ingest_gtfs()
    print(f"\n✓ GTFS ingestion complete")
    print(f"  Total stops: {len(stops):,}")

