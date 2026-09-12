# -*- coding: utf-8 -*-
from __future__ import print_function

import gettext
import os

try:
    from Components.Language import language
except Exception:
    language = None

PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
LOCALE_PATH = os.path.join(PLUGIN_PATH, 'locale')
DOMAIN = 'PiconHub'


def localeInit():
    try:
        if language is not None:
            lang = language.getLanguage()[:2]
            os.environ['LANGUAGE'] = lang
        gettext.bindtextdomain(DOMAIN, LOCALE_PATH)
    except Exception as e:
        print('[PiconHub] gettext bind error:', e)


localeInit()
try:
    if language is not None:
        language.addCallback(localeInit)
except Exception as e:
    print('[PiconHub] language callback error:', e)


def _(txt):
    try:
        translated = gettext.dgettext(DOMAIN, txt)
        return translated if translated else txt
    except Exception:
        return txt


# Extend the provider area from the live server catalog while keeping the
# existing provider/update implementation in plugin.py unchanged.
try:
    from . import provider_extension  # noqa: F401
except Exception as e:
    print('[PiconHub] provider extension load error:', e)

# GitHub self-updater. The public piconhub-server repository is used as the
# update distribution channel so no private GitHub token is stored in a box.
try:
    from . import plugin_updater  # noqa: F401
except Exception as e:
    print('[PiconHub] plugin updater load error:', e)
