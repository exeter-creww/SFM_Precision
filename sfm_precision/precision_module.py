import Metashape  # V1.5.0
import random  #
import math  #
import csv  #
import os  #
from datetime import datetime  #
import numpy as np  #
from plyfile import PlyData  #
from tqdm import tqdm  #
import warnings
import shutil  #


# Define how many times bundle adjustment (MetaShape 'optimisation') will be carried out.
# 4000 recommended by James et al. as a reasonable starting point.

# For efficiency of read and write, we have maintained the original handling of intermediate MonteCarlo files.
# An offset is calculated and applied to all points which are then  written in .ply format.
# The final result is then re-projected using the saved offsets.

###################################   END OF SETUP   ###################################
########################################################################################

def Proj_SetUp():
    print("setting up folder structure")

    docu = Metashape.app.document

    orig_path = docu.path
    file_name = os.path.basename(docu.path)[:-4]
    home = os.path.dirname(docu.path)

    direc_path = os.path.join(home, file_name + '_SFM_PREC')
    if os.path.exists(direc_path):
        pass
    else:
        os.makedirs(direc_path)

    # delete dense cloud and mesh if they exist - copy document to temp psx file.
    chunky = docu.chunk

    if chunky.dense_cloud is not None:
        chunky.remove(chunky.dense_cloud)
    if chunky.model is not None:
        chunky.remove(chunky.model)
    if chunky.elevation is not None:
        chunky.remove(chunky.elevation)
    if chunky.depth_maps is not None:
        chunky.remove(chunky.depth_maps)
    if chunky.orthomosaic is not None:
        chunky.remove(chunky.orthomosaic)
    if chunky.tiled_model is not None:
        chunky.remove(chunky.tiled_model)

    docu.read_only = True

    return docu, direc_path, file_name, orig_path


