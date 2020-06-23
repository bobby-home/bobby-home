from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import json
import time
import cv2
from tempimage import TempImage

conf = json.load(open('./conf.json'))

print(conf)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

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


# capture frames from the camera continuously (so it's a video)
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image
    frame = f.array
    timestamp = datetime.datetime.now()
    text = "Unoccupied"

    frame = resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the average frame is None, initialize it
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
	
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
            # check to see if enough time has passed between uploads
            if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
                # increment the motion counter
                motionCounter += 1
                print(cv2.contourArea(c), conf["min_area"])


                # check to see if the number of frames with consistent motion is
                # high enough
                if motionCounter >= conf["min_motion_frames"]:
                    # write the image to temporary file
                    t = TempImage()
                    cv2.imwrite(t.path, frame)

                    print("TAKE A PICTURE")

                    # upload the image to Dropbox and cleanup the tempory image
                    # print("[UPLOAD] {}".format(ts))
                    # path = "/{base_path}/{timestamp}.jpg".format(
                    #     base_path=conf["dropbox_base_path"], timestamp=ts)
                    # client.files_upload(open(t.path, "rb").read(), path)
                    # t.cleanup()

                    # update the last uploaded timestamp and reset the motion
                    # counter
                    lastUploaded = timestamp
                    motionCounter = 0

        # otherwise, the room is not occupied
        else:
            motionCounter = 0
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
 