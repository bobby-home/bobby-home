import os

from django import template
from django.utils.html import format_html
from django.conf import settings

from template_addons.assets_helper import AssetsHelper

register = template.Library()


assets_uri = os.environ['ASSETS_DEV_SERVER']
public_asset = os.environ['PUBLIC_ASSET']
env = os.getenv('ENV', 'prod')

assets_helper = AssetsHelper(env, public_asset, assets_uri, 'manifest.json')

def _inject_vite_dev():
    return f'<script type="module" src="{assets_uri}/@vite/client"></script>'

INIT = False

@register.simple_tag()
def assets(filename: str):
    global INIT
    to_inject = ''

    if INIT is False and settings.ENV == 'dev':
        INIT = True
        to_inject += _inject_vite_dev()

    paths = assets_helper.path(filename)

    for path in paths:
        ext = path.split('.')[-1]
        print(f'ext={ext} file={path}')

        if ext == 'css':
            to_inject += '<link rel="stylesheet" media="screen" href="{}">'.format(path)

        if ext == 'js':
            to_inject += '<script type="module" src="{}" defer></script>'.format(path)

    return format_html(to_inject)


@register.simple_tag()
def svg_icon(name: str):
    return format_html(f"""
    <svg class="icon icon-{name}">
      <use xlink:href="/public/svg/sprite.svg#{name}"></use>
    </svg>
    """)


@register.filter
def get_obj_attr(obj, attr):
    """
    Allows us to access property by variable value inside our templates.
    Example: `data={'monday': True}`, `day='monday'`, then we can do: `{{ data|get_obj_attr:day }}`


    Parameters
    ----------
    obj
    attr

    Returns
    -------
    Attribute of obj
    """
    return getattr(obj, attr)
