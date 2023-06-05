import json
import logging
import sys

logging.basicConfig(level=logging.INFO)

import numpy
import pygeoprocessing
from osgeo import gdal

source_raster = sys.argv[1]
target_raster = sys.argv[2]
stats_json_file = sys.argv[3]

nodata = pygeoprocessing.get_raster_info(source_raster)['nodata'][0]

minimum = float('inf')
maximum = float('-inf')

for data, block in pygeoprocessing.iterblocks((source_raster, 1)):
    if nodata is not None:
        valid_pixels = ~numpy.isclose(block, nodata)
    else:
        valid_pixels = numpy.ones(block.shape, dtype=bool)

    minimum = min(block[valid_pixels].min(), minimum)
    maximum = max(block[valid_pixels].max(), maximum)

def rescale(block):
    if nodata is not None:
        valid_pixels = ~numpy.isclose(block, nodata)
    else:
        valid_pixels = True
    target = numpy.full(block.shape, -1, dtype=numpy.uint8)

    target[valid_pixels] = numpy.interp(block[valid_pixels], (minimum, maximum), (0, 254))

    return target

pygeoprocessing.raster_calculator(
    [(source_raster, 1)], rescale, target_raster, gdal.GDT_Int16, -1
)

with open(stats_json_file, 'w') as stats_json:
    json.dump({'minimum': int(minimum), 'maximum': int(maximum)}, stats_json)
