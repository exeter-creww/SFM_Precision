import Metashape
import random
import math
import csv
import os
from datetime import datetime
import numpy as np
from plyfile import PlyData
from tqdm import tqdm


startTime = datetime.now()
print("Script start time: " + str(startTime))


# Specify file path to project. Tested with .psz, need to verify with .psx?
filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/pia_plots/P3E1.psz")
# filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_02_15_Danes_Mill/17_02_15_DanesCroft_Vprc.psx")
fold_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/HG_Retest_Pia_1000_it")
# fold_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/HG_Retest_CWC_10it")
if os.path.exists(fold_path):
    print("output folder exists")
else:
    print("creating output folder")
    os.mkdir(fold_path)
# dir_path = os.path.abspath('C:/HG_Projects/CWC_Drone_work/HG_Retest_Pia')
# act_ctrl_file = 'active_ctrl_indices.txt'

# Define how many times bundle adjustment (MetaShape 'optimisation') will be carried out.
# 4000 recommended by James et al. as a reasonable starting point.
num_iterations = 1000

retrieve_shape_only_Prec = False

# Set desired optimisation params here:

optimise_f = True
optimise_cx = True
optimise_cy = True
optimise_b1 = False
optimise_b2 = False
optimise_k1 = True
optimise_k2 = True
optimise_k3 = True
optimise_k4 = False
optimise_p1 = False
optimise_p2 = False
optimise_p3 = False
optimise_p4 = False

# For efficiency of read and write, we have maintained the original handling of intermediate MonteCarlo files.
# An offset is calculated and applied to all points whic are then  written in .ply format.
# The final result is then re projected using the saved offsets.

###################################   END OF SETUP   ###################################
########################################################################################
def KickOff():
    dir_path = os.path.join(fold_path, 'Monte_Carlo_output')
    os.makedirs(dir_path, exist_ok=True)
    NaN = float('NaN')
    pts_offset = Metashape.Vector([NaN, NaN, NaN])
    # Initialisation
    doc = Metashape.app.document
    doc.open(filename, read_only=False)

    chunk_orig = doc.chunk
    chunk = chunk_orig.copy()
    chunk.label = 'Monte Carlo chunk'

    if chunk.dense_cloud is not None:
        chunk.dense_cloud = None

    point_proj = chunk.point_cloud.projections

    # Need CoordinateSystem object, but PS only returns 'None' if an arbitrary coordinate system is being used
    # thus need to set manually in this case; otherwise use the Chunk coordinate system.

    if chunk.crs is None:
        crs = Metashape.CoordinateSystem('LOCAL_CS["Local CS",LOCAL_DATUM["Local Datum",0],UNIT["metre",1]]')
        chunk.crs = crs
    else:
        crs = chunk.crs

    # Find which markers are enabled for use as control points in the bundle adjustment
    act_marker_flags = []
    for marker in chunk.markers:
        act_marker_flags.append(marker.reference.enabled)
    num_act_markers = sum(act_marker_flags)

    # Find which camera orientations are enabled for use as control in the bundle adjustment
    act_cam_orient_flags = []
    for cam in chunk.cameras:
        act_cam_orient_flags.append(cam.reference.enabled)
    num_act_cam_orients = sum(act_cam_orient_flags)

    # Reset the random seed, so that all equivalent runs of this script are started identically
    random.seed(1)

    # Carry out an initial bundle adjustment to ensure that everything subsequent has a consistent reference starting point.
    chunk.optimizeCameras(fit_f=optimise_f, fit_cx=optimise_cx, fit_cy=optimise_cy,
                          fit_b1=optimise_b1, fit_b2=optimise_b2,
                          fit_k1=optimise_k1, fit_k2=optimise_k2, fit_k3=optimise_k3, fit_k4=optimise_k4,
                          fit_p1=optimise_p1, fit_p2=optimise_p2, fit_p3=optimise_p3, fit_p4=optimise_p4)

    sparse_ref = os.path.join(dir_path, 'start_pts_temp.ply')
    chunk.exportPoints(sparse_ref, normals=False, colors=False,
                       format=Metashape.PointsFormatPLY, projection=crs, shift=pts_offset)

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

    # Save the used offset to text file
    # with open(os.path.join(fold_path, '_coordinate_local_origin.txt'), "w") as f:
    #     fwriter = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    #     fwriter.writerow(pts_offset)
    #     f.close()

    # Export a text file of observation distances and ground dimensions of pixels from which relative precisions can be calculated
    # File will have one row for each observation, and three columns:
    # cameraID      ground pixel dimension (m)   observation distance (m)
    points = chunk.point_cloud.points
    npoints = len(points)
    camera_index = 0

    if retrieve_shape_only_Prec is True:
        retrieve_shape_precision(chunk, camera_index, npoints, points)
    else:
        print("Shape Precision values not requested... Skipping export")

    # Export a text file with the coordinate system
    # with open(os.path.join(fold_path, '_coordinate_system.txt'), "w") as f:
    #     fwriter = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    #     fwriter.writerow([crs])
    #     f.close()

    # Make a copy of the chunk to use as a zero-error reference chunk
    original_chunk = chunk.copy()

    # Set the original_marker locations be zero error, from which we can add simulated error
    print("iterating markers - setting zero error")
    for original_marker in tqdm(original_chunk.markers):
        if original_marker.position is not None:
            original_marker.reference.location = crs.project(original_chunk.transform.matrix.mulp(original_marker.position))

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
    MonteCarloJam(num_act_cam_orients, chunk, original_chunk, point_proj,
                  original_point_proj, tie_proj_x_stdev, tie_proj_y_stdev,
                  marker_proj_x_stdev, marker_proj_y_stdev, num_act_markers,
                  crs, pts_offset, dir_path, dimen)


