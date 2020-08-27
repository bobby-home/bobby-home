from typing import Callable
import datetime
import json
import re
import datetime

import io

from fractions import Fraction

import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter


class DetectMotion():

    def __init__(self, presenceCallback: Callable[[bool, str], None], noMorePresenceCallback: Callable):
        # State
        self._last_time_people_detected = None

        self._presenceCallback = presenceCallback
        self._noMorePresenceCallback = noMorePresenceCallback
        self._run()

    def _load_labels(self, path):
        """Loads the labels file. Supports files with or without index numbers."""
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            labels = {}
            for row_number, content in enumerate(lines):
                pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)

                if len(pair) == 2 and pair[0].strip().isdigit():
                    labels[int(pair[0])] = pair[1].strip()
                else:
                    labels[row_number] = pair[0].strip()
        
        return labels

    def _set_input_tensor(self, interpreter, image):
        """Sets the input tensor."""
        tensor_index = interpreter.get_input_details()[0]['index']
        input_tensor = interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def _get_output_tensor(self, interpreter, index):
        """Returns the output tensor at the given index."""
        output_details = interpreter.get_output_details()[index]
        tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
        return tensor

    def _detect_objects(self, interpreter, image, threshold):
        """Returns a list of detection results, each a dictionary of object info."""
        self._set_input_tensor(interpreter, image)
        interpreter.invoke()

        # Get all output details
        boxes = self._get_output_tensor(interpreter, 0)
        classes = self._get_output_tensor(interpreter, 1)
        scores = self._get_output_tensor(interpreter, 2)
        count = int(self._get_output_tensor(interpreter, 3))

        results = []
        for i in range(count):
            if scores[i] >= threshold:
                result = {
                    'bounding_box': boxes[i],
                    'class_id': classes[i],
                    'score': scores[i]
                }
            
                results.append(result)

        return results


    def _run(self):
        CAMERA_WIDTH = 640
        CAMERA_HEIGHT = 480

        args = {
            'model': 'tensorflow-object-detection/data/detect.tflite',
            'labels': 'tensorflow-object-detection/data/coco_labels.txt',
            'threshold': 0.5
        }

        labels = self._load_labels(args['labels'])
        interpreter = Interpreter(args['model'])
        interpreter.allocate_tensors()
        _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

        with picamera.PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=1) as camera:
            # Create the in-memory stream
            stream = io.BytesIO()

            for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                stream.seek(0)
                image = Image.open(stream).convert('RGB').resize((input_width, input_height), Image.ANTIALIAS)

                results = self._detect_objects(interpreter, image, args['threshold'])

                for obj in results:
                    label = labels[obj['class_id']]
                    score = obj['score']

                    if label == 'person':
                        print(f'we found {label} score={score}')
                        if self._last_time_people_detected is None:
                            print('WE NOTIFY')
                            self._presenceCallback(stream.getvalue())

                        self._last_time_people_detected = datetime.datetime.now()

                    
                time_lapsed = (self._last_time_people_detected is not None) and (datetime.datetime.now() - self._last_time_people_detected).seconds >= 5
                if time_lapsed:
                    self._last_time_people_detected = None
                    self._noMorePresenceCallback()

                # "Rewind" the stream to the beginning so we can read its content
                stream.seek(0)
                stream.truncate()

