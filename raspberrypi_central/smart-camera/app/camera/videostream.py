class VideoStream:
    def __init__(self, process_frame, resolution, framerate, src=0, pi_camera=False):

        # If the user doesn't run the code on a PI, then the pi camera module will, very likely, crashes on import.
        # That is why we import this module ONLY if usePiCamera is true.
        if pi_camera is True:
            from camera.pivideostream import PiVideoStream
            self.stream = PiVideoStream(process_frame, resolution, framerate)
        else:
            from camera.webcamvideostream import WebcamVideoStream
            self.stream = WebcamVideoStream(process_frame, resolution, framerate, src)
