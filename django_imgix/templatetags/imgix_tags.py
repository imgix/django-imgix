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

def get_settings_variables():
    try:
        use_https = settings.IMGIX_HTTPS
    except AttributeError:
        use_https = True
    try:
        sign_key = settings.IMGIX_SIGN_KEY
    except AttributeError:
        sign_key = None
    try:
        shard_strategy = settings.IMGIX_SHARD_STRATEGY
    except AttributeError:
        shard_strategy = None
    try:
        aliases = settings.IMGIX_ALIASES
    except AttributeError:
        aliases = None
    try:
        format_detect = settings.IMGIX_DETECT_FORMAT
    except AttributeError:
        format_detect = False
    return shard_strategy, sign_key, use_https, aliases, format_detect


def get_kwargs(alias, aliases, kwargs):

    # Check if we are using an alias or inline arguments
    if not alias:
        return kwargs
    elif not aliases:
        raise ImproperlyConfigured(
            "No aliases set. Please set IMGIX_ALIASES in settings.py"
        )
    elif alias not in aliases:
        raise ImproperlyConfigured(
            "Alias {0} not found in IMGIX_ALIASES".format(alias)
        )
    else:
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

    try:
        domains = settings.IMGIX_DOMAINS
    except:
        raise ImproperlyConfigured(
            "IMGIX_DOMAINS not set in settings.py"
        )

    ### Build arguments
    args = {}

    # Get arguments from settings
    shard_strategy, sign_key, use_https, aliases,\
        format_detect = get_settings_variables()

    args['use_https'] = use_https

    if sign_key:
        args['sign_key'] = sign_key

    if shard_strategy:
        args['shard_strategy'] = shard_strategy

    # Imgix by default appends ?ixlib=python-<version_number> to the end
    # of the URL, but we don't want that.
    args['sign_with_library_version'] = False

    # Get builder instance
    builder = imgix.UrlBuilder(
        domains,
        **args
    )

    # Has the wh argument been passed? If yes,
    # set w and h arguments accordingly
    if wh:
        size = wh
        if isinstance(size, six.string_types):
            m = WH_PATTERN.match(size)
            if m:
                w = int(m.group(1))
                h = int(m.group(2))
                if w > 0:
                    kwargs['w'] = int(m.group(1))
                if h > 0:
                    kwargs['h'] = int(m.group(2))
            else:
                raise TemplateSyntaxError(
                    "%r is not a valid size." % size
                )

    # Is format detection on? If yes, use the appropriate image format.

    arguments = get_kwargs(alias, aliases, kwargs)

    if format_detect and 'fm' not in arguments:
        fm = get_fm(image_url)
        if fm:
            arguments['fm'] = fm

    # Take only the relative path of the URL
    image_url = urlparse(image_url).path

    # Build the Imgix URL
    url = builder.create_url(image_url, arguments)
    return url
