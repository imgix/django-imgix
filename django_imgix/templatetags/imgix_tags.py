from django import template

from .. import get_imgix_url


register = template.Library()

get_imgix = register.simple_tag(get_imgix_url, name='get_imgix')