def main(num_iterations, params_list, retrieve_shape_only_Prec, export_log):
    startTime = datetime.now()

    doc, dir_path, file_name, original_path = Proj_SetUp()

    if isinstance(params_list, list) is True:
        print("optimization params provided - using user defined parameters")
        optimise_f, optimise_cx, optimise_cy, optimise_b1, \
        optimise_b2, optimise_k1, optimise_k2, optimise_k3, \
        optimise_k4, optimise_p1, optimise_p2, optimise_p3, \
        optimise_p4 = Set_Camera_Params(params_list)
    else:
        warnings.warn("No params provided or params are not in the correct list form\n"
                      "Using default optimization params from James et al., 2017 ...")
        # these are the parameters described in James et al., 2017... use as defaults when no preference given.
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

    NaN = float('NaN')  # Recommend that these are not changed - enforces the calculation of offsets automatically
    pts_offset = Metashape.Vector([NaN, NaN, NaN])

    chunk = doc.chunk
    chunk.label = 'Monte Carlo chunk'

    # Functions to set the tie point accuracy to the mean of the tie point marker RMSE values.
    point_cloud = chunk.point_cloud
    points = point_cloud.points
    projections = chunk.point_cloud.projections
    total_error = calc_reprojection_error(chunk, points, projections)  # calculate reprojection error

    reproj_error = sum(total_error) / len(total_error)  # get average RMSE for all cameras

    print("mean reprojection error for point cloud:")
    print(round(reproj_error, 3))

    tiepoint_acc = (round(reproj_error, 2))
    chunk.tiepoint_accuracy = tiepoint_acc
    # chunk.marker_projection_accuracy = tiepoint_acc # leave the project setting for now.

    point_proj = chunk.point_cloud.projections

    # check for a crs. By default Metashape returns CoordinateSystem 'Local Coordinates (m)' unless changed by the user.
    if chunk.crs is None:
        raise CrsError('ERROR: No coordinate reference system set. Please set a (preferably metre-based) '
                       'coordinate reference system before running the SFM_Precision module.')
    else:
        crs = chunk.crs

    # Find which camera orientations are enabled for use as control in the bundle adjustment
    act_cam_orient_flags = []
    for cam in chunk.cameras:
        act_cam_orient_flags.append(cam.reference.enabled)
    num_act_cam_orients = sum(act_cam_orient_flags)

    # Reset the random seed, so that all equivalent runs of this script are started identically
    random.seed(1)

    # Carry out an initial bundle adjustment as a starting point to provide a consistent.
    chunk.optimizeCameras(fit_f=optimise_f, fit_cx=optimise_cx, fit_cy=optimise_cy,
                          fit_b1=optimise_b1, fit_b2=optimise_b2,
                          fit_k1=optimise_k1, fit_k2=optimise_k2, fit_k3=optimise_k3, fit_k4=optimise_k4,
                          fit_p1=optimise_p1, fit_p2=optimise_p2, fit_p3=optimise_p3, fit_p4=optimise_p4)

    sparse_ref = os.path.join(dir_path, 'start_pts_temp.ply')

    chunk.exportPoints(sparse_ref, source_data='PointCloudData', save_normals=False, save_colors=False,
                       format=Metashape.PointsFormatPLY, crs=crs, shift=pts_offset)

    # Read in reference cloud to get dimensions
    spcdata = PlyData.read(sparse_ref)
    spc_arr = np.vstack([spcdata.elements[0].data['x'],
                         spcdata.elements[0].data['y'],
                         spcdata.elements[0].data['z']]).transpose()

    dimen = np.shape(spc_arr)
    del spcdata, spc_arr
    if os.path.exists(sparse_ref):
        os.remove(sparse_ref)

    # If required, calculate the mean point coordinate to use as an offset
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

    # Export a text file of observation distances and ground dimensions of pixels from which
    # relative precisions can be calculated. File will have one row for each observation, and three columns:
    # cameraID      ground pixel dimension (m)   observation distance (m)
    points = chunk.point_cloud.points
    npoints = len(points)
    camera_index = 0

    if retrieve_shape_only_Prec is True:
        retrieve_shape_precision(chunk, camera_index, npoints, points, dir_path, file_name)
    else:
        print("Shape Precision values not requested... Skipping export")

    # Make a copy of the chunk to use as a zero-error reference chunk
    original_chunk = chunk.copy()
    original_chunk.label = 'MC copy'

    # Set the original_marker locations be zero error, from which we can add simulated error
    print("iterating markers - setting zero error")
    for original_marker in tqdm(original_chunk.markers):
        if original_marker.position is not None:
            original_marker.reference.location = crs.project(
                original_chunk.transform.matrix.mulp(original_marker.position))

    # Set the original_marker and point projections to be zero error, from which we can add simulated error
    original_points = original_chunk.point_cloud.points
    original_point_proj = original_chunk.point_cloud.projections
    npoints = len(original_points)
    print("iterating cameras - setting zero error")
    for camera in tqdm(original_chunk.cameras):
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
        for markerIDx, original_marker in enumerate(original_chunk.markers):
            if (not original_marker.projections[camera]) or (not chunk.markers[markerIDx].position):
                continue
            original_marker.projections[camera].coord = camera.project(chunk.markers[markerIDx].position)

    # Derive x and y components for image measurement precisions
    tie_proj_x_stdev = chunk.tiepoint_accuracy / math.sqrt(2)
    tie_proj_y_stdev = chunk.tiepoint_accuracy / math.sqrt(2)
    marker_proj_x_stdev = chunk.marker_projection_accuracy / math.sqrt(2)
    marker_proj_y_stdev = chunk.marker_projection_accuracy / math.sqrt(2)

    # return to the Monte Carlo chunk
    Metashape.app.document.chunk = chunk

    # Run the monteCarlo Stuff
    ppc_path, num_fail, p_val_list = MonteCarloJam(num_act_cam_orients, chunk, original_chunk, point_proj,
                                                   original_point_proj,  tie_proj_x_stdev, tie_proj_y_stdev,
                                                   marker_proj_x_stdev, marker_proj_y_stdev, file_name,
                                                   crs, pts_offset, dir_path, dimen, num_iterations,
                                                   optimise_f, optimise_cx,  optimise_cy, optimise_b1,
                                                   optimise_b2, optimise_k1, optimise_k2,  optimise_k3,
                                                   optimise_k4, optimise_p1, optimise_p2, optimise_p3, optimise_p4)

    TotTime = datetime.now() - startTime

    t_path = doc.path
    t_folder = doc.path[:-4] + ".files"

    # reopen original document
    doc.open(original_path, read_only=False)

    if export_log is True:
        logfile_export(dir_path, file_name, crs, ppc_path, num_iterations, num_fail, retrieve_shape_only_Prec,
                       optimise_f, optimise_cx, optimise_cy, optimise_b1, optimise_b2, optimise_k1, optimise_k2,
                       optimise_k3, optimise_k4, optimise_p1, optimise_p2, optimise_p3, optimise_p4, TotTime,
                       p_val_list)

    print("SFM Precision Complete.\n Run time: " + str(TotTime))


