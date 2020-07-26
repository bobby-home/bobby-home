from django import template
from django.conf import settings
import os
from jdj_tags.assets_helper import AssetsHelper

from jinja2 import lexer, nodes
from jinja2.ext import Extension

register = template.Library()

assets_uri = os.getenv('ASSETS_DEV_SERVER', None)
asset = os.getenv('WEBPACK_ASSSET', None)

if (not assets_uri and not asset):
    raise Exception("ASSETS_DEV_SERVER and WEBPACK_ASSSET environment variables are not defined so we cannot render assets.")

assets_helper = AssetsHelper(asset, assets_uri)

# @register.simple_tag
# def assets(self, asset_name, *args, **kwargs):
#     """
#     https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/#simple-tags
#     """
#     print('assets tag called')
#     return assets_helper.path(asset_name)

class Assets(Extension):
    tags = set(['assets'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_STRING)

        filename = nodes.Const(token.value)
        call = self.call_method('_assets', [filename], lineno=lineno)

        return nodes.Output([nodes.MarkSafe(call)], lineno=lineno)

    def _assets(self, filename):
        path = assets_helper.path(filename)

        name, ext = filename.split('.')
        if ext == 'css':
            return '<link rel="stylesheet" href="{}">'.format(path)
        
        if ext == 'js':
            return '<script type="module" defer src="{}"></script>'.format(path)
