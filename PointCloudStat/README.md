# This Directory contains the XXXXX module

### Name ideas:
PointCloudStat
SFMtoGrid
ConfidentChange
The above aren't great so ideas welcome!
##
### DSM module

The DSM module has one function called'height_map' which allows for the derivation of a Digital Surface Model (DSM) from 
a point cloud. It uses the mean point height (z) within each grid square to define the elevation of the raster cells 
(Band 1). The standard deviation of point elevations is calculated for each grid cell and returned in Band 2.

#### The height_map function is exectued as follows:

`from PointCloudStat.DSM import height_map`

`height_map(point_cloud=[path to pointloud], out_raster=[raster save location], 
    resolution=[desired resolution (numeric)], window_size=[fill window for no data (int)], 
    epsg=[epsg code (int)], bounds=[bounding box in form ([xmin, xmax], [ymin, ymax])])`

#### The function returns a Dsm Class object containing the following attributes:
* rpc - The path of the pointcloud used to create the DSM
* res - The resolution of the raster
* path - the path of the raster file
* wind - the window used to fill no data holes (default=0)
* bounds - the ounds of the raster - can be used to match other rasters or set manually in args


### PrecisionMap module
The precision_map module has the function precision_map which creates a precision raster from a precision point cloud 
generated with the SFM_Precision module in Metashape. One can make precision rasters of x, y or z dimensions but the
main purpose is to create a z precision raster so we can determine height change maps with accurate limits of detection.

#### The precision_map function is exectued as follows:
`from PointCloudStat.precision_map import precision_map`

precision_map(prec_point_cloud=pcp1_path, out_raster=pcp1_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=[bounding box in form ([xmin, xmax], [ymin, ymax])])


Have a map...
![CWC example](../Example_Images/dod_example.png)  

### DEMofDiff module

blah... blah...

### Plotting module

This hasn't been made yet but need to make a module that can create simple plots with all the 
necessaries. Also need to create something to export histograms for Precision Analysis.

####OLD
**Create_Prec_Raster.py** is an example of creating a precision map (raster) from the precision point cloud. NB. this  
cannot be combined into the MetaShape script because the required modules cannot be imported into the Metashape  
environment. Other point2grid approaches could be used for this, and it is essential for users to specify the  
parameters used (e.g. spatial resolution etc.) suitable for their application.