#########################################################################################
######### Main set of nested loops which control the repeated bundle adjustment #########
#########################################################################################
def MonteCarloJam(num_act_cam_orients, chunk, original_chunk, point_proj,
                  original_point_proj, tie_proj_x_stdev, tie_proj_y_stdev,
                  marker_proj_x_stdev, marker_proj_y_stdev, file_name,
                  crs, pts_offset, dir_path, dimen, num_iterations,
                  optimise_f, optimise_cx, optimise_cy, optimise_b1,
                  optimise_b2, optimise_k1, optimise_k2, optimise_k3,
                  optimise_k4, optimise_p1, optimise_p2, optimise_p3,
                  optimise_p4):
    file_idx = 0
    n_size_err = 0
    prec_val = 100000000

    for line_ID in tqdm(range(0, num_iterations)):
        file_idx += 1
        # Reset the camera coordinates if they are used for georeferencing
        if num_act_cam_orients > 0:
            for camIDx, cam in enumerate(chunk.cameras):
                if not cam.reference.accuracy:
                    cam.reference.location = (original_chunk.cameras[camIDx].reference.location +
                                              Metashape.Vector([random.gauss(0, chunk.camera_location_accuracy[0]),
                                                                random.gauss(0, chunk.camera_location_accuracy[1]),
                                                                random.gauss(0, chunk.camera_location_accuracy[2])]))
                else:
                    cam.reference.location = (original_chunk.cameras[camIDx].reference.location +
                                              Metashape.Vector([random.gauss(0, cam.reference.accuracy[0]),
                                                                random.gauss(0, cam.reference.accuracy[1]),
                                                                random.gauss(0, cam.reference.accuracy[2])]))

        # Reset the marker coordinates and add noise
        for markerIDx, marker in enumerate(chunk.markers):
            if not marker.reference.accuracy:
                marker.reference.location = (original_chunk.markers[markerIDx].reference.location +
                                             Metashape.Vector([random.gauss(0, chunk.marker_location_accuracy[0]),
                                                               random.gauss(0, chunk.marker_location_accuracy[1]),
                                                               random.gauss(0, chunk.marker_location_accuracy[2])]))
            else:
                marker.reference.location = (original_chunk.markers[markerIDx].reference.location +
                                             Metashape.Vector([random.gauss(0, marker.reference.accuracy[0]),
                                                               random.gauss(0, marker.reference.accuracy[1]),
                                                               random.gauss(0, marker.reference.accuracy[2])]))

        # Reset the scalebar lengths and add Gaussian noise
        for scalebarIDx, scalebar in enumerate(chunk.scalebars):
            if scalebar.reference.distance:
                if not scalebar.reference.accuracy:
                    scalebar.reference.distance = (original_chunk.scalebars[scalebarIDx].reference.distance +
                                                   random.gauss(0, chunk.scalebar_accuracy))
                else:
                    scalebar.reference.distance = (original_chunk.scalebars[scalebarIDx].reference.distance +
                                                   random.gauss(0, scalebar.reference.accuracy))

        # Reset the observations (projections) and add Gaussian noise
        for photoIDx, camera in enumerate(chunk.cameras):
            original_camera = original_chunk.cameras[photoIDx]
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
                marker.projections[camera].coord = (
                            original_chunk.markers[markerIDx].projections[original_camera].coord +
                            Metashape.Vector([random.gauss(0, marker_proj_x_stdev),
                                              random.gauss(0, marker_proj_y_stdev)]))

        # Bundle adjustment
        chunk.optimizeCameras(fit_f=optimise_f, fit_cx=optimise_cx, fit_cy=optimise_cy, fit_b1=optimise_b1,
                              fit_b2=optimise_b2, fit_k1=optimise_k1, fit_k2=optimise_k2, fit_k3=optimise_k3,
                              fit_k4=optimise_k4, fit_p1=optimise_p1, fit_p2=optimise_p2, fit_p3=optimise_p3,
                              fit_p4=optimise_p4)

        out_file = os.path.join(dir_path, 'Temp_PointCloud.ply')
        if os.path.exists(out_file):
            os.remove(out_file)
        # Export the sparse point cloud
        chunk.exportPoints(out_file, source_data='PointCloudData', save_normals=False, save_colors=False,
                           format=Metashape.PointsFormatPLY, crs=crs, shift=pts_offset)

        # Increment the file counter

        plydata = PlyData.read(out_file)
        ply_arr = np.vstack([plydata.elements[0].data['x'],
                             plydata.elements[0].data['y'],
                             plydata.elements[0].data['z']]).transpose()

        check_dim = np.shape(ply_arr)

        if check_dim != dimen:
            print("Inconsistently sized array produced - skipping this iteration...")
            n_size_err += 1
            del plydata, ply_arr
            continue

        int_arr = np.asarray(ply_arr * prec_val, dtype=np.float64)

        if file_idx == 1:
            dimen = np.shape(ply_arr)
            start_arr = np.zeros(dimen)

            Agg = (0, ply_arr * prec_val, ply_arr * prec_val)

        Agg = update(Agg, int_arr)

        del plydata, ply_arr

    mean, variance, sampleVariance = finalize(Agg)

    stdev_arr = np.sqrt(abs(variance)) / prec_val
    mean_arr = mean / prec_val
    # sv_std = np.sqrt(sampleVariance)

    out_cloud_path = os.path.join(dir_path, file_name + '_Prec_Cloud.txt')

    combined = np.concatenate((mean_arr, stdev_arr), axis=1)
    nested_lst_of_tuples = [tuple(l) for l in combined]
    comb_arr = np.array(nested_lst_of_tuples,
                        dtype=[('x', 'f8'), ('y', 'f8'),
                               ('z', 'f8'), ('xerr', 'f8'),
                               ('yerr', 'f8'), ('zerr', 'f8')])

    comb_arr['x'] = comb_arr['x'] + pts_offset[0]
    comb_arr['y'] = comb_arr['y'] + pts_offset[1]
    comb_arr['z'] = comb_arr['z'] + pts_offset[2]

    np.savetxt(out_cloud_path, comb_arr, delimiter=" ",
               header="x y z xerr yerr zerr", comments='')

    if os.path.exists(os.path.join(dir_path, 'Temp_PointCloud.ply')):
        os.remove(os.path.join(dir_path, 'Temp_PointCloud.ply'))

    if n_size_err > 0:
        print("############   WARNING   ############")
        print("{0} out of {1} iterations skipped...".format(n_size_err, num_iterations))
        print("Results based on {0} iterations.".format(num_iterations - n_size_err))

    xmean = np.mean(comb_arr['xerr'])
    xmax = np.max(comb_arr['xerr'])
    xmin = np.min(comb_arr['xerr'])
    ymean = np.mean(comb_arr['yerr'])
    ymax = np.max(comb_arr['yerr'])
    ymin = np.min(comb_arr['yerr'])
    zmean = np.mean(comb_arr['zerr'])
    zmax = np.max(comb_arr['zerr'])
    zmin = np.min(comb_arr['zerr'])

    p_s_vals = [xmean, xmax, xmin, ymean, ymax, ymin, zmean, zmax, zmin]

    return out_cloud_path, n_size_err, p_s_vals


