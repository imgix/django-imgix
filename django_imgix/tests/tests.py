from django.template import Context, Template
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class MyTest(TestCase):
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_correct_url_is_generated(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg"
            )

    def test_arguments_are_used_correctly(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' h=100 w=250 lossless=1 auto='format' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=100&lossless=1&w=250"
            )

    def test_no_https(self):

        domains = 'test1.imgix.net'
        https = False

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_HTTPS=https):
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertEqual(
                rendered,
                "http://test1.imgix.net/media/image/image_0001.jpg"
            )

    def test_sharding(self):

        domains = [
            'test1.imgix.net',
            'test2.imgix.net',
            'test3.imgix.net',
        ]

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertIn(
                rendered,
                [
                "https://test1.imgix.net/media/image/image_0001.jpg",
                "https://test2.imgix.net/media/image/image_0001.jpg",
                "https://test3.imgix.net/media/image/image_0001.jpg",
                ]
            )

    def test_sign_key(self):

        domains = 'test1.imgix.net'
        key = '1234test'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_SIGN_KEY=key):
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?s=3ffb2810efc98cca7de5cd9c8ee6aec1"
            )

    def test_alias_as_unnamed_argument(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' 'alias_one' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&w=150"
            )

    def test_alias_as_named_argument(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' alias='alias_one' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&w=150"
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
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' 'alias_one' "
                "w=111 h=222 auto='override' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&w=150"
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
            rendered = self.render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' alias='alias_one' "
                "w=111 h=222 auto='override' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&w=150"
            )


    def test_missing_alias_gives_useful_error(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            try:
                rendered = self.render_template(
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
                rendered = self.render_template(
                    "{% load imgix_tags %}"
                    "{% get_imgix 'media/image/image_0001.jpg' alias='alias_two' "
                    "w=111 h=222 auto='override' %}"
                )
            except ImproperlyConfigured as e:
                self.assertEqual(
                    str(e),
                    "No aliases set. Please set IMGIX_ALIASES in settings.py"
                )
