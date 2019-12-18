# SFM_Precision
A python workflow to create precision maps with Agisoft MetaShape.

(Developed after: James, M., Robson, S., and Smith M (2017) ‘3-D Uncertainty-Based Topographic Change Detection with Structure-from-Motion Photogrammetry: Precision Maps for Ground Control and Directly Georeferenced Surveys’. Earth Surface Processes and Landforms 42(12):1769–88. https://doi.org/10.1002/esp.4125).
# 
### Installation
Run the falling (in cmd.exe) to install dependencies in the Metashape environment:

"C:\Program Files\Agisoft\Metashape Pro\python\python.exe" -m pip install numpy tqdm plyfile

Then if you want to add this as a module in the Metashape python distribution just copy SFM_precision_analysis.py into 
this folder: "C:\Program Files\Agisoft\Metashape Pro\python\Lib\site-packages". Then the module can be used in custom 
scripts or called directly from the metashape console with:

`import SFM_precision`

`SFM_precision.Run(num_iterations=1000)`

#### The following optional args can be used:

**shape_only_Prec=False** # Default is False - if True then a file with observation distances is produced

**params_list=[]** # This is a list with desired camera optimization parameters, submitting an empty list returns all params
as False. Enter desired params in list as follows:  
['fit_f', 'fit_cx', 'fit_cy','fit_b1', 'fit_b2', 'fit_k1', 
'fit_k2', 'fit_k3', 'fit_k4','fit_p1', 'fit_p2', 'fit_p3', 'fit_p4']
If no arg is provided then default parameters are selected based on James, et al. 2017.

**SFM_precision.py** is the new version of the original SfM precision code published by James et al. 2017, which is a module that produces a sparse point cloud of mean location and x, y and z precision estimate for each tie point, based on Monte Carlo analysis in Metashape.

**SS/original_precision_estimates.py** is the original python script published by James et al. (with some minor changes for running from cmd and testing). Produces a folder with all montecarlo outputs and additional output info (some of which is not relevant here...).

**Create_Prec_Raster.py** is an example of creating a precision map (raster) from the precision point cloud. NB. this cannot be combined into the MetaShape script because the required modules cannot be imported into the metashape environment. Other point2grid approaches could be used for this, and it is essential for users to specify the parameters used (e.g. spatial resolution etc.) depending on their application.

**Launch_script.py** is an example launch script for the SFM_precision module

