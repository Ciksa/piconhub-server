# -*- coding: utf-8 -*-
from __future__ import print_function

from . import update_style_v18  # noqa: F401
from . import plugin as p
from .update_ui import PiconHubUpdateChoice


def _open_update_choice(self):
    self.session.open(PiconHubUpdateChoice)


p.PiconHubMain.quickUpdate = _open_update_choice
p.PiconHubUpdateMenu = PiconHubUpdateChoice