def MonteCarloJam(num_act_cam_orients, chunk, original_chunk, point_proj,
                  original_point_proj, tie_proj_x_stdev, tie_proj_y_stdev,
                  marker_proj_x_stdev, marker_proj_y_stdev, num_act_markers,
                  crs, pts_offset, dir_path, dimen):

    print("Pre Loop Time: " + str(datetime.now() - startTime))
    file_idx = 0
    prec_val = 100000000
    ########################################################################################
    # Main set of nested loops which control the repeated bundle adjustment
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
                marker.projections[camera].coord = (original_chunk.markers[markerIDx].projections[original_camera].coord +
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
        chunk.exportPoints(out_file, normals=False, colors=False, format=Metashape.PointsFormatPLY,
                           projection=crs, shift=pts_offset)

        # Increment the file counter

        plydata = PlyData.read(out_file)
        ply_arr = np.vstack([plydata.elements[0].data['x'],
                             plydata.elements[0].data['y'],
                             plydata.elements[0].data['z']]).transpose()

        check_dim = np.shape(ply_arr)

        if check_dim != dimen:
            print("size issue!!!!!!!!!!!!!!!!!!!")
            del plydata, ply_arr
            continue

        int_arr = np.asarray(ply_arr * prec_val, dtype=np.float64)

        if file_idx == 1:
            dimen = np.shape(ply_arr)
            start_arr = np.zeros(dimen)

            Agg = (0, start_arr, ply_arr * prec_val, ply_arr * prec_val)


        Agg = update(Agg, int_arr)

        del plydata, ply_arr

    mean, variance, sampleVariance = finalize(Agg)

    stdev_arr = np.sqrt(variance) / prec_val
    mean_arr = mean / prec_val
    # sv_std = np.sqrt(sampleVariance)
    print(np.mean(stdev_arr))

    out_cloud_path = os.path.join(dir_path, 'Final_PointCloud.txt')

    combined = np.concatenate((mean_arr, stdev_arr), axis=1)
    nested_lst_of_tuples = [tuple(l) for l in combined]
    comb_arr = np.array(nested_lst_of_tuples,
                        dtype=[('x', 'f8'), ('y', 'f8'),
                               ('z', 'f8'), ('xerr', 'f8'), ('yerr', 'f8'),
                               ('zerr', 'f8')])

    comb_arr['x'] = comb_arr['x'] + pts_offset[0]
    comb_arr['y'] = comb_arr['y'] + pts_offset[1]
    comb_arr['z'] = comb_arr['z'] + pts_offset[2]

    np.savetxt(out_cloud_path, comb_arr, delimiter=" ",
               header="x y z xerr yerr zerr", comments='')

    if os.path.exists(os.path.join(dir_path, 'Temp_PointCloud.ply')):
        os.remove(os.path.join(dir_path, 'Temp_PointCloud.ply'))


def update(existingAggregate, newValue):
    (n, count, mean, M2) = existingAggregate
    n += 1
    count = count.__iadd__(1)
    delta = np.subtract(newValue, mean)
    mean = mean.__iadd__(np.divide(delta, count))
    # mean += np.divide(delta, count)
    delta2 = np.subtract(newValue, mean)
    M2 = M2.__iadd__(np.multiply(delta, delta2))
    # M2 += delta * delta2

    return (n, count, mean, M2)

# Retrieve the mean, variance and sample variance from an aggregate
def finalize(existingAggregate):
    (n, count, mean, M2) = existingAggregate
    (mean, variance, sampleVariance) = (mean, M2 / count, M2 / (count - 1))
    if n < 2:
        return float('nan')
    else:
        return (mean, variance, sampleVariance)

def retrieve_shape_precision(chunk, camera_index, npoints, points):
    with open(os.path.join(fold_path,'_observation_distances.txt'), "w") as f:
        fwriter = csv.writer(f, dialect='excel-tab', lineterminator='\n')
        for camera in chunk.cameras:
            camera_index += 1
            if not camera.transform:
                continue

            fx = camera.sensor.calibration.fx

            # Accommodate change in attribute name in v.1.2.5
            # try:
            #    fx = camera.sensor.calibration.fx
            # except AttributeError:
            #     fx = camera.sensor.calibration.f

            point_index = 0
            for proj in chunk.point_cloud.projections[camera]:
                track_id = proj.track_id
                while point_index < npoints and points[point_index].track_id < track_id:
                    point_index += 1
                if point_index < npoints and points[point_index].track_id == track_id:
                    if not points[point_index].valid:
                        continue
                    dist = (chunk.transform.matrix.mulp(camera.center) - chunk.transform.matrix.mulp(Metashape.Vector(
                        [points[point_index].coord[0], points[point_index].coord[1], points[point_index].coord[2]]))).norm()
                    fwriter.writerow([camera_index, '{0:.4f}'.format(dist / fx), '{0:.2f}'.format(dist)])

        f.close()

# Metashape.app.document.remove([original_chunk])


if __name__ == '__main__':
    KickOff()
    print("Total Time: " + str(datetime.now() - startTime))