def update(existingAggregate, newValue):
    (count, mean, M2) = existingAggregate

    count += 1
    delta = newValue - mean
    mean += np.divide(delta, count)
    delta2 = newValue - mean
    M2 += delta * delta2

    return count, mean, M2


# Retrieve the mean, variance and sample variance from an aggregate
def finalize(existingAggregate):
    (count, mean, M2) = existingAggregate
    (mean, variance, sampleVariance) = (mean, M2 / count, M2 / (count - 1))
    if count < 2:
        return float('nan')
    else:
        return mean, variance, sampleVariance


def calc_reprojection_error(chunk, points, projections):
    npoints = len(points)

    photo_avg = []
    print(" iterating cameras to determine Reprojection Error...")
    for camera in tqdm(chunk.cameras):
        if not camera.transform:
            continue
        point_index = 0
        photo_num = 0
        photo_err = 0
        for proj in projections[camera]:
            track_id = proj.track_id
            while point_index < npoints and points[point_index].track_id < track_id:
                point_index += 1
            if point_index < npoints and points[point_index].track_id == track_id:
                if not points[point_index].valid:
                    continue

                dist = camera.error(points[point_index].coord,
                                    proj.coord).norm() ** 2  # get the square error for each point in camera

                photo_num += 1  # counts number of points per camera
                photo_err += dist  # creates list of square point errors

        photo_avg.append(math.sqrt(photo_err / photo_num))  # get root mean square error for each camera

    return photo_avg  # returns list of rmse values for each camera


