from typing import List

from django.conf import settings
import json
import pathlib

class AssetsHelper:
    def __init__(self, env: str, public_asset: str, asset_url: str, manifest_filename: str):
        self._public_asset = public_asset
        self._asset_url = asset_url
        self._env = env
        self._manifest_filename = manifest_filename
        self._manifest = self._load_manifest()

    def _load_manifest(self):
        manifest_data = pathlib.Path(f'{self._public_asset}/{self._manifest_filename}')
        with open(manifest_data) as json_file:
            return json.load(json_file)

    def path(self, file: str) -> List[str]:

        if self._env == 'dev':
            url = self._asset_url + '/' + file
            return [url]


        file_data = self._manifest.get(file, '')

        file_path = f'{self._public_asset}/{file_data["file"]}'
        urls = [file_path]

        css_files = file_data.get('css', None)
        if css_files:
            for css_file in css_files:
                urls.append(f'{self._public_asset}/{css_file}')

        return urls
