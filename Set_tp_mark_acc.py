import Metashape
import math
# import os
# import csv
# import inspect
# from datetime import datetime

def main():
    doc = Metashape.app.document
    chunk = doc.chunk
    point_cloud = chunk.point_cloud
    points = point_cloud.points
    projections = chunk.point_cloud.projections
    total_error = calc_reprojection_error(chunk, points, projections)  # calculate reprojection error

    reproj_error = sum(total_error) / len(total_error)  # get average rmse for all cameras

    print("mean reprojection error for point cloud:")
    print(round(reproj_error, 3))

    tiepoint_acc = (round(reproj_error, 2))
    chunk.tiepoint_accuracy = tiepoint_acc
    chunk.marker_projection_accuracy = tiepoint_acc
    doc.save()

def calc_reprojection_error(chunk, points, projections):

    npoints = len(points)

    photo_avg = []

    for camera in chunk.cameras:
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

                dist = camera.error(points[point_index].coord, proj.coord).norm() ** 2  # get the square error for each point in camera

                photo_num += 1 # counts number of points per camera
                photo_err += dist # creates list of square point errors

        photo_avg.append(math.sqrt(photo_err / photo_num))  # get root mean square error for each camera

    return photo_avg  # returns list of rmse values for each camera


if __name__ == '__main__':
    main()