from object_detection.detect_people_utils import bounding_box_size
import re
from io import BytesIO
from typing import List, Tuple
import numpy as np
from PIL import Image
from tflite_runtime.interpreter import Interpreter
from object_detection.model import BoundingBox, People


class DetectPeople:

    def __init__(self, tflite_file: str, labels_file: str):
        self.model_file = tflite_file
        self.labels_file = labels_file
        self.threshold = 0.6

        self.labels = self._load_labels(self.labels_file)
        self.interpreter = Interpreter(self.model_file)
        self.interpreter.allocate_tensors()
        _, self.input_height, self.input_width, _ = self.interpreter.get_input_details()[0]['shape']

    @staticmethod
    def _load_labels(path):
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

    @staticmethod
    def _set_input_tensor(interpreter, image):
        """Sets the input tensor."""
        tensor_index = interpreter.get_input_details()[0]['index']
        input_tensor = interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    @staticmethod
    def _get_output_tensor(interpreter, index):
        """Returns the output tensor at the given index."""
        output_details = interpreter.get_output_details()[index]
        tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
        return tensor

    @staticmethod
    def _relative_to_absolute_bounding_box(bounding_box: BoundingBox, image_width, image_height) -> BoundingBox:
        # Convert the bounding box figures from relative coordinates
        # to absolute coordinates based on the original resolution

        xmin = bounding_box.xmin
        ymin = bounding_box.ymin

        xmax = bounding_box.xmax
        ymax = bounding_box.ymax

        xmin = int(xmin * image_width)
        xmax = int(xmax * image_width)
        ymin = int(ymin * image_height)
        ymax = int(ymax * image_height)

        return BoundingBox(ymin=ymin, xmin=xmin, ymax=ymax, xmax=xmax)

    def _detect_objects(self, interpreter, image, threshold) -> List[People]:
        """Returns a list of detection results, each a People object."""
        self._set_input_tensor(interpreter, image)
        interpreter.invoke()

        # Get all output details
        tf_bounding_box = self._get_output_tensor(interpreter, 0)
        classes = self._get_output_tensor(interpreter, 1)
        scores = self._get_output_tensor(interpreter, 2)
        count = int(self._get_output_tensor(interpreter, 3))

        WIDTH, HEIGHT = image.size

        results = []
        for i in range(count):
            if scores[i] >= threshold:
                ymin, xmin, ymax, xmax = tf_bounding_box[i]

                # Tensorflow model computes things with relatives coordinate to keep numbers small which helps to make the model converge faster.
                # to exploit results, we need absolute (to the picture) coords.
                relative_bounding_box = BoundingBox(ymin=ymin, xmin=xmin, ymax=ymax, xmax=xmax)
                bounding_box = self._relative_to_absolute_bounding_box(relative_bounding_box, WIDTH, HEIGHT)

                result = People(bounding_box=bounding_box, bounding_box_point_and_size=bounding_box_size(bounding_box), class_id=classes[i], score=scores[i])
                results.append(result)

        return results

    def process_frame(self, stream: BytesIO) -> List[People]:
        image = Image.open(stream).convert('RGB').resize(
            (self.input_width, self.input_height), Image.ANTIALIAS)

        results = self._detect_objects(
            self.interpreter, image, self.threshold)

        peoples = []

        for result in results:
            label = self.labels[result.class_id]

            if label == 'person':
                peoples.append(result)

        return peoples
