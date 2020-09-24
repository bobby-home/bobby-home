import io
import cv2
import numpy as np
from PIL.Image import Image


def pil_image_to_byte_array(image: Image, img_format='jpeg') -> bytes:
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=img_format)
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr


def cv2_image_to_byte_array(image: np.ndarray, img_format='jpg') -> bytes:
    # encode the Numpy ndarray in the specified format.
    # im_buf is the the encoded image in an one-dimension Numpy array.
    is_success, im_buf_arr = cv2.imencode(f".{img_format}", image)
    return im_buf_arr.tobytes()
