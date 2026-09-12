# -*- coding: utf-8 -*-
from __future__ import print_function

# 0.6.12.17 visual implementation lives separately so the routing patch stays
# small and future updater styling can be changed without touching plugin.py.
from . import update_style_v17  # noqa: F401
from . import plugin as p
from .update_ui import PiconHubUpdateChoice


def _open_update_choice(self):
    self.session.open(PiconHubUpdateChoice)


p.PiconHubMain.quickUpdate = _open_update_choice
p.PiconHubUpdateMenu = PiconHubUpdateChoice
