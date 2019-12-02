import Metashape
import random
import math
import csv
import os
from datetime import datetime
import shutil
import numpy as np
import laspy

startTime = datetime.now()
print("Script start time: " + str(startTime))

NaN = float('NaN')

# For use with Photoscan Pro v.1.4, with projects saved as .psz archives.
#
# Python script associated with James et al (2017) -
# 3-D uncertainty-based topographic change detection with structure-from-motion photogrammetry:
# precision maps for ground control and directly georeferenced surveys, Earth Surf. Proc. Landforms
#
# This script uses a Monte Carlo approach to enable precision estimates to be made for
# the coordinates of sparse points and camera parameters. Output files from the script can
# be processed using sfm_georef (http://tinyurl.com/sfmgeoref) and also provide variance-
# covariance information. Designed for use on projects containing a single chunk, with all photos
# taken with the same camera.
#
# Precision estimates are made by carrying out repeated bundle adjustments ('optimisations' in Photoscan)
# with different pseudo-random offsets applied to the image observations and the control measurements for each.
# The offsets are taken from normal distributions with standard deviations representative of the appropriate
# measurement precision within the survey, as given by the following Metashape settings:
#	Image coordinates:
# 		'Tie point accuracy' - defines the image measurement precision for tie points (in pixels)
#		'Marker accuracy' (or 'Projection accuracy' in older versions) - defines the image measurement precision for markers (in pixels)
# 	Measurement accuracy (i.e. survey precision of control measurements)
#		'Camera accuracy' - defines precision of known camera positions (can be set individually for each photo)
#		'Marker accuracy' -	defines precision of ground control points positions (can be set individually for each marker)
#
# Estimated point precisions will not be correct unless the values of these settings have been appropriately
# set within Metashape (e.g. 'tie point accuracy' should be set to the actual precision of the measurements
# as given by the RMS reprojection error in pixels - see James et al. 2017; doi: 10.1016/j.geomorph.2016.11.021).
# Note that use of camera angles or scalebars as control measurements have not been implemented in the script. The
# script has only been used with Local or Projected coordinate systems (i.e. not with a GCS system).
#
# Author: Mike James, Lancaster University, U.K.
# Contact: m.james at lancaster.ac.uk
# Updates: Check http://tinyurl.com/sfmgeoref
#
# Tested and used in PhotoScan Pro v.1.4, with projects saved as .psz archives.
# 15/03/18 Added scalebars into the analysis
# 29/01/18 Removed fit_shutter for compatibility with v.1.4
# 28/01/18 Added export of initial sparse point cloud ('sparse_pts_reference.ply') for use as a reference in sfm_georef.
# 28/05/17 Fixed bug in calculation of observation distances, which only affected global relative precision estimates (ratios) made in sfm_georef.
# 25/02/17 Updated the camera parameter optimisation options to exploit the greater flexibility now offered.
# 25/02/17 Added a required test for non-None marker locations (Metashape now sets them to none if unselected).
# 25/02/17 Multiple name changes to accommodate Metashape updates of chunk accuracy attributes (e.g. tie_point_accuracy).
# 25/02/17 Multiple changes to export function parameters to accommodate Metashape updates.

########################################################################################
######################################   SETUP    ######################################
########################################################################################
# Update the parameters below to tailor the script to your project.

# Directory where output will be stored and active control file is saved.
# Note use of '/' in the path (not '\'); end the path with '/'
# The files will be generated in a sub-folder named "Monte_Carlo_output"
# Change the path to the one you want, but there's no need to change act_ctrl_file.
dir_path = os.path.abspath('C:/HG_Projects/CWC_Drone_work/Prec_test_outs_v2')

filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_02_15_Danes_Mill/17_02_15_DanesCroft_Vprc.psx")

outfile = os.path.join(dir_path, "MonteCarlo_Export")

# Define how many times bundle adjustment (Metashape 'optimisation') will be carried out.
# 4000 used in original work, as a reasonable starting point.
num_randomisations = 1

# These are now set to what Andy and I use - perhaps just set it up to retrieve from project?
optimise_f = True
optimise_cx = True
optimise_cy = True
optimise_b1 = True
optimise_b2 = True
optimise_k1 = True
optimise_k2 = True
optimise_k3 = False
optimise_k4 = False
optimise_p1 = True
optimise_p2 = True
optimise_p3 = False
optimise_p4 = False

###################################   END OF SETUP   ###################################
########################################################################################

