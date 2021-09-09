[![DOI](https://zenodo.org/badge/222968925.svg)](https://zenodo.org/badge/latestdoi/222968925)

***This Directory contains two packages (sfm_precision and sfm_gridz). A more detailed readme is provided 
in the subfolders. The code for our in-review paper "Using aerial photogrammetry to detect significant canopy height change 
resulting from beaver foraging" is given in GRAHAM_ET_AL_2021_PROCESSING/Analysis folders. ***

**Scope of Project/Packages**  
This project supports the calculation of precision maps to quantify uncertainty in structure-from-motion photogrammetric 
reconstructions, and the propagation of these uncertainties to robustly inform change detection analyses 
(after James et al., 2017). The method is a robust, raster based approach which allows for the propogation of both SfM 
precision and rasterisation uncertainty (aka. roughness)


**[sfm_precision](sfm_precision)**  
Package to be used with Agisoft Metashape (> 1.6). Methods used align with James, et al. (2017)

**[sfm_gridz](sfm_gridz)**  
Create Digital Surface Models (DSM), SFM Precision Raster, Height Change Maps (with consideration of Precision and 
Roughness to determine limit of detection(LOD))

**[GRAHAM_ET_AL_2021_PROCESSING](GRAHAM_ET_AL_2021_PROCESSING)**
The processing workflow for point cloud data for our in-review paper "Using aerial photogrammetry to detect significant canopy height change 
resulting from beaver foraging". Mainly uses the sfm_griz module to covert point clouds to rasters e.g.
DSMs, CHMs. ALso includes plotting of maps for the publication. generates the dataframes required for  
[GRAHAM_ET_AL_2021_Analysis](GRAHAM_ET_AL_2021_Analysis)

**[GRAHAM_ET_AL_2021_Analysis](GRAHAM_ET_AL_2021_Analysis)**
The Data Analysis for our in-review paper "Using aerial photogrammetry to detect significant canopy height change 
resulting from beaver foraging". The workflow consists of an R project and contains the workflow we used to analyse the 
DEM of difference maps produced using The [GRAHAM_ET_AL_2021_PROCESSING](GRAHAM_ET_AL_2021_PROCESSING).


**References**
James, M., Robson, S., and Smith M (2017) ‘3-D Uncertainty-Based Topographic Change Detection with  
Structure-from-Motion Photogrammetry: Precision Maps for Ground Control and Directly Georeferenced Surveys’.  
Earth Surface Processes and Landforms 42(12):1769–88. https://doi.org/10.1002/esp.4125).
