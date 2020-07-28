from django.conf import settings

class AssetsHelper:
    def __init__(self, asset_path_file: str, asset_url: str):
        self._asset_path_file = asset_path_file
        self._asset_url = asset_url

    def path(self, file: str) -> str:
        if self._asset_url:
            return self._asset_url + '/' + file
        
        raise ValueError('Please add the code to handle production env.')
        # @TODO: for prod env
