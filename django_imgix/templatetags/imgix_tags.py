from django import template

from .. import get_imgix_url


register = template.Library()


@register.simple_tag
def get_imgix(image_url, alias=None, wh=None, **kwargs):
    """
    Template tag for returning an Imgix image URL.

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
    return get_imgix_url(image_url, alias=alias, wh=wh, **kwargs)