def retrieve_shape_precision(chunk, camera_index, npoints, points, dir_path, file_name):
    with open(os.path.join(dir_path, file_name + '_observation_distances.txt'), "w") as f:
        fwriter = csv.writer(f, dialect='excel-tab', lineterminator='\n')
        for camera in chunk.cameras:
            camera_index += 1
            if not camera.transform:
                continue

            fx = camera.sensor.calibration.f

            point_index = 0
            for proj in chunk.point_cloud.projections[camera]:
                track_id = proj.track_id
                while point_index < npoints and points[point_index].track_id < track_id:
                    point_index += 1
                if point_index < npoints and points[point_index].track_id == track_id:
                    if not points[point_index].valid:
                        continue
                    dist = (chunk.transform.matrix.mulp(camera.center) - chunk.transform.matrix.mulp(Metashape.Vector(
                        [points[point_index].coord[0], points[point_index].coord[1],
                         points[point_index].coord[2]]))).norm()
                    fwriter.writerow([camera_index, '{0:.4f}'.format(dist / fx), '{0:.2f}'.format(dist)])

        f.close()


def Set_Camera_Params(p_list):
    if 'fit_f' in p_list:
        optimise_f = True
    else:
        optimise_f = False

    if 'fit_cx' in p_list:
        optimise_cx = True
    else:
        optimise_cx = False
    if 'fit_cy' in p_list:
        optimise_cy = True
    else:
        optimise_cy = False
    if 'fit_b1' in p_list:
        optimise_b1 = True
    else:
        optimise_b1 = False
    if 'fit_b2' in p_list:
        optimise_b2 = True
    else:
        optimise_b2 = False
    if 'fit_k1' in p_list:
        optimise_k1 = True
    else:
        optimise_k1 = False
    if 'fit_k2' in p_list:
        optimise_k2 = True
    else:
        optimise_k2 = False
    if 'fit_k3' in p_list:
        optimise_k3 = True
    else:
        optimise_k3 = False
    if 'fit_k4' in p_list:
        optimise_k4 = True
    else:
        optimise_k4 = False
    if 'fit_p1' in p_list:
        optimise_p1 = True
    else:
        optimise_p1 = False
    if 'fit_p2' in p_list:
        optimise_p2 = True
    else:
        optimise_p2 = False
    if 'fit_p3' in p_list:
        optimise_p3 = True
    else:
        optimise_p3 = False
    if 'fit_p4' in p_list:
        optimise_p4 = True
    else:
        optimise_p4 = False

    return optimise_f, optimise_cx, optimise_cy, optimise_b1, \
           optimise_b2, optimise_k1, optimise_k2, optimise_k3, \
           optimise_k4, optimise_p1, optimise_p2, optimise_p3, \
           optimise_p4


