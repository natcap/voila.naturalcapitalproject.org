import logging
import os

import pygeoprocessing
import shapely
from ipyleaflet import Rectangle
from osgeo import gdal
from osgeo import osr

gdal.DontUseExceptions()

WGS84_SRS = osr.SpatialReference()
WGS84_SRS.ImportFromEPSG(4326)
LOGGER = logging.getLogger(os.path.basename(__file__))


def leaflet_rectangle_from_bbox(bbox):
    shapely_geom = shapely.geometry.shape(bbox)
    minx, miny, maxx, maxy = shapely_geom.bounds
    bbox_layer = Rectangle(
        name="Bounding box",
        bounds=[(miny, minx), (maxy, maxx)],
        color='black',
        fill=False,
        weight=1,  # default=5
    )
    return bbox_layer


def compute(source_raster_path, aoi_geom, target_epsg, target_raster_path,
            target_pixel_size):
    LOGGER.info(f"Starting to clip {source_raster_path}")
    LOGGER.info(f"Using target EPSG:{target_epsg}")
    # Clip the source raster to the target bounding box in WGS84
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(int(target_epsg))
    target_srs_wkt = target_srs.ExportToWkt()
    LOGGER.info(f"Source SRS WKT: {WGS84_SRS.ExportToWkt()}")
    LOGGER.info(f"Target SRS WKT: {target_srs_wkt}")
    source_bbox = shapely.geometry.shape(aoi_geom).bounds
    LOGGER.info(f"Source bbox: {source_bbox}")
    target_bbox = pygeoprocessing.transform_bounding_box(
        bounding_box=source_bbox,
        base_projection_wkt=WGS84_SRS.ExportToWkt(),
        target_projection_wkt=target_srs_wkt,
    )
    LOGGER.info(f"Bounding box converted to EPSG:{target_epsg} is "
                f"{target_bbox}")

    LOGGER.info("Warping to the target bounding box")
    LOGGER.info(f"Target pixel size:{target_pixel_size}")
    LOGGER.info(f"Target bounding box: {target_bbox}")
    pygeoprocessing.warp_raster(
        base_raster_path=source_raster_path,
        target_pixel_size=target_pixel_size,
        target_raster_path=target_raster_path,
        resample_method='near',
        target_projection_wkt=target_srs_wkt,
        target_bb=target_bbox,
    )
    LOGGER.info('Finished warping')
    LOGGER.info(f"Clipped raster available at {target_raster_path}")
