# SFM_Precision
A python workflow to create precision maps with Agisoft MetaShape.

(Developed after: James, M., Robson, S., and Smith M (2017) ‘3-D Uncertainty-Based Topographic Change Detection with Structure-from-Motion Photogrammetry: Precision Maps for Ground Control and Directly Georeferenced Surveys’. Earth Surface Processes and Landforms 42(12):1769–88. https://doi.org/10.1002/esp.4125).

Before running SFM_precision_analysis.py, run the falling (in cmd.exe) to install dependencies in the Metashape environment:

"C:\Program Files\Agisoft\Metashape Pro\python\python.exe" -m pip install numpy tqdm plyfile


**SFM_precision_analysis.py** is the new version of the original SfM precision code published by James et al. 2017, which produces a sparse point cloud of mean location and x, y and z precision estimate for each tie point, based on Monte Carlo analysis in Metashape.

**original_precision_estimates.py** is the original python script published by James et al. (with some minor changes for running from cmd and testing). Produces a folder with all montecarlo outputs and additional output info (some of which is not relevant here...).

**Create_Prec_Raster.py** is an example of creating a precision map (raster) from the precision point cloud. NB. this cannot be combined into the MetaShape script because the required modules cannot be imported into the metashape environment. Other point2grid approaches could be used for this, and it is essential for users to specify the parameters used (e.g. spatial resolution etc.) depending on their application.


