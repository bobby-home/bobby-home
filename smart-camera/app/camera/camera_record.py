from abc import ABC, abstractmethod


class CameraRecorder(ABC):

    @abstractmethod
    def start_recording(self, video_ref: str) -> None:
        pass

    @abstractmethod
    def split_recording(self, video_ref: str) -> None:
        pass

    @abstractmethod
    def stop_recording(self) -> None:
        pass


class DumbCameraRecorder(CameraRecorder):
    """Class to communicate with dumb camera to orchestrate video recording.
    """
    def __init__(self, mqtt_client, device_id: str):
        self._device_id = device_id
        self.mqtt_client = mqtt_client

    def stop_recording(self) -> None:
        self.mqtt_client.publish(f'camera/recording/{self._device_id}/end', qos=2)

    def start_recording(self, video_ref: str) -> None:
        self.mqtt_client.publish(f'camera/recording/{self._device_id}/start/{video_ref}', qos=2)

    def split_recording(self, video_ref: str) -> None:
        self.mqtt_client.publish(f'camera/recording/{self._device_id}/split/{video_ref}', qos=2)
