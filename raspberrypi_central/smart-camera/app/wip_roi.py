import cv2
import numpy as np
from image_processing.contour_collision import contour_collision
from image_processing.contour import create_contour_from_points

# cap = cv2.VideoCapture(0)

def order_points_new(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # if use Euclidean distance, it will run in error when the object
    # is trapezoid. So we should use the same simple y-coordinates order method.

    # now, sort the right-most coordinates according to their
    # y-coordinates so we can grab the top-right and bottom-right
    # points, respectively
    rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
    (tr, br) = rightMost

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")

x = 14
y = 9
w = 36
h = 46
image_width = 300
image_height = 300

while(True):
    width = 640
    height = 480

    frame = np.zeros((height, width, 3), np.uint8)
    # _, frame = cap.read()


    def scalePoint(x, y):
        new_x = (x / image_width) * width
        new_y = (y / image_height) * height

        return new_x, new_y

    x1, y1 = scalePoint(x, y + h)
    x2, y2 = scalePoint(x + w, y + h)
    x3, y3 = scalePoint(x + w, y)
    x4, y4 = scalePoint(x, y)

    # List of (x,y) points in clockwise order
    points = np.array([[x1,y1], [x2,y2], [x3,y3], [x4,y4]])

    print(points)

    roi_contours = create_contour_from_points(order_points_new(points))

    motions_points = points + 70
    motion_contours = create_contour_from_points(motions_points)

    frame = cv2.drawContours(frame, [roi_contours], 0, (0,255,0), 3)
    frame = cv2.drawContours(frame, [motion_contours], 0, (0,0,255), 3)

    # create an image filled with zeros, single-channel, same size as img.
    blank_frame = np.zeros(frame.shape[0:2])

    # copy each of the contours (assuming there's just two) to its own image. 
    # Just fill with a '1'.
    img1 = cv2.drawContours(blank_frame.copy(), [roi_contours], 0, 1, thickness=-1)
    img2 = cv2.drawContours(blank_frame.copy(), [motion_contours], 0, 1, thickness=-1)

    # now AND the two together
    intersection = np.logical_and(img1, img2)
    print(f'intersection 1: {intersection.any()}')

    # intersection2 = (img1 + img2) == 2
    # print(f'intersection 2 result: {intersection2.any()}')


    cv2.imshow("preview", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
