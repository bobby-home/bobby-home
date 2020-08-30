from camera.webcamvideostream import WebcamVideoStream


class VideoStream:
	def __init__(self, processFrame, resolution, framerate, src=0, usePiCamera=False):

        # If the user doesn't run the code on a PI, then the picamera module will, very likely, crashes on import.
        # That is why we import this module ONLY if usePiCamera is true.
		if usePiCamera is True:  
			from camera.pivideostream import PiVideoStream
			self.stream = PiVideoStream(processFrame, resolution, framerate)
		else:
			self.stream = WebcamVideoStream(processFrame, resolution, framerate, src)
