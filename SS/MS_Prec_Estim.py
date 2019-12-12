import Metashape
import random
import math
import os
from datetime import datetime
import shutil
import numpy as np
from tqdm import tqdm
from plyfile import PlyData, PlyElement
import sys

startTime = datetime.now()
print("Script start time: " + str(startTime))

# def it_list():
#     i_list = [1000, 2500, 6000, 10000]
#
#     for i in i_list:
#         print("running script for {0} iterations".format(i))
#
#         setup(i)

def setup():
    # The files will be generated in a sub-folder named "Monte_Carlo_Export"
    # Change the path to the one you want, but there's no need to change act_ctrl_file.
    dir_path = os.path.abspath('C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1')

    # filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_02_15_Danes_Mill/17_02_15_DanesCroft_Vprc.psx")
    filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/pia_plots/P3E1_HG.psz")

    outfolder = os.path.join(dir_path, "MonteCarlo_Export_pia")

    out_cloud_path = os.path.join(outfolder, ('MonteCarloResult_New_it_{0}b.txt').format(1000))

    # Define how many times bundle adjustment (Metashape 'optimisation') will be carried out.
    # 4000 used in original work, as a reasonable starting point.
    num_randomisations = 1000
    print("Running for {0} iterations...".format(num_randomisations))
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

    main(dir_path, filename, outfolder, num_randomisations, optimise_f,
         optimise_cx, optimise_cy, optimise_b1, optimise_b2, optimise_k1,
         optimise_k2, optimise_k3, optimise_k4, optimise_p1, optimise_p2,
         optimise_p3, optimise_p4, out_cloud_path)
###################################   END OF SETUP   ###################################
########################################################################################

