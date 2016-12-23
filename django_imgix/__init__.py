__author__ = 'daniel.kirov'

import re
try:
    from urlparse import urlparse
except ImportError:
    # Python 3 location
    from urllib.parse import urlparse

from django.utils import six
from django.template import TemplateSyntaxError
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import imgix

from .utils import pick, omit, merge_dicts


WH_PATTERN = re.compile(r'(\d+)x(\d+)$')

FM_PATTERN = re.compile(r'([^\?]+)')
FM_MATCHES = {
    'jpg': 'jpg',
    'jpeg': 'jpg',
    'png': 'png',
    'gif': 'gif',
    'jp2': 'jp2',
    'jxr': 'jxr',
    'webp': 'webp',
}


def get_settings():
    try:
        _settings = {
            'domains': getattr(settings, 'IMGIX_DOMAINS'),
            'use_https': getattr(settings, 'IMGIX_HTTPS', True),
            'sign_key': getattr(settings, 'IMGIX_SIGN_KEY', None),
            'shard_strategy': getattr(settings, 'IMGIX_SHARD_STRATEGY', None),
            'aliases': getattr(settings, 'IMGIX_ALIASES', None),
            'format_detect': getattr(settings, 'IMGIX_DETECT_FORMAT', False),
            'web_proxy': getattr(settings, 'IMGIX_WEB_PROXY_SOURCE', False),
            'sign_with_library_version': getattr(settings, 'IMGIX_SIGN_WITH_LIBRARY_VERSION', False)
        }
    except AttributeError:
        raise ImproperlyConfigured('Missing IMGIX_DOMAINS setting.')

    # If these settings below are not present, we want to omit it the key
    # so that `imgix-python` applies it's default.

    try:
        _settings['sign_mode'] = settings.IMGIX_SIGN_MODE
    except AttributeError:
        pass

    try:
        _settings['shard_strategy'] = settings.IMGIX_SHARD_STRATEGY
    except AttributeError:
        pass

    return _settings


def get_alias(alias):
    try:
        aliases = settings.IMGIX_ALIASES
    except AttributeError:
        aliases_set = False
    else:
        aliases_set = True

    if aliases_set and not aliases:
        raise ImproperlyConfigured(
            "No aliases set. Please set IMGIX_ALIASES in settings.py"
        )

    if not aliases or alias not in aliases:
        raise ImproperlyConfigured(
            "Alias {0} not found in IMGIX_ALIASES".format(alias)
        )

    return aliases[alias]


def get_fm(image_url):
    image_end = image_url.split('.')[-1]
    m = FM_PATTERN.match(image_end)
    if m:
        fm = m.group(1)
        try:
            format = FM_MATCHES[fm]
            return format
        except:
            return False
    else:
        return False


IMGIX_URL_BUILDER_KWARGS = frozenset([
    'domains',
    'sign_mode',
    'sign_with_library_version',
    'use_https',
    'sign_key',
    'shard_strategy',
])

DJANGO_IMGIX_KWARGS = frozenset([
    'format_detect',
    'alias',
    'aliases',
    'web_proxy',
    'wh',
])

NON_IMGIX_API_KWARGS = IMGIX_URL_BUILDER_KWARGS | DJANGO_IMGIX_KWARGS


def get_imgix_url(image_url, alias=None, wh=None, **kwargs):
    """
    Returns an Imgix image URL.

    In `kwargs`, keys that correspond to `django-imgix` settings will override them. They are:

    - `use_https` overrides `IMGIX_HTTPS`
    - `web_proxy` overrides `IMGIX_WEB_PROXY`
    - `domains` overrides `IMGIX_DOMAINS`
    - `sign_key` overrides `IMGIX_SIGN_KEY`
    - `shard_strategy` overrides `IMGIX_SHARD_STRATEGY`
    - `aliases` overrides `IMGIX_ALIASES`
    - `format_detect` overrides `IMGIX_FORMAT_DETECT`

    Others will be passed to the Imgix API. See https://www.imgix.com/docs/reference

    This template tag returns a string that represents the Imgix URL for the image.

    :param image_url: the image URL that we will pass onto Imgix
    :param alias: An optional alias name corresponding to a key in IMGIX_ALIASES setting.
    :param wh: An optional string in the format '600x400'.
    :param kwargs: optional, arbitrary number of key-value pairs to override settings
                   and pass to the Imgix API.
    :returns: An Imgix URL
    """
    _settings = get_settings()
    merged_settings = merge_dicts(_settings, kwargs)

    if alias:
        merged_settings.update(get_alias(alias))

    builder_kwargs = pick(IMGIX_URL_BUILDER_KWARGS, merged_settings)
    create_url_opts = omit(NON_IMGIX_API_KWARGS, merged_settings)
    # Get builder instance
    builder = imgix.UrlBuilder(**builder_kwargs)

    # Has the wh argument been passed? If yes,
    # set w and h arguments accordingly
    if wh:
        create_url_opts.update(parse_wh(wh))

    # Is format detection on? If yes, use the appropriate image format.

    if merged_settings['format_detect'] and 'fm' not in create_url_opts:
        fm = get_fm(image_url)
        if fm:
            create_url_opts['fm'] = fm

    # Take only the relative path of the URL if the source is not a Web Proxy Source
    if not merged_settings['web_proxy']:
        image_url = urlparse(image_url).path

    # Build the Imgix URL
    url = builder.create_url(image_url, create_url_opts)
    return url


def parse_wh(wh):
    size = wh
    if not isinstance(size, six.string_types):
        raise TemplateSyntaxError(
            "Invalid argument type for 'wh': %s" % wh
        )

    m = WH_PATTERN.match(size)

    if not m:
        raise TemplateSyntaxError(
            "%r is not a valid size." % size
        )

    w = int(m.group(1))
    h = int(m.group(2))

    result = {}
    if w > 0:
        result['w'] = w
    if h > 0:
        result['h'] = h

    return result