def main():
    # Create scratch file
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    scratch = os.path.join(dir_path, "scratch_folder")
    if os.path.exists(scratch):
        shutil.rmtree(scratch)
    os.mkdir(scratch)

    if not os.path.exists(outfile):
        os.mkdir(outfile)



    # Initialisation

    doc = Metashape.app.document

    if filename is not None:
        doc.open(filename, read_only=False)

    chunk = doc.chunk
    chunk = chunk.copy()
    chunk.label = 'Monte Carlo chunk'
    point_proj = chunk.point_cloud.projections


    if chunk.dense_cloud is not None:
        chunk.dense_cloud = None

    # Need CoordinateSystem object, but PS only returns 'None' if an arbitrary coordinate system is being used
    # thus need to set manually in this case; otherwise use the Chunk coordinate system.
    if chunk.crs == None:
        crs = Metashape.CoordinateSystem('LOCAL_CS["Local CS",LOCAL_DATUM["Local Datum",0],UNIT["metre",1]]')
        chunk.crs = crs
    else:
        crs = chunk.crs

    # Find which camera orientations are enabled for use as control in the bundle adjustment
    act_cam_orient_flags = []
    for cam in chunk.cameras:
        act_cam_orient_flags.append(cam.reference.enabled)
    num_act_cam_orients = sum(act_cam_orient_flags)

    # Reset the random seed, so that all equivalent runs of this script are started identically
    random.seed(1)

    # Carry out an initial bundle adjustment to ensure that everything subsequent has a consistent reference starting point.
    chunk.optimizeCameras(fit_f=optimise_f, fit_cx=optimise_cx, fit_cy=optimise_cy, fit_b1=optimise_b1, fit_b2=optimise_b2,
                          fit_k1=optimise_k1, fit_k2=optimise_k2, fit_k3=optimise_k3, fit_k4=optimise_k4,
                          fit_p1=optimise_p1, fit_p2=optimise_p2, fit_p3=optimise_p3, fit_p4=optimise_p4)


    # Set the original_marker locations be zero error, from which we can add simulated error
    for original_marker in chunk.markers:
        if original_marker.position is not None:
            original_marker.reference.location = crs.project(chunk.transform.matrix.mulp(original_marker.position))

    # Set the original_marker and point projections to be zero error, from which we can add simulated error
    original_points = chunk.point_cloud.points
    original_point_proj = chunk.point_cloud.projections
    npoints = len(original_points)
    for camera in chunk.cameras:
        if not camera.transform:
            continue

        point_index = 0
        for original_proj in original_point_proj[camera]:
            track_id = original_proj.track_id
            while point_index < npoints and original_points[point_index].track_id < track_id:
                point_index += 1
            if point_index < npoints and original_points[point_index].track_id == track_id:
                if not original_points[point_index].valid:
                    continue
                original_proj.coord = camera.project(original_points[point_index].coord)

        # Set the original marker points be zero error, from which we can add simulated error
        # Note, need to set from chunk because original_marker.position will be continuously updated
        for markerIDx, original_marker in enumerate(chunk.markers):
            if (not original_marker.projections[camera]) or (not chunk.markers[markerIDx].position):
                continue
            original_marker.projections[camera].coord = camera.project(chunk.markers[markerIDx].position)

    # Derive x and y components for image measurement precisions
    tie_proj_x_stdev = chunk.tiepoint_accuracy / math.sqrt(2)
    tie_proj_y_stdev = chunk.tiepoint_accuracy / math.sqrt(2)
    marker_proj_x_stdev = chunk.marker_projection_accuracy / math.sqrt(2)
    marker_proj_y_stdev = chunk.marker_projection_accuracy / math.sqrt(2)

    file_idx = 1

    # get point cloud dimensions and initiate running stats calculator
    dimen = (len([p for p in chunk.point_cloud.points if p.valid]), 3)
    rs = RunningStats(dimen)


    print("starting Monte Carlo optimisation loop")
    print("Pre Loop Time: " + str(datetime.now() - startTime))
    ########################################################################################
    # Main set of nested loops which control the repeated bundle adjustment
    for line_ID in range(0, num_randomisations):
        # Reset the camera coordinates if they are used for georeferencing
        if num_act_cam_orients > 0:
            for camIDx, cam in enumerate(chunk.cameras):
                if not cam.reference.accuracy:
                    cam.reference.location = (chunk.cameras[camIDx].reference.location +
                                              Metashape.Vector([random.gauss(0, chunk.camera_location_accuracy[0]),
                                                                random.gauss(0, chunk.camera_location_accuracy[1]),
                                                                random.gauss(0, chunk.camera_location_accuracy[2])]))
                else:
                    cam.reference.location = (chunk.cameras[camIDx].reference.location +
                                              Metashape.Vector([random.gauss(0, cam.reference.accuracy[0]),
                                                                random.gauss(0, cam.reference.accuracy[1]),
                                                                random.gauss(0, cam.reference.accuracy[2])]))

        # Reset the marker coordinates and add noise
        for markerIDx, marker in enumerate(chunk.markers):
            if not marker.reference.accuracy:
                marker.reference.location = (chunk.markers[markerIDx].reference.location +
                                             Metashape.Vector([random.gauss(0, chunk.marker_location_accuracy[0]),
                                                               random.gauss(0, chunk.marker_location_accuracy[1]),
                                                               random.gauss(0, chunk.marker_location_accuracy[2])]))
            else:
                marker.reference.location = (chunk.markers[markerIDx].reference.location +
                                             Metashape.Vector([random.gauss(0, marker.reference.accuracy[0]),
                                                               random.gauss(0, marker.reference.accuracy[1]),
                                                               random.gauss(0, marker.reference.accuracy[2])]))

        # Reset the scalebar lengths and add noise
        for scalebarIDx, scalebar in enumerate(chunk.scalebars):
            if scalebar.reference.distance:
                if not scalebar.reference.accuracy:
                    scalebar.reference.distance = (chunk.scalebars[scalebarIDx].reference.distance +
                                                   random.gauss(0, chunk.scalebar_accuracy))
                else:
                    scalebar.reference.distance = (chunk.scalebars[scalebarIDx].reference.distance +
                                                   random.gauss(0, scalebar.reference.accuracy))

        # Reset the observations (projections) and add Gaussian noise
        for photoIDx, camera in enumerate(chunk.cameras):
            original_camera = chunk.cameras[photoIDx]
            if not camera.transform:
                continue

            # Tie points (matches)
            matches = point_proj[camera]
            original_matches = original_point_proj[original_camera]
            for matchIDx in range(0, len(matches)):
                matches[matchIDx].coord = (original_matches[matchIDx].coord +
                                           Metashape.Vector(
                                               [random.gauss(0, tie_proj_x_stdev), random.gauss(0, tie_proj_y_stdev)]))

            # Markers
            for markerIDx, marker in enumerate(chunk.markers):
                if not marker.projections[camera]:
                    continue
                marker.projections[camera].coord = (chunk.markers[markerIDx].projections[original_camera].coord +
                                                    Metashape.Vector([random.gauss(0, marker_proj_x_stdev),
                                                                      random.gauss(0, marker_proj_y_stdev)]))

        # Bundle adjustment
        chunk.optimizeCameras(fit_f=optimise_f, fit_cx=optimise_cx, fit_cy=optimise_cy, fit_b1=optimise_b1,
                              fit_b2=optimise_b2, fit_k1=optimise_k1, fit_k2=optimise_k2, fit_k3=optimise_k3,
                              fit_k4=optimise_k4, fit_p1=optimise_p1, fit_p2=optimise_p2, fit_p3=optimise_p3,
                              fit_p4=optimise_p4)

        mc_file = os.path.join(scratch, 'monte_carlo_TP{0}.las'.format(file_idx))
        # Export the sparse point cloud
        chunk.exportPoints(mc_file, normals=False, colors=False, format=Metashape.PointsFormatLAS,
                           projection=crs)

        # call the continous stats calculator...
        print("pushing point cloud array to stats calculator")

        lf_r = laspy.file.File(mc_file, mode="r")

        las_arr = np.vstack([lf_r.X, lf_r.Y, lf_r.Z]).transpose()

        # push array to function
        rs.push(las_arr, dimen)

        # Increment the file counter
        file_idx += 1

        print("MC iteration {0}/{1} completed...".format(file_idx, num_randomisations))

    retrieve_stats_cloud(rs)

def retrieve_stats_cloud(rs):
    print("Monte Carlo iterations complete\n"
          "retrieve stats and convert to las...")

    print("continuous approach")
    mean_arr = rs.mean()

    mean_stdev = rs.standard_deviation()




class RunningStats:

    def __init__(self, dims):
        self.n = 0
        self.old_m = np.zeros(dims)
        self.new_m = np.zeros(dims)
        self.old_s = np.zeros(dims)
        self.new_s = np.zeros(dims)

    def clear(self, dims):
        self.n = np.zeros(dims)

    def push(self, x, dims):
        self.n += 1

        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = np.zeros(dims)
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else 0.0

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else 0.0

    def standard_deviation(self):
        return np.sqrt(self.variance())

    print("Total Time: " + str(datetime.now() - startTime))
    # Metashape.app.document.remove([chunk])

if __name__ == '__main__':
    main()