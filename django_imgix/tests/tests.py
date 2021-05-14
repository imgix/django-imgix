from django.template import Context, Template
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_imgix.templatetags._version import __version__

def render_template(string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

class GeneralImgixTests(TestCase):
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_correct_url_is_generated(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?ixlib=python-{0}".format(__version__)
            )

    def test_arguments_are_used_correctly(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' h=100 w=250 lossless=1 auto='format' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=100&ixlib=python-{0}&lossless=1&w=250".format(__version__)
            )

    def test_no_https(self):

        domains = 'test1.imgix.net'
        https = False

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_HTTPS=https):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertEqual(
                rendered,
                "http://test1.imgix.net/media/image/image_0001.jpg?ixlib=python-{0}".format(__version__)
            )

    def test_sharding(self):

        domains = [
            'test1.imgix.net',
            'test2.imgix.net',
            'test3.imgix.net',
        ]

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertIn(
                rendered,
                [
                "https://test1.imgix.net/media/image/image_0001.jpg?ixlib=python-{0}".format(__version__),
                "https://test2.imgix.net/media/image/image_0001.jpg?ixlib=python-{0}".format(__version__),
                "https://test3.imgix.net/media/image/image_0001.jpg?ixlib=python-{0}".format(__version__),
                ]
            )

    def test_sign_key(self):

        domains = 'test1.imgix.net'
        key = '1234test'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_SIGN_KEY=key):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?ixlib=python-{0}&s=69cce16d20a22e7bd5dbb53a2c276827".format(__version__)
            )

    def test_alias_as_unnamed_argument(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' 'alias_one' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&ixlib=python-{0}&w=150".format(__version__)
            )

    def test_alias_as_named_argument(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' alias='alias_one' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&ixlib=python-{0}&w=150".format(__version__)
            )

    # Test that if there is a valid alias specified all other arguments will
    # be ignored
    def test_alias_as_unnamed_argument_with_other_arguments(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' 'alias_one' "
                "w=111 h=222 auto='override' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&ixlib=python-{0}&w=150".format(__version__)
            )


    # Test that if there is a valid alias specified all other arguments will
    # be ignored
    def test_alias_as_named_argument_with_other_arguments(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' alias='alias_one' "
                "w=111 h=222 auto='override' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&ixlib=python-{0}&w=150".format(__version__)
            )


    def test_missing_alias_gives_useful_error(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            try:
                rendered = render_template(
                    "{% load imgix_tags %}"
                    "{% get_imgix 'media/image/image_0001.jpg' alias='alias_two' "
                    "w=111 h=222 auto='override' %}"
                )
            except ImproperlyConfigured as e:
                self.assertEqual(
                    str(e),
                    "Alias alias_two not found in IMGIX_ALIASES"
                )


    def test_no_aliases_specified_gives_useful_error(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=None):
            try:
                rendered = render_template(
                    "{% load imgix_tags %}"
                    "{% get_imgix 'media/image/image_0001.jpg' alias='alias_two' "
                    "w=111 h=222 auto='override' %}"
                )
            except ImproperlyConfigured as e:
                self.assertEqual(
                    str(e),
                    "No aliases set. Please set IMGIX_ALIASES in settings.py"
                )


    def test_wh_argument(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' wh='1024x768' "
                " %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?h=768&ixlib=python-{0}&w=1024".format(__version__)
            )



    def test_wh_argument_overrides_w_and_h(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' wh='1024x768' "
                "w=111 h=222 auto='format' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=768&ixlib=python-{0}&w=1024".format(__version__)
            )


    def test_wh_with_h_0_argument_overrides_w_but_not_h(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' wh='1024x0' "
                "w=111 h=222 auto='format' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=222&ixlib=python-{0}&w=1024".format(__version__)
            )


    def test_wh_with_w_0_argument_overrides_h_but_not_w(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' wh='0x768' "
                "w=111 h=222 auto='format' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=768&ixlib=python-{0}&w=111".format(__version__)
            )


    def test_wh_with_w_0_and_h_0_arguments_does_nothing(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' wh='0x0' "
                "w=111 h=222 auto='format' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=222&ixlib=python-{0}&w=111".format(__version__)
            )

    def test_web_proxy_setting_keeps_full_url(self):
        domains = 'test1.imgix.net'
        key = '1234key'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True,
                           IMGIX_SIGN_KEY=key):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'i.imgur.net/media/image/image_0001.jpg' fm='png' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/i.imgur.net/media/image/image_0001.jpg?fm=png&ixlib=python-{0}&s=712265624f9c721872dc19e1cf356fbf".format(__version__)
            )


# Tests related to the IMGIX_DETECT_FORMAT option
class DetectFormatTests(TestCase):


    def test_jpg_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?fm=jpg&ixlib=python-{0}".format(__version__)
            )


    def test_jpeg_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpeg' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpeg?fm=jpg&ixlib=python-{0}".format(__version__)
            )


    def test_png_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.png' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.png?fm=png&ixlib=python-{0}".format(__version__)
            )


    def test_gif_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.gif' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.gif?fm=gif&ixlib=python-{0}".format(__version__)
            )


    def test_webp_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.webp' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.webp?fm=webp&ixlib=python-{0}".format(__version__)
            )


    def test_fm_in_alias_overrides_detect_format(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_fm': {'fm': 'png'}
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True,
                           IMGIX_ALIASES=aliases):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' 'alias_fm' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?fm=png&ixlib=python-{0}".format(__version__)
            )


    def test_inline_fm_argument_overrides_detect_format(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' fm='png' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?fm=png&ixlib=python-{0}".format(__version__)
            )


