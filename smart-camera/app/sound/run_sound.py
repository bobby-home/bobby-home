from service_manager.service_manager import RunService
from sound.sound import Sound


class RunSound(RunService):

    def is_restart_necessary(self, data) -> bool:
        return False

    def prepare_run(self, data=None):
        pass

    def run(self, *args) -> None:
        Sound().alarm()


def run_sound_factory():
    return RunSound()
