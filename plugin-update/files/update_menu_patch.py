# -*- coding: utf-8 -*-
from __future__ import print_function

from . import plugin as p
from .update_ui import PiconHubUpdateChoice


def _open_update_choice(self):
    """Open the split updater menu: picon database or PiconHub plugin."""
    self.session.open(PiconHubUpdateChoice)


# The main green/OK UPDATE action must open the choice screen first.
p.PiconHubMain.quickUpdate = _open_update_choice
p.PiconHubUpdateMenu = PiconHubUpdateChoice
