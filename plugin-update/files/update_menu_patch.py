# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap

from . import plugin as p
from . import update_ui as ui
from .update_ui import PiconHubUpdateChoice


def _open_update_choice(self):
    """Open the split updater menu: picon database or PiconHub plugin."""
    self.session.open(PiconHubUpdateChoice)


# ---------------------------------------------------------------------------
# Two-button footer for updater screens.
# The legacy picons_*_base.jpg contains four baked buttons. Cover the whole
# footer and redraw only RED + GREEN so unused YELLOW/BLUE keys disappear.
# ---------------------------------------------------------------------------

def _footer_widgets(hd, with_buttons=True):
    if hd:
        widgets = [
            '<widget name="footer_cover" position="20,612" size="1240,72" zPosition="20" alphatest="blend" />',
        ]
        if with_buttons:
            widgets += [
                '<widget name="footer_red" position="37,624" size="263,53" zPosition="21" alphatest="blend" />',
                '<widget name="footer_green" position="344,624" size="263,53" zPosition="21" alphatest="blend" />',
                '<widget name="footer_red_title" position="93,629" size="190,20" zPosition="22" font="Regular;15" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />',
                '<widget name="footer_red_sub" position="93,648" size="190,17" zPosition="22" font="Regular;10" foregroundColor="#dbefff" transparent="1" halign="center" valign="center" />',
                '<widget name="footer_green_title" position="400,629" size="190,20" zPosition="22" font="Regular;15" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />',
                '<widget name="footer_green_sub" position="400,648" size="190,17" zPosition="22" font="Regular;10" foregroundColor="#dbefff" transparent="1" halign="center" valign="center" />',
            ]
        return widgets

    widgets = [
        '<widget name="footer_cover" position="30,918" size="1860,108" zPosition="20" alphatest="blend" />',
    ]
    if with_buttons:
        widgets += [
            '<widget name="footer_red" position="55,936" size="395,79" zPosition="21" alphatest="blend" />',
            '<widget name="footer_green" position="516,936" size="395,79" zPosition="21" alphatest="blend" />',
            '<widget name="footer_red_title" position="140,944" size="285,30" zPosition="22" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />',
            '<widget name="footer_red_sub" position="140,973" size="285,25" zPosition="22" font="Regular;15" foregroundColor="#dbefff" transparent="1" halign="center" valign="center" />',
            '<widget name="footer_green_title" position="601,944" size="285,30" zPosition="22" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />',
            '<widget name="footer_green_sub" position="601,973" size="285,25" zPosition="22" font="Regular;15" foregroundColor="#dbefff" transparent="1" halign="center" valign="center" />',
        ]
    return widgets


_orig_choice_widgets = ui._choice_widgets
_orig_dialog_widgets = ui._dialog_widgets
_orig_progress_widgets = ui._progress_widgets


def _choice_widgets_two(hd):
    return _orig_choice_widgets(hd) + _footer_widgets(hd, True)


def _dialog_widgets_two(hd, status=False, error=False):
    return _orig_dialog_widgets(hd, status, error) + _footer_widgets(hd, True)


def _progress_widgets_clean(hd):
    return _orig_progress_widgets(hd) + _footer_widgets(hd, False)


ui._choice_widgets = _choice_widgets_two
ui._dialog_widgets = _dialog_widgets_two
ui._progress_widgets = _progress_widgets_clean


def _install_footer(screen, red_title, red_sub, green_title, green_sub, buttons=True):
    screen['footer_cover'] = Pixmap()
    if buttons:
        screen['footer_red'] = Pixmap()
        screen['footer_green'] = Pixmap()
        screen['footer_red_title'] = Label(red_title)
        screen['footer_red_sub'] = Label(red_sub)
        screen['footer_green_title'] = Label(green_title)
        screen['footer_green_sub'] = Label(green_sub)

    def ready():
        mode = 'hd' if screen.hd else 'fhd'
        try:
            screen['footer_cover'].instance.setPixmapFromFile(
                os.path.join(p.ASSET_PATH, 'news_footer_cover_%s.png' % mode))
            screen['footer_cover'].show()
            if buttons:
                screen['footer_red'].instance.setPixmapFromFile(
                    os.path.join(p.ASSET_PATH, 'picons_btn_red_%s.png' % mode))
                screen['footer_green'].instance.setPixmapFromFile(
                    os.path.join(p.ASSET_PATH, 'picons_btn_green_%s.png' % mode))
                screen['footer_red'].show()
                screen['footer_green'].show()
        except Exception as e:
            print('[PiconHub] updater footer load error:', e)

    screen.onLayoutFinish.append(ready)


_orig_choice_init = ui.PiconHubUpdateChoice.__init__
_orig_confirm_init = ui.PiconHubPluginConfirm.__init__
_orig_status_init = ui.PiconHubUpdateStatus.__init__
_orig_progress_init = ui.PiconHubPluginProgress.__init__


def _choice_init(self, session):
    _orig_choice_init(self, session)
    _install_footer(self, 'SPÄŤ', 'Návrat do hlavnej ponuky', 'OK / VYBRAŤ', 'Otvoriť vybranú aktualizáciu')
    self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions'], {
        'cancel': self.close, 'red': self.close,
        'ok': self.open_selected, 'green': self.open_selected,
        'up': self.up, 'down': self.down,
    }, -1)


def _confirm_init(self, session, result):
    _orig_confirm_init(self, session, result)
    _install_footer(self, 'SPÄŤ', 'Zrušiť aktualizáciu', 'AKTUALIZOVAŤ', 'Nainštalovať novú verziu')


def _status_init(self, session, title, message, detail='', error=False):
    _orig_status_init(self, session, title, message, detail, error)
    _install_footer(self, 'SPÄŤ', 'Návrat na výber', 'OK', 'Zavrieť stav aktualizácie')
    self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {
        'cancel': self.close, 'red': self.close,
        'ok': self.close, 'green': self.close,
    }, -1)


def _progress_init(self, session, manifest):
    _orig_progress_init(self, session, manifest)
    _install_footer(self, '', '', '', '', False)


ui.PiconHubUpdateChoice.__init__ = _choice_init
ui.PiconHubPluginConfirm.__init__ = _confirm_init
ui.PiconHubUpdateStatus.__init__ = _status_init
ui.PiconHubPluginProgress.__init__ = _progress_init

# Main green/OK UPDATE action opens the split updater menu first.
p.PiconHubMain.quickUpdate = _open_update_choice
p.PiconHubUpdateMenu = ui.PiconHubUpdateChoice
