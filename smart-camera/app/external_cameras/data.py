from dataclasses import dataclass


@dataclass
class HTTPCameraData:
    user: str
    password: str
    endpoint: str
