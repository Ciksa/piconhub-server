# -*- coding: utf-8 -*-
from __future__ import print_function

from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.Screen import Screen
from enigma import getDesktop

from . import plugin as p
from . import plugin_updater as pu
from . import update_menu as um
from . import ui_async_patch as ua


def _desktop():
    try:
        return getDesktop(0).size().width(), getDesktop(0).size().height()
    except Exception:
        return 1920, 1080


class PluginUpdateStatus(Screen):
    def __init__(self, session, title, message, detail='', error=False):
        self.session = session
        self.w, self.h = _desktop()
        self.hd = self.w <= 1280
        self.error = bool(error)
        icon_color = '#ff5968' if self.error else '#4fe27a'

        if self.hd:
            widgets = [
                '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="72,153" size="900,42" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
                '<eLabel position="90,250" size="1100,270" zPosition="2" backgroundColor="#021d2b" borderWidth="1" borderColor="#2e9dce" />',
                '<widget name="icon" position="125,285" size="105,105" zPosition="4" font="Regular;68" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % icon_color,
                '<widget name="title" position="265,282" size="850,48" zPosition="4" font="Regular;29" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="message" position="265,350" size="850,52" zPosition="4" font="Regular;21" foregroundColor="#dbefff" transparent="1" />',
                '<widget name="detail" position="265,418" size="850,70" zPosition="4" font="Regular;16" foregroundColor="#9fc4d7" transparent="1" />',
                '<eLabel position="25,600" size="1230,90" zPosition="8" backgroundColor="#062d40" />',
                '<eLabel position="38,612" size="280,62" zPosition="9" backgroundColor="#481018" borderWidth="2" borderColor="#ff5968" />',
                '<widget name="back_icon" position="50,620" size="52,44" zPosition="10" font="Regular;31" foregroundColor="#ff5968" transparent="1" halign="center" valign="center" />',
                '<widget name="back_title" position="112,618" size="185,24" zPosition="10" font="Regular;18" foregroundColor="#ffffff" transparent="1" valign="center" />',
                '<widget name="back_sub" position="112,645" size="185,18" zPosition="10" font="Regular;11" foregroundColor="#d7e4ea" transparent="1" valign="center" />',
                '<widget name="help" position="665,620" size="535,44" zPosition="10" font="Regular;16" foregroundColor="#b9d7e8" transparent="1" halign="right" valign="center" />',
            ]
        else:
            widgets = [
                '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="108,230" size="1350,60" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
                '<eLabel position="135,365" size="1650,405" zPosition="2" backgroundColor="#021d2b" borderWidth="2" borderColor="#2e9dce" />',
                '<widget name="icon" position="190,415" size="155,155" zPosition="4" font="Regular;100" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % icon_color,
                '<widget name="title" position="400,412" size="1270,70" zPosition="4" font="Regular;43" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="message" position="400,515" size="1270,75" zPosition="4" font="Regular;31" foregroundColor="#dbefff" transparent="1" />',
                '<widget name="detail" position="400,620" size="1270,105" zPosition="4" font="Regular;24" foregroundColor="#9fc4d7" transparent="1" />',
                '<eLabel position="38,900" size="1844,135" zPosition="8" backgroundColor="#062d40" />',
                '<eLabel position="58,918" size="416,92" zPosition="9" backgroundColor="#481018" borderWidth="3" borderColor="#ff5968" />',
                '<widget name="back_icon" position="76,930" size="70,60" zPosition="10" font="Regular;42" foregroundColor="#ff5968" transparent="1" halign="center" valign="center" />',
                '<widget name="back_title" position="158,930" size="285,36" zPosition="10" font="Regular;27" foregroundColor="#ffffff" transparent="1" valign="center" />',
                '<widget name="back_sub" position="158,970" size="285,25" zPosition="10" font="Regular;16" foregroundColor="#d7e4ea" transparent="1" valign="center" />',
                '<widget name="help" position="1030,930" size="780,60" zPosition="10" font="Regular;24" foregroundColor="#b9d7e8" transparent="1" halign="right" valign="center" />',
            ]

        widgets.extend(p._system_header_widgets(self.hd))
        self.skin = '<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>' % (
            self.w, self.h, ''.join(widgets))

        Screen.__init__(self, session)
        self['bg'] = p.Pixmap()
        self['version'] = Label('')
        p._setup_system_header(self)
        self['section'] = Label('AKTUALIZÁCIA PICONHUBU')
        self['icon'] = Label('!' if self.error else '✓')
        self['title'] = Label(title)
        self['message'] = Label(message)
        self['detail'] = Label(detail)
        self['back_icon'] = Label('←')
        self['back_title'] = Label('SPÄŤ')
        self['back_sub'] = Label('Návrat do aktualizácie')
        self['help'] = Label('ČERVENÁ / OK = späť')
        self['actions'] = ActionMap(
            ['OkCancelActions', 'ColorActions'],
            {'ok': self.close, 'cancel': self.close, 'red': self.close, 'green': self.close}, -1)
        self.onLayoutFinish.append(self.ready)

    def ready(self):
        try:
            mode = 'hd' if self.hd else 'fhd'
            self['bg'].instance.setPixmapFromFile(
                p.os.path.join(p.ASSET_PATH, 'missing_%s_base.jpg' % mode))
        except Exception:
            pass


def _show_latest(screen, result=None):
    result = result or {}
    version = result.get('remote_version') or result.get('current_version') or pu.RELEASE_VERSION
    screen.session.open(
        PluginUpdateStatus,
        'POUŽÍVAŠ NAJNOVŠIU VERZIU',
        'PiconHub %s je aktuálny.' % version,
        'Nie je potrebná žiadna aktualizácia pluginu.',
        False)


def _show_error(screen, error):
    screen.session.open(
        PluginUpdateStatus,
        'KONTROLA AKTUALIZÁCIE ZLYHALA',
        'Nepodarilo sa overiť dostupnú verziu PiconHubu.',
        str(error or 'Neznáma chyba.'),
        True)


def _poll_check(self):
    if not self._check_done:
        self.poll_timer.start(100, True)
        return

    self.checking = False
    self['status'].setText('')
    self['help'].setText('HORE / DOLE = výber')

    if self._check_error:
        _show_error(self, self._check_error)
        return

    result = self._check_result or {}
    if not result.get('available'):
        _show_latest(self, result)
        return

    self.pending = result.get('manifest')
    self.session.openWithCallback(self.confirmed, ua.PluginUpdateConfirm, result)


def _styled_offer_update(screen, result, manual=False):
    result = result or {}
    if result.get('available'):
        def confirmed(answer):
            if answer and result.get('manifest'):
                screen.session.open(um.PluginProgress, result.get('manifest'))
        screen.session.openWithCallback(confirmed, ua.PluginUpdateConfirm, result)
        return
    if manual:
        _show_latest(screen, result)


def _styled_manual_update_check(screen):
    try:
        result = pu.PiconHubPluginUpdater().check()
    except Exception as e:
        _show_error(screen, e)
        return
    _styled_offer_update(screen, result, manual=True)


ua.PrettyUpdateMenu._poll_check = _poll_check
pu._offer_update = _styled_offer_update
pu._manual_update_check = _styled_manual_update_check
