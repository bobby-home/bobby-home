from camera.detect_motion import DetectPeople
import datetime
import struct


class Camera():

    def __init__(self, detect_motion: DetectPeople, get_mqtt_client, device_id):
        self._device_id = device_id
        self.get_mqtt_client = get_mqtt_client
        self._last_time_people_detected = None

        self._initialize = True

        self.detect_motion = detect_motion
        self._start()

    def _start(self):
        self.mqtt_client = self.get_mqtt_client(client_name=f'{self._device_id}-rpi4-alarm-motion-DETECT')
        self.mqtt_client.loop_start()

    def _needToPublishNoMotion(self):
        if self._initialize is True:
            self._initialize = False
            return True

        time_lapsed = (self._last_time_people_detected is not None) and (
            datetime.datetime.now() - self._last_time_people_detected).seconds >= 5

        if time_lapsed:
            self._last_time_people_detected = None

        return time_lapsed

    def _is_people_in_roi(self, people, image: bytes):
        pass

    def processFrame(self, frame):
        result, peoples, image = self.detect_motion.process_frame(frame)

        if result is True:
            # We have to check if people is in ROI.
            for people in peoples:
                self._is_people_in_roi(people, image)

            if self._last_time_people_detected is None:
                self._initialize = False
                self.mqtt_client.publish(f'motion/camera/{self._device_id}', struct.pack('?', 1), qos=1, retain=True)
                self.mqtt_client.publish(f'motion/picture/{self._device_id}', payload=byteArr, qos=1)

            self._last_time_people_detected = datetime.datetime.now()
        elif self._needToPublishNoMotion():
            self.mqtt_client.publish(f'motion/camera/{self._device_id}', payload=struct.pack('?', 0), qos=1, retain=True)
