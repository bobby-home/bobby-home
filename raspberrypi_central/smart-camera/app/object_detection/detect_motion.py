import re
import numpy as np
from PIL import Image
from tflite_runtime.interpreter import Interpreter
from typing import List, Tuple

from object_detection.model import BoundingBox, BoundingBoxPointAndSize, ObjectBoundingBox, People


class DetectPeople:

    def __init__(self):
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

    @staticmethod
    def _bounding_box_size(bounding_box: BoundingBox) -> BoundingBoxPointAndSize:
        """
        xmax >= xmin and ymax >= ymin
        Validation has been done in BoundingBox class.
        """
        delta_x = bounding_box.xmax - bounding_box.xmin
        delta_y = bounding_box.ymax - bounding_box.ymin

        return BoundingBoxPointAndSize(x=bounding_box.xmin, y=bounding_box.ymin, w=delta_x, h=delta_y)

    @staticmethod
    def _relative_to_absolute_bounding_box(bounding_box: BoundingBox, image_width, image_height) -> ObjectBoundingBox:
        ymin, xmin, ymax, xmax = bounding_box

        xmin = int(xmin * image_width)
        xmax = int(xmax * image_width)
        ymin = int(ymin * image_height)
        ymax = int(ymax * image_height)

        # construction of the contours
        # List of (x,y) points in clockwise order <!>
        x1 = xmin
        y1 = ymax

        x2 = xmax
        y2 = ymax

        x3 = xmax
        y3 = ymin

        x4 = xmin
        y4 = ymin

        points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
        # https://stackoverflow.com/a/24174904
        contours = points.reshape((-1,1,2)).astype(np.int32)

        return ObjectBoundingBox(ymin, xmin, ymax, xmax, contours)

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
                bounding_box = self._relative_to_absolute_bounding_box(tf_bounding_box[i], WIDTH, HEIGHT)
                bounding_box_point_and_size = self._bounding_box_size(bounding_box)

                result = People(bounding_box=bounding_box, bounding_box_point_and_size=bounding_box_point_and_size, class_id=classes[i], score=scores[i])
                results.append(result)

        return results

    def process_frame(self, stream) -> Tuple[List[People], Image.Image]:
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

        return peoples, image