def logfile_export(dir_path, file_name, crs, ppc_path, num_it, num_fail, obs_path,
                   optimise_f, optimise_cx, optimise_cy, optimise_b1, optimise_b2, optimise_k1, optimise_k2,
                   optimise_k3, optimise_k4, optimise_p1, optimise_p2, optimise_p3, optimise_p4, time, p_sum_list):
    print("Exporting log file...")
    with open(os.path.join(dir_path, file_name + '_log_file.txt'), "w") as f:
        f.write("------------------------------------------------------------\n")
        f.write("------------- METASHAPE SFM PRECISION LOG FILE -------------\n")
        f.write("------------------------------------------------------------\n\n")
        f.write("Number of MonteCarlo iterations Attempted:    {0}\n".format(num_it))
        f.write("Number of MonteCarlo iterations Skipped:      {0}\n".format(num_fail))
        f.write("Number of MonteCarlo iterations Completed:    {0}\n\n".format(num_it - num_fail))
        f.write("------------------------------------------------------------\n\n")
        f.write("Project CRS:\n")
        f.write(str([crs]) + "\n\n")
        f.write("------------------------------------------------------------\n\n")
        f.write("Point Precision Summary Stats:\n")
        f.write("mean x: {0}\n".format(p_sum_list[0]))
        f.write("max x:  {0}\n".format(p_sum_list[1]))
        f.write("min x:  {0}\n".format(p_sum_list[2]))
        f.write("mean y: {0}\n".format(p_sum_list[3]))
        f.write("max y:  {0}\n".format(p_sum_list[4]))
        f.write("min y:  {0}\n".format(p_sum_list[5]))
        f.write("mean z: {0}\n".format(p_sum_list[6]))
        f.write("max z:  {0}\n".format(p_sum_list[7]))
        f.write("min z:  {0}\n\n".format(p_sum_list[8]))
        f.write("------------------------------------------------------------\n\n")
        f.write("Optimised Lens Parameters:\n")
        f.write('fit_f  = {}\n'.format(optimise_f))
        f.write('fit_cx = {}\n'.format(optimise_cx))
        f.write('fit_cy = {}\n'.format(optimise_cy))
        f.write('fit_b1 = {}\n'.format(optimise_b1))
        f.write('fit_b2 = {}\n'.format(optimise_b2))
        f.write('fit_k1 = {}\n'.format(optimise_k1))
        f.write('fit_k2 = {}\n'.format(optimise_k2))
        f.write('fit_k3 = {}\n'.format(optimise_k3))
        f.write('fit_k4 = {}\n'.format(optimise_k4))
        f.write('fit_p1 = {}\n'.format(optimise_p1))
        f.write('fit_p2 = {}\n'.format(optimise_p2))
        f.write('fit_p3 = {}\n'.format(optimise_p3))
        f.write('fit_p4 = {}\n\n'.format(optimise_p4))
        f.write("------------------------------------------------------------\n\n")
        f.write("The following files were produced:\n\n")
        f.write("{0}\n\n".format(ppc_path))
        if obs_path is True:
            f.write("{0}\n\n".format(os.path.join(dir_path, file_name + '_observation_distances.txt')))
        f.write("------------------------------------------------------------\n\n")
        f.write("SFM Precision Run Time: {0}\n".format(time))
        f.write("Analysis completed at: {0}".format(datetime.now()))



    f.close()


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class CrsError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
