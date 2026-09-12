# -*- coding: utf-8 -*-
from __future__ import print_function

from Components.Label import Label
from . import plugin as p
from . import update_ui as ui


def _native_choice_widgets(hd):
    if hd:
        return [
            '<widget name="bg" position="0,0" size="1280,127" zPosition="0" alphatest="blend" />',
            '<widget name="body" position="20,127" size="1240,485" zPosition="0" backgroundColor="#022635" transparent="0" />',
            '<widget name="footer" position="20,612" size="1240,72" zPosition="0" backgroundColor="#021f2c" transparent="0" />',
            '<widget name="section" position="72,153" size="570,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
            '<widget name="summary" position="660,153" size="570,42" zPosition="4" font="Regular;19" foregroundColor="#ffffff" transparent="1" halign="right" />',
            '<widget name="list" position="72,212" size="790,145" zPosition="4" font="Regular;22" itemHeight="58" transparent="1" />',
            '<widget name="name" position="900,300" size="320,48" zPosition="5" font="Regular;25" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="state" position="900,365" size="320,38" zPosition="5" font="Regular;20" foregroundColor="#4ee878" transparent="1" halign="center" />',
            '<widget name="detail" position="880,430" size="360,115" zPosition="5" font="Regular;17" foregroundColor="#dbefff" transparent="1" halign="center" />',
            '<widget name="red_btn" position="37,624" size="263,53" zPosition="5" backgroundColor="#6b1018" foregroundColor="#ffffff" font="Regular;18" borderWidth="2" borderColor="#ff5968" transparent="0" halign="center" valign="center" />',
            '<widget name="green_btn" position="344,624" size="263,53" zPosition="5" backgroundColor="#0b5b23" foregroundColor="#ffffff" font="Regular;16" borderWidth="2" borderColor="#4ee878" transparent="0" halign="center" valign="center" />',
        ]
    return [
        '<widget name="bg" position="0,0" size="1920,190" zPosition="0" alphatest="blend" />',
        '<widget name="body" position="30,190" size="1860,728" zPosition="0" backgroundColor="#022635" transparent="0" />',
        '<widget name="footer" position="30,918" size="1860,108" zPosition="0" backgroundColor="#021f2c" transparent="0" />',
        '<widget name="section" position="108,230" size="840,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
        '<widget name="summary" position="1010,230" size="790,60" zPosition="4" font="Regular;27" foregroundColor="#ffffff" transparent="1" halign="right" />',
        '<widget name="list" position="108,325" size="1160,220" zPosition="4" font="Regular;30" itemHeight="82" transparent="1" />',
        '<widget name="name" position="1365,450" size="430,65" zPosition="5" font="Regular;34" foregroundColor="#ffffff" transparent="1" halign="center" />',
        '<widget name="state" position="1365,530" size="430,50" zPosition="5" font="Regular;26" foregroundColor="#4ee878" transparent="1" halign="center" />',
        '<widget name="detail" position="1335,610" size="490,165" zPosition="5" font="Regular;23" foregroundColor="#dbefff" transparent="1" halign="center" />',
        '<widget name="red_btn" position="55,936" size="395,79" zPosition="5" backgroundColor="#6b1018" foregroundColor="#ffffff" font="Regular;27" borderWidth="3" borderColor="#ff5968" transparent="0" halign="center" valign="center" />',
        '<widget name="green_btn" position="516,936" size="395,79" zPosition="5" backgroundColor="#0b5b23" foregroundColor="#ffffff" font="Regular;23" borderWidth="3" borderColor="#4ee878" transparent="0" halign="center" valign="center" />',
    ]


ui._choice_widgets = _native_choice_widgets
_original_choice_init = ui.PiconHubUpdateChoice.__init__


def _choice_init(self, session):
    _original_choice_init(self, session)
    self['body'] = Label('')
    self['footer'] = Label('')
    self['red_btn'] = Label('SPÄŤ')
    self['green_btn'] = Label('OK, SPUSTIŤ AKTUALIZÁCIU')
    self['actions'] = ui.ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions'], {
        'cancel': self.close, 'red': self.close,
        'ok': self.open_selected, 'green': self.open_selected,
        'up': self.up, 'down': self.down,
    }, -1)


ui.PiconHubUpdateChoice.__init__ = _choice_init


