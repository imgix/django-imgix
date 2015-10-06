__author__ = 'daniel.kirov'

from exceptions import AttributeError

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django import template

import imgix


register = template.Library()

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
def get_imgix(image_url, **kwargs):

    try:
        domains = settings.IMGIX_DOMAINS
    except:
        raise ImproperlyConfigured(
            "IMGIX_DOMAINS not set in settings.py"
        )

    ### Build arguments
    args = {}
    # Get arguments from settings
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


    # Build the Imgix URL
    url = builder.create_url(image_url, **kwargs)
    return url