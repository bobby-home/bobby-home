def video_stream_factory(process_frame, resolution, framerate, src=0, pi_camera=False):
    # If the user doesn't run the code on a PI, then the pi camera module will, very likely, crashes on import.
    # That is why we import this module ONLY if usePiCamera is true.
    if pi_camera is True:
        from camera.pivideostream import PiVideoStream
        return PiVideoStream(process_frame, resolution, framerate)
    else:
        from camera.webcamvideostream import WebcamVideoStream
        return WebcamVideoStream(process_frame, resolution, framerate, src)