def main(dir_path, filename, outfolder, num_randomisations, optimise_f,
         optimise_cx, optimise_cy, optimise_b1, optimise_b2, optimise_k1,
         optimise_k2, optimise_k3, optimise_k4, optimise_p1, optimise_p2,
         optimise_p3, optimise_p4, out_cloud_path):

    # Create scratch file
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    scratch = os.path.join(dir_path, "MC_Test_outs_offset")
    if os.path.exists(scratch):
        shutil.rmtree(scratch)
    os.mkdir(scratch)

    if not os.path.exists(outfolder):
        os.mkdir(outfolder)

    # Initialisation

    doc = Metashape.app.document

    if filename is not None:
        doc.open(filename, read_only=False)

    chunk_orig = doc.chunk
    chunk = chunk_orig.copy()
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

    pts_offset = Metashape.Vector([float('NaN'), float('NaN'), float('NaN')])
    if math.isnan(pts_offset[0]):
        points = chunk.point_cloud.points
        npoints = 0
        pts_offset = Metashape.Vector([0, 0, 0])
        for point in points:
            if not point.valid:
                continue
            npoints += 1
            pts_offset[0] += point.coord[0]
            pts_offset[1] += point.coord[1]
            pts_offset[2] += point.coord[2]

        pts_offset = crs.project(chunk.transform.matrix.mulp(pts_offset / npoints))
        pts_offset[0] = round(pts_offset[0], -2)
        pts_offset[1] = round(pts_offset[1], -2)
        pts_offset[2] = round(pts_offset[2], -2)

    # Reset the random seed, so that all equivalent runs of this script are started identically
    random.seed(1)

    # Carry out an initial bundle adjustment to ensure that everything subsequent has a consistent reference starting point.
    chunk.optimizeCameras(fit_f=optimise_f, fit_cx=optimise_cx, fit_cy=optimise_cy, fit_b1=optimise_b1, fit_b2=optimise_b2,
                          fit_k1=optimise_k1, fit_k2=optimise_k2, fit_k3=optimise_k3, fit_k4=optimise_k4,
                          fit_p1=optimise_p1, fit_p2=optimise_p2, fit_p3=optimise_p3, fit_p4=optimise_p4)


    # Set the original_marker locations be zero error, from which we can add simulated error
    print("set marker locs to be zero error:")
    for original_marker in tqdm(chunk.markers):
        if original_marker.position is not None:
            original_marker.reference.location = crs.project(chunk.transform.matrix.mulp(original_marker.position))

    # Set the original_marker and point projections to be zero error, from which we can add simulated error
    print("Update: Setting the original_marker and point projections to be zero error")
    original_points = chunk.point_cloud.points
    original_point_proj = chunk.point_cloud.projections
    npoints = len(original_points)

    for camera in tqdm(chunk.cameras):

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

    file_idx = 0

    # get point cloud dimensions and set up stats calculator
    dimen = (len([p for p in chunk.point_cloud.points if p.valid]), 3)
    rs = RunningStats(dimen)
    prc_val = 100000000

    chunk.resetRegion()  # reset bounding region
    region = chunk.region
    region.size = 10 * region.size  # increase bounding region
    chunk.region = region


    print("starting Monte Carlo optimisation loop")
    print("Pre Loop Time: " + str(datetime.now() - startTime))
    ########################################################################################
    # Main set of nested loops which control the repeated bundle adjustment
    for line_ID in tqdm(range(0, num_randomisations)):

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

        mc_file = os.path.join(scratch, 'monte_carlo_TP{}.txt'.format(file_idx+1))
        # Export the sparse point cloud
        chunk.exportPoints(mc_file, normals=False, colors=False, format=Metashape.PointsFormatXYZ,
                           projection=crs, binary=False, precision=8, shift=pts_offset)

        # call the continous stats calculator...
        print("pushing point cloud array to stats calculator")

        ply_arr = readPC(mc_file, prc_val)

        # push array to function
        rs.push(ply_arr)

        # Increment the file counter
        file_idx += 1


        # print("MC iteration {0}/{1} completed...".format(file_idx, num_randomisations))


    print("Monte Carlo iterations complete\n"
          "retrieve stats and convert to ply...")

    mean_arr = rs.mean()/prc_val

    stdev_arr = rs.standard_deviation()/prc_val

    combined = np.concatenate((mean_arr, stdev_arr), axis=1)
    nested_lst_of_tuples = [tuple(l) for l in combined]
    comb_arr = np.array(nested_lst_of_tuples,
                        dtype=[('x', 'f8'), ('y', 'f8'),
                               ('z', 'f8'), ('xerr', 'f8'), ('yerr', 'f8'),
                               ('zerr', 'f8')])


    np.savetxt(out_cloud_path, comb_arr, delimiter=" ",
               header="x y z xerr yerr zerr", comments='')

    # el = PlyElement.describe(comb_arr, 'vertex')
    #
    # PlyData([el]).write(os.path.join(outfolder, 'MonteCarloResult_v13.ply'))

    print("ply file created")
    doc.remove(chunk)

    doc.save()

    print("script completed!")
    print("Total Time: " + str(datetime.now() - startTime))

def readPC(pc, prec_val,):
    pcdata = np.loadtxt(pc, dtype={'names': ('x', 'y', 'z'), 'formats': ('f8', 'f8', 'f8')})
    pc_arr = np.vstack([pcdata['x'],
                         pcdata['y'],
                         pcdata['z']]).transpose()

    int_arr = np.asarray(pc_arr * prec_val, dtype=np.float64)

    return int_arr


class RunningStats:

    def __init__(self, dims):
        self.zeroArr = np.zeros(dims)
        self.n = 0
        self.old_m = np.zeros(dims)
        self.new_m = np.zeros(dims)
        self.old_s = np.zeros(dims)
        self.new_s = np.zeros(dims)

    def clear(self):
        self.n = 0

    def push(self, x):
        self.n += 1

        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = self.zeroArr
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else self.zeroArr

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else self.zeroArr

    def standard_deviation(self):
        return np.sqrt(self.variance())



if __name__ == '__main__':
    # it_list()
    setup()

