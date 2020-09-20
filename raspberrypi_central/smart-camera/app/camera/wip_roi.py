import cv2
import numpy as np

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

cap = cv2.VideoCapture(0)

x = 14
y = 9
w = 36
h = 46
image_width = 300
image_height = 300

while(True):
    ret, frame = cap.read()

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

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
    ordered_points = order_points_new(points)

    print(ordered_points)

    # https://stackoverflow.com/a/24174904
    ctr = ordered_points.reshape((-1,1,2)).astype(np.int32)

    cv2.drawContours(frame,[ctr], 0, (0,255,0), 3)

    point = (300,400)
    frame = cv2.circle(frame, point, radius=2, color=(0, 0, 255), thickness=2)

    points = [point, (305,405)]

    results = any([cv2.pointPolygonTest(ctr, point, False) for point in points])
    print(results)

    cv2.imshow("preview", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
