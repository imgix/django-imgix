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
from django import template

import imgix


register = template.Library()

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


def pick(keys, _dict):
    """
    Returns a new dictionary based on `_dict`,
    restricting keys to those in the iterable `keys`.
    """

    key_set = set(keys) & set(_dict.keys())

    return dict((key, _dict[key]) for key in key_set)


def omit(keys, _dict):
    """
    Returns a new dictionary based on `_dict`,
    restricting keys to those not in the iterable `keys`.
    """

    key_set = set(_dict.keys()) - set(keys)

    return dict((key, _dict[key]) for key in key_set)


def merge_dicts(*dicts):
    merged = {}
    for _dict in dicts:
        merged.update(_dict)
    return merged


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
])


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

"""
Template tag for returning an image from imgix.

This template tag takes the following arguments:
1. image_url -- the image URL that we will pass onto Imgix
2. any number of optional arguments, which Imgix can accept.
For reference - https://www.imgix.com/docs/reference


You must also put IMGIX_DOMAINS in your settings.py file.
Thix can be a single domain, e.g.:

        IMGIX_DOMAINS = 'test.imgix.net'

or a list of domains, if you have sharding enabled in your Imgix account, e.g.:

        IMGIX_DOMAINS = [
            'test-1.imgix.net',
            'test-2.imgix.net',
            'test-3.imgix.net',
        ]

If you do indeed use sharding, you can choose a sharding strategy by setting
IMGIX_SHARD_STRATEGY in your settings.py file.

If you want to disable HTTPS support, put IMGIX_HTTPS = False in settings.py.


This template tag returns a string that represents the Imgix URL for the image.
"""


@register.simple_tag
def get_imgix(image_url, alias=None, wh=None, **kwargs):
    _settings = get_settings()
    merged_settings = merge_dicts(_settings, kwargs)

    if alias:
        merged_settings.update(get_alias(alias))

    builder_kwargs = pick(IMGIX_URL_BUILDER_KWARGS, merged_settings)
    create_url_opts = omit(IMGIX_URL_BUILDER_KWARGS | DJANGO_IMGIX_KWARGS, merged_settings)
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
