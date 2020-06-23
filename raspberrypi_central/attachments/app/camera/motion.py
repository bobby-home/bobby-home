from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import json
import time
import cv2
from .tempimage import TempImage
from typing import Callable

conf = json.load(open('camera/motion-conf.json', 'r'))

def grab_contours(cnts):
    # if the length the contours tuple returned by cv2.findContours
    # is '2' then we are using either OpenCV v2.4, v4-beta, or
    # v4-official
    if len(cnts) == 2:
        cnts = cnts[0]

    # if the length of the contours tuple is '3' then we are using
    # either OpenCV v3, v4-pre, or v4-alpha
    elif len(cnts) == 3:
        cnts = cnts[1]

    # otherwise OpenCV has changed their cv2.findContours return
    # signature yet again and I have no idea WTH is going on
    else:
        raise Exception(("Contours tuple must have length 2 or 3, "
            "otherwise OpenCV changed their cv2.findContours return "
            "signature yet again. Refer to OpenCV's documentation "
            "in that case"))

    # return the actual contours array
    return cnts


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized

class DetectMotion():

    def __init__(self, presenceCallback: Callable[[bool, str], None]):
        # Initialize RPI Camera.
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(640, 480))
        # allow the self.camera to warmup
        time.sleep(0.1)

        # State
        self.avg = None
        self.lastUploaded = datetime.datetime.now()
        self.motionCounter = 0

        self.presenceCallback = presenceCallback
        self._run()

    def _run(self):
        # capture frames from the camera continuously (so it's a video)
        for f in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image
            frame = f.array
            text = "Unoccupied"

            frame = resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the average frame is None, initialize it
            if self.avg is None:
                print("[INFO] starting background model...")
                self.avg = gray.copy().astype("float")
                self.rawCapture.truncate(0)
                continue

            # accumulate the weighted average between the current frame and
            # previous frames, then compute the difference between the current
            # frame and running average
            cv2.accumulateWeighted(gray, self.avg, 0.5)
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))
            
            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = grab_contours(cnts)
        
            # loop over the contours
            for c in cnts:

                # if the contour is too small, ignore it
                if cv2.contourArea(c) < conf["min_area"]:
                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"

                if text == "Occupied":
                    timestamp = datetime.datetime.now()

                    # check to see if enough time has passed between uploads
                    if (timestamp - self.lastUploaded).seconds >= conf["min_upload_seconds"]:
                        # increment the motion counter
                        self.motionCounter += 1

                        # check to see if the number of frames with consistent motion is
                        # high enough
                        if self.motionCounter >= conf["min_motion_frames"]:
                            # write the image to temporary file
                            t = TempImage()
                            print(f'Write {t.path} image.')
                            cv2.imwrite(t.path, frame)

                            self.presenceCallback(True, t.path)

                            # upload the image to Dropbox and cleanup the tempory image
                            # print("[UPLOAD] {}".format(ts))
                            # path = "/{base_path}/{timestamp}.jpg".format(
                            #     base_path=conf["dropbox_base_path"], timestamp=ts)
                            # client.files_upload(open(t.path, "rb").read(), path)
                            # t.cleanup()

                            # update the last uploaded timestamp and reset the motion
                            # counter
                            self.lastUploaded = timestamp
                            self.motionCounter = 0

                # otherwise, the room is not occupied
                else:
                    self.motionCounter = 0
                    self.presenceCallback(False)
        
            # clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)
