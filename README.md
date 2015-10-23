Django imgix
============

[![Build Status](https://travis-ci.org/pancentric/django-imgix.png?branch=master)](https://travis-ci.org/pancentric/django-imgix)

A simple Django application for creating imgix formatted image links in your templates


Installation
------------

Dependencies:
This app requires Django > 1.4 and imgix>0.1


1. Run ```  pip install django-imgix  ```
2. Add ``` 'django-imgix' ``` to your ``` INSTALLED_APPS ```:




```
	INSTALLED_APPS = (
		...
		'django-imgix',
	)
```


----------


Configuration
-------------
There are a few settings you can use to configure how django-imgix works:

**IMGIX_DOMAINS** (*required*) - Give the domain name, or list of domain names, that you have registered with Imgix.net:
```
IMGIX_DOMAINS = 'my-domain.imgix.net'
...
or
...
IMGIX_DOMAINS = [
	'my-domain-1.imgix.net',
	'my-domain-2.imgix.net',
	'my-domain-3.imgix.net',
	]
```

**IMGIX_HTTPS** - Boolean value, defaults to `False` if not specified. If set to `True` it enables HTTPS support.

**IMGIX_SIGN_KEY**  - If you want to produce signed URLs you need to enable secure URLs in the 'Source' tab in your Imgix.net account. This will generate a secret key that you need to specify here, e.g.

```
IMGIX_SIGN_KEY = 'jUIrLPuMEm2aCRj'
```

**IMGIX_DETECT_FORMAT** - Boolean value, defaults to `False` if not specified. If set to `True` django-imgix will automatically detect popular image extensions and apply the `fm=image_extension` attribute to the image url, where `image_extension`  is one of the formats listed [here](https://www.imgix.com/docs/reference/format#param-fm "Imgix fm parameter")


Example:
```
{% load imgix_tags %}
{% get_imgix '/media/images/dsc_0001.jpg' w=1280 h=720 %}
```
will produce

` https://my-domain.imgix.net/media/images/dsc_0001.jpg?fm=jpg&h=720&w=1280`


Currently supported image formats for IMGIX_DETECT_FORMAT are jpg, jpeg, png, gif, jp2, jxr and webp.


**IMGIX_ALIASES** - Read about aliases in the **Usage** section below.


----------


Usage
-----

In your template:

```
{% load imgix_tags %}
<img src="{% get_imgix 'image_url' key=value ... %}"/>
```

You can add as many `key=value` pairs as you want. Each `key=value` pair results in a url parameter
that Imgix can recognise and use to generate your thumbnail.

For a full list of supported parameters, see [here](https://www.imgix.com/docs/reference/ "Imgix API reference")

There is a special argument, `wh=WIDTHxHEIGHT`, which is made specifically so that transition from other image processing libraries such as **easy_thumbnails** is easier.
For example,
`{% get_imgix '/media/images/dsc_0001.jpg' wh='1280x720' %}`
is the same as saying
`{% get_imgix '/media/images/dsc_0001.jpg' w=1280 h=720 %}`
which resolves to
`http://my-domain.imgix.net/media/images/dsc_0001.jpg?h=720&w=1280`

#### **Aliases**

If you don't want to list all your `key=value` parameters inline all the time, you can group them into aliases.

To do that, first specify the aliases in your settings file:
```
IMGIX_ALIASES = {
        'alias_one': {'w': 200, 'h': 300, 'lossless': 1, 'auto': 'format'},
        'alias_two': {'w': 450, 'h': 160, 'fm':'jpg', 'q': 70 },
    }

```

Then, in your template, either simply provide the alias name as the first unnamed argument, or use `alias='alias_name'`:
```
{% load imgix_tags %}
<img src="{% get_imgix 'image_url' 'alias_one' %}"/>
... or ...
<img src="{% get_imgix 'image_url' alias='alias_one' %}"/>
```

