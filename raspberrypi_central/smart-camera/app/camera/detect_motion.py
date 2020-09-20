import re
import io
import numpy as np
from PIL import Image
from tflite_runtime.interpreter import Interpreter
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class People():
    bounding_box: any
    class_id: any
    score: float


class DetectPeople():

    def __init__(self):
        self._last_time_people_detected = None

        self.args = {
            'model': 'tensorflow-object-detection/data/detect.tflite',
            'labels': 'tensorflow-object-detection/data/coco_labels.txt',
            'threshold': 0.5
        }

        self.labels = self._load_labels(self.args['labels'])
        self.interpreter = Interpreter(self.args['model'])
        self.interpreter.allocate_tensors()
        _, self.input_height, self.input_width, _ = self.interpreter.get_input_details()[0]['shape']

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

    def _detect_objects(self, interpreter, image, threshold) -> List[People]:
        """Returns a list of detection results, each a People object."""
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
                result = People(bounding_box=boxes[i], class_id=classes[i], score=scores[i])
                results.append(result)

        return results

    def process_frame(self, stream) -> Tuple[bool, List[People], Optional[Image.Image]]:
        """
        From Tensorflow examples, we have .convert('RGB') before the resize.
        We removed it because the RGB is created at the stream level (opencv or picamera).
        And actually it didn't transform the stream to RGB.
        """
        image = Image.fromarray(stream).resize(
            (self.input_width, self.input_height), Image.ANTIALIAS)

        results = self._detect_objects(
            self.interpreter, image, self.args['threshold'])

        peoples = []

        for result in results:
            label = self.labels[result.class_id]

            if label == 'person':
                peoples.append(result)

        if len(peoples) > 0:
            return True, peoples, image

        return False, peoples, None