_original_dialog_widgets = ui._dialog_widgets
def _native_dialog_widgets(hd, status=False, error=False):
    widgets = _original_dialog_widgets(hd, status, error)
    widgets[0] = '<widget name="bg" position="0,0" size="%s" zPosition="0" alphatest="blend" />' % ('1280,127' if hd else '1920,190')
    if hd:
        widgets += [
            '<widget name="body" position="20,127" size="1240,485" zPosition="0" backgroundColor="#022635" transparent="0" />',
            '<widget name="footer" position="20,612" size="1240,72" zPosition="0" backgroundColor="#021f2c" transparent="0" />',
            '<widget name="red_btn" position="37,624" size="263,53" zPosition="5" backgroundColor="#6b1018" foregroundColor="#ffffff" font="Regular;18" borderWidth="2" borderColor="#ff5968" transparent="0" halign="center" valign="center" />',
            '<widget name="green_btn" position="344,624" size="263,53" zPosition="5" backgroundColor="#0b5b23" foregroundColor="#ffffff" font="Regular;16" borderWidth="2" borderColor="#4ee878" transparent="0" halign="center" valign="center" />',
        ]
    else:
        widgets += [
            '<widget name="body" position="30,190" size="1860,728" zPosition="0" backgroundColor="#022635" transparent="0" />',
            '<widget name="footer" position="30,918" size="1860,108" zPosition="0" backgroundColor="#021f2c" transparent="0" />',
            '<widget name="red_btn" position="55,936" size="395,79" zPosition="5" backgroundColor="#6b1018" foregroundColor="#ffffff" font="Regular;27" borderWidth="3" borderColor="#ff5968" transparent="0" halign="center" valign="center" />',
            '<widget name="green_btn" position="516,936" size="395,79" zPosition="5" backgroundColor="#0b5b23" foregroundColor="#ffffff" font="Regular;23" borderWidth="3" borderColor="#4ee878" transparent="0" halign="center" valign="center" />',
        ]
    return widgets

ui._dialog_widgets = _native_dialog_widgets

_original_confirm_init = ui.PiconHubPluginConfirm.__init__
def _confirm_init(self, session, result):
    _original_confirm_init(self, session, result)
    self['body'] = Label('')
    self['footer'] = Label('')
    self['red_btn'] = Label('SPÄŤ')
    self['green_btn'] = Label('OK, SPUSTIŤ AKTUALIZÁCIU')
ui.PiconHubPluginConfirm.__init__ = _confirm_init

_original_status_init = ui.PiconHubUpdateStatus.__init__
def _status_init(self, session, title, message, detail='', error=False):
    _original_status_init(self, session, title, message, detail, error)
    self['body'] = Label('')
    self['footer'] = Label('')
    self['red_btn'] = Label('SPÄŤ')
    self['green_btn'] = Label('OK')
    self['actions'] = ui.ActionMap(['OkCancelActions', 'ColorActions'], {
        'cancel': self.close, 'red': self.close,
        'ok': self.close, 'green': self.close,
    }, -1)
ui.PiconHubUpdateStatus.__init__ = _status_init

_original_progress_widgets = ui._progress_widgets
def _native_progress_widgets(hd):
    widgets = _original_progress_widgets(hd)
    widgets[0] = '<widget name="bg" position="0,0" size="%s" zPosition="0" alphatest="blend" />' % ('1280,127' if hd else '1920,190')
    if hd:
        widgets += [
            '<widget name="body" position="20,127" size="1240,485" zPosition="0" backgroundColor="#022635" transparent="0" />',
            '<widget name="footer" position="20,612" size="1240,72" zPosition="0" backgroundColor="#021f2c" transparent="0" />',
        ]
    else:
        widgets += [
            '<widget name="body" position="30,190" size="1860,728" zPosition="0" backgroundColor="#022635" transparent="0" />',
            '<widget name="footer" position="30,918" size="1860,108" zPosition="0" backgroundColor="#021f2c" transparent="0" />',
        ]
    return widgets
ui._progress_widgets = _native_progress_widgets

_original_progress_init = ui.PiconHubPluginProgress.__init__
def _progress_init(self, session, manifest):
    _original_progress_init(self, session, manifest)
    self['body'] = Label('')
    self['footer'] = Label('')
ui.PiconHubPluginProgress.__init__ = _progress_init


def _open_update_choice(self):
    self.session.open(ui.PiconHubUpdateChoice)


p.PiconHubMain.quickUpdate = _open_update_choice
p.PiconHubUpdateMenu = ui.PiconHubUpdateChoice
