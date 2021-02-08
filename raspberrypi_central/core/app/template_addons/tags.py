import os

from django import template
from django.utils.html import format_html

from template_addons.assets_helper import AssetsHelper

register = template.Library()


assets_uri = os.getenv('ASSETS_DEV_SERVER', None)
asset = os.getenv('WEBPACK_ASSSET', None)

if not assets_uri and not asset:
    raise Exception("ASSETS_DEV_SERVER and WEBPACK_ASSSET environment variables are not defined so we cannot render assets.")

assets_helper = AssetsHelper(asset, assets_uri)


@register.simple_tag()
def assets(filename: str):
    path = assets_helper.path(filename)

    to_inject = ''

    # It seems that Vite does this for us.
    # if self._is_hmr_injected is False and settings.DEBUG:
    #     to_inject += self._add_hmr_script()

    name, ext = filename.split('.')
    if ext == 'css':
        to_inject += '<link rel="stylesheet" href="{}">'.format(path)

    if ext == 'js':
        to_inject += '<script type="module" src="{}"></script>'.format(path)

    return format_html(to_inject)


@register.simple_tag()
def svg_icon(name: str):
    return format_html(f"""
    <svg class="icon icon-{name}">
      <use xlink:href="/static/sprite.svg#{name}"></use>
    </svg>
    """)
