#!/bin/python																										#
# -*- coding: utf-8 -*-																								#
# Author: 		S. Crommelinck, 2017																				#
# Description: 	This script converts a binary (gPb) raster to a vector file containing the centerlines for connected#
#               cells having a value of 1 (i.e. the gPb contour lines).                                             #
# QGIS Version: QGIS 2.18																							#
#####################################################################################################################

### Import script in QGIS Python console ###
"""
#Add directory with script to Python search path
import sys
sys.path.append(r"D:\...\directory_of_script")

#import own module
import A3_raster_to_centerline

#another run after changing the source code
reload(A3_raster_to_centerline)
"""

### Predefine variables ###

gPb = r"D:\..>\path_to_gPb_raster_file"

data_dir= r"D:\..>\data_directory"

########################################################################################################################

### Import required modules ###
import qgis
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import *
from qgis.analysis import *
import processing
from osgeo import ogr

### Main processing part ###
# Change into data directory
os.chdir(data_dir)

# Load raster
fileInfo = QFileInfo(gPb)
path = fileInfo.filePath()
baseName = fileInfo.baseName()
gPb_rlayer = QgsRasterLayer(path, baseName)
if not gPb_rlayer.isValid():
  print "--> ERROR: gPb layer failed to load."
else:
    print "--> gPb layer successfully loaded.\n"

# Define extent
extent = gPb_rlayer.extent()
xmin = extent.xMinimum()
xmax = extent.xMaximum()
ymin = extent.yMinimum()
ymax = extent.yMaximum()

### Replace all no data values ###
mapcalc = data_dir + r"\gPb_mapcalc.tif"
if not os.path.isfile(mapcalc):
    processing.runalg('grass:r.mapcalculator',
                      {"amap": gPb_rlayer,
                       "formula": "if(A>0, 1, null())",
                       "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                       "GRASS_REGION_CELLSIZE_PARAMETER": 1,
                       "outfile": mapcalc})

    print "--> successfully applied mapcalc.\n"

### Thin raster layer to thin non-null cells ###
thinned = data_dir + r"\gPb_thinned.tif"
if not os.path.isfile(thinned):
    processing.runalg('grass7:r.thin',
                      {"input": mapcalc,
                       "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                       "output": thinned})

    print "--> successfully applied thinning.\n"

### Raster to vector conversion (-> lines) ###
centerlines = data_dir + r"\gPb_centerlines.shp"
if not os.path.isfile(centerlines):
    processing.runalg('grass7:r.to.vect',
                      {"input": thinned,
                       "type": 0,
                       "GRASS_OUTPUT_TYPE_PARAMETER": 2,
                       "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                       "output": centerlines})

    print "--> successfully created centerlines.\n"

### Raster to vector conversion (-> areas) ###
# centerlines = data_dir + r"\gPb_areas.shp"
# if not os.path.isfile(centerlines):
#     processing.runalg('grass7:r.to.vect',
#                       {"input": thinned,
#                        "type": 2,
#                        "GRASS_OUTPUT_TYPE_PARAMETER": 3,
#                        "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
#                        "output": centerlines})
#
#     print "--> successfully created centerlines.\n"


### Helping resources ###
# In QGIS:
# import processing
# processing.alghelp("grass7:r.to.vect")
# processing.alglist("g.extension")
