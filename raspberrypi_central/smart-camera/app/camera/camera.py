from camera.detect_motion import DetectPeople, People
import datetime
import struct
from PIL import Image
import io
from functools import partial
import numpy as np
import cv2


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


def image_to_byte_array(image: Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='jpeg')
    imgByteArr = imgByteArr.getvalue()

    return imgByteArr


def scalePoint(old_img_width, old_img_height, new_img_width, new_img_height, x, y):
    new_x = (x / old_img_width) * new_img_width
    new_y = (y / old_img_height) * new_img_height

    return new_x, new_y


class Camera():

    def __init__(self, detect_motion: DetectPeople, get_mqtt_client, device_id):
        self._device_id = device_id
        self.get_mqtt_client = get_mqtt_client
        self._last_time_people_detected = None

        self._initialize = True

        self.detect_motion = detect_motion
        self._start()

    def _start(self):
        self.mqtt_client = self.get_mqtt_client(client_name=f'{self._device_id}-rpi4-alarm-motion-DETECT')
        self.mqtt_client.loop_start()

    def _needToPublishNoMotion(self):
        if self._initialize is True:
            self._initialize = False
            return True

        time_lapsed = (self._last_time_people_detected is not None) and (
            datetime.datetime.now() - self._last_time_people_detected).seconds >= 5

        if time_lapsed:
            self._last_time_people_detected = None

        return time_lapsed

    def _get_roi_contour(self, image: Image.Image):
        # x = 14
        # y = 9
        # w = 36
        # h = 46
        x = 128
        y = 185
        w = 81
        h = 76
        old_img_width = 300
        old_image_height = 300

        WIDTH, HEIGHT = image.size

        print(f'old size: {old_img_width} {old_image_height}, new size: {WIDTH} {HEIGHT}')

        scalePointToImg = partial(scalePoint, old_img_width, old_image_height, WIDTH, HEIGHT)

        x1, y1 = scalePointToImg(x, y + h)
        x2, y2 = scalePointToImg(x + w, y + h)
        x3, y3 = scalePointToImg(x + w, y)
        x4, y4 = scalePointToImg(x, y)

        # List of (x,y) points in clockwise order
        points = np.array([[x1,y1], [x2,y2], [x3,y3], [x4,y4]])
        # points = order_points_new(points)

        # https://stackoverflow.com/a/24174904
        ctr = points.reshape((-1,1,2)).astype(np.int32)
        return ctr

    def _people_bounding_box(self, people: People, image: Image.Image):
        WIDTH, HEIGHT = image.size

        # Convert the bounding box figures from relative coordinates
        # to absolute coordinates based on the original resolution
        ymin, xmin, ymax, xmax = people.bounding_box
        xmin = int(xmin * WIDTH)
        xmax = int(xmax * WIDTH)
        ymin = int(ymin * HEIGHT)
        ymax = int(ymax * HEIGHT)

        x1 = xmin
        y1 = ymax

        x2 = xmax
        y2 = ymax

        x3 = xmax
        y3 = ymin

        x4 = xmin
        y4 = ymin

        # List of (x,y) points in clockwise order
        points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
        points = order_points_new(points)

        # https://stackoverflow.com/a/24174904
        ctr = points.reshape((-1,1,2)).astype(np.int32)

        return points, ctr

    def _is_people_in_roi(self, roi_contour, points,  people: People, image: Image.Image):
        for point in points:
            result = cv2.pointPolygonTest(roi_contour, tuple(point), False)
            if result == 1:
                print(f'point {tuple(point)} in roi')
                return True

        return False
        # return any([cv2.pointPolygonTest(roi_contour, tuple(point), False) for point in points])

    def processFrame(self, frame):
        result, peoples, image = self.detect_motion.process_frame(frame)

        """
        TODO:
        - one function to create the ROI contour -> call it in constructor & create a property.
        - one function to get 4 points from bounding box of people
        - draw the bounding box of people to debug.
        """

        if result is True:
            roi_contour = self._get_roi_contour(image)
            print(f'points roi_contour: {roi_contour}')

            opencvImage = cv2.drawContours(np.array(image), [roi_contour], 0, (0,255,0), 2)

            peoples_in_roi = []
            for people in peoples:
                points, ctr = self._people_bounding_box(people, image)

                print(f'points people bounding box: {points}')
    
                opencvImage = cv2.drawContours(opencvImage, [ctr], 0, (0,0,255), 2)

                r = self._is_people_in_roi(roi_contour, points, people, image)
                peoples_in_roi.append(r)

            is_anybody_in_roi = any(peoples_in_roi)

            print(f'is_anybody_in_roi = {is_anybody_in_roi}, {peoples_in_roi}')

            # is_anybody_in_roi and
            if self._last_time_people_detected is None:
                self._initialize = False
                self.mqtt_client.publish(f'motion/camera/{self._device_id}', struct.pack('?', 1), qos=1, retain=True)

                byteArr = image_to_byte_array(Image.fromarray(opencvImage))
                # byteArr = opencvImage.tobytes()

                self.mqtt_client.publish(f'motion/picture/{self._device_id}', payload=byteArr, qos=1)

            self._last_time_people_detected = datetime.datetime.now()
        elif self._needToPublishNoMotion():
            self.mqtt_client.publish(f'motion/camera/{self._device_id}', payload=struct.pack('?', 0), qos=1, retain=True)
