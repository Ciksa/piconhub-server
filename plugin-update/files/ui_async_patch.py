# -*- coding: utf-8 -*-
from __future__ import print_function

from threading import Thread

from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import eTimer, getDesktop

from . import plugin as p
from . import plugin_updater as pu
from . import update_menu as um


def _desktop():
    try:
        return getDesktop(0).size().width(), getDesktop(0).size().height()
    except Exception:
        return 1920, 1080


def _bottom_widgets(hd, action_title='VYBRAŤ', action_sub='Spustiť označenú voľbu'):
    if hd:
        return [
            '<eLabel position="25,600" size="1230,90" zPosition="8" backgroundColor="#062d40" />',
            '<eLabel position="38,612" size="280,62" zPosition="9" backgroundColor="#481018" borderWidth="2" borderColor="#ff5968" />',
            '<eLabel position="330,612" size="280,62" zPosition="9" backgroundColor="#0a4926" borderWidth="2" borderColor="#4fe27a" />',
            '<widget name="back_icon" position="50,620" size="52,44" zPosition="10" font="Regular;31" foregroundColor="#ff5968" transparent="1" halign="center" valign="center" />',
            '<widget name="back_title" position="112,618" size="185,24" zPosition="10" font="Regular;18" foregroundColor="#ffffff" transparent="1" valign="center" />',
            '<widget name="back_sub" position="112,645" size="185,18" zPosition="10" font="Regular;11" foregroundColor="#d7e4ea" transparent="1" valign="center" />',
            '<widget name="action_icon" position="342,620" size="52,44" zPosition="10" font="Regular;31" foregroundColor="#4fe27a" transparent="1" halign="center" valign="center" />',
            '<widget name="action_title" position="404,618" size="185,24" zPosition="10" font="Regular;18" foregroundColor="#ffffff" transparent="1" valign="center" />',
            '<widget name="action_sub" position="404,645" size="185,18" zPosition="10" font="Regular;11" foregroundColor="#d7e4ea" transparent="1" valign="center" />',
            '<widget name="help" position="665,620" size="535,44" zPosition="10" font="Regular;16" foregroundColor="#b9d7e8" transparent="1" halign="right" valign="center" />',
        ]
    return [
        '<eLabel position="38,900" size="1844,135" zPosition="8" backgroundColor="#062d40" />',
        '<eLabel position="58,918" size="416,92" zPosition="9" backgroundColor="#481018" borderWidth="3" borderColor="#ff5968" />',
        '<eLabel position="492,918" size="416,92" zPosition="9" backgroundColor="#0a4926" borderWidth="3" borderColor="#4fe27a" />',
        '<widget name="back_icon" position="76,930" size="70,60" zPosition="10" font="Regular;42" foregroundColor="#ff5968" transparent="1" halign="center" valign="center" />',
        '<widget name="back_title" position="158,930" size="285,36" zPosition="10" font="Regular;27" foregroundColor="#ffffff" transparent="1" valign="center" />',
        '<widget name="back_sub" position="158,970" size="285,25" zPosition="10" font="Regular;16" foregroundColor="#d7e4ea" transparent="1" valign="center" />',
        '<widget name="action_icon" position="510,930" size="70,60" zPosition="10" font="Regular;42" foregroundColor="#4fe27a" transparent="1" halign="center" valign="center" />',
        '<widget name="action_title" position="592,930" size="285,36" zPosition="10" font="Regular;27" foregroundColor="#ffffff" transparent="1" valign="center" />',
        '<widget name="action_sub" position="592,970" size="285,25" zPosition="10" font="Regular;16" foregroundColor="#d7e4ea" transparent="1" valign="center" />',
        '<widget name="help" position="1030,930" size="780,60" zPosition="10" font="Regular;24" foregroundColor="#b9d7e8" transparent="1" halign="right" valign="center" />',
    ]


def _bind_bottom(screen, action_title, action_sub, help_text):
    screen['back_icon'] = Label('←')
    screen['back_title'] = Label('SPÄŤ')
    screen['back_sub'] = Label('Návrat do hlavnej ponuky')
    screen['action_icon'] = Label('✓')
    screen['action_title'] = Label(action_title)
    screen['action_sub'] = Label(action_sub)
    screen['help'] = Label(help_text)


class PluginUpdateConfirm(Screen):
    def __init__(self, session, result):
        self.session = session
        self.result = result or {}
        self.w, self.h = _desktop()
        self.hd = self.w <= 1280

        if self.hd:
            widgets = [
                '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="72,153" size="900,42" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
                '<eLabel position="65,228" size="650,330" zPosition="2" backgroundColor="#021d2b" borderWidth="1" borderColor="#2e9dce" />',
                '<eLabel position="735,228" size="480,330" zPosition="2" backgroundColor="#021d2b" borderWidth="1" borderColor="#2e9dce" />',
                '<widget name="question" position="95,258" size="590,52" zPosition="4" font="Regular;28" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="current" position="95,335" size="590,34" zPosition="4" font="Regular;20" foregroundColor="#c9e4f1" transparent="1" />',
                '<widget name="remote" position="95,380" size="590,34" zPosition="4" font="Regular;20" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="restart" position="95,455" size="590,64" zPosition="4" font="Regular;16" foregroundColor="#9fc4d7" transparent="1" />',
                '<widget name="notes_title" position="765,252" size="420,36" zPosition="4" font="Regular;21" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="notes" position="765,300" size="420,225" zPosition="4" font="Regular;16" foregroundColor="#dbefff" transparent="1" />',
            ]
        else:
            widgets = [
                '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="108,230" size="1350,60" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
                '<eLabel position="98,340" size="970,490" zPosition="2" backgroundColor="#021d2b" borderWidth="2" borderColor="#2e9dce" />',
                '<eLabel position="1100,340" size="720,490" zPosition="2" backgroundColor="#021d2b" borderWidth="2" borderColor="#2e9dce" />',
                '<widget name="question" position="145,385" size="875,72" zPosition="4" font="Regular;41" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="current" position="145,510" size="875,48" zPosition="4" font="Regular;30" foregroundColor="#c9e4f1" transparent="1" />',
                '<widget name="remote" position="145,575" size="875,48" zPosition="4" font="Regular;30" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="restart" position="145,690" size="875,92" zPosition="4" font="Regular;24" foregroundColor="#9fc4d7" transparent="1" />',
                '<widget name="notes_title" position="1145,380" size="630,52" zPosition="4" font="Regular;31" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="notes" position="1145,455" size="630,320" zPosition="4" font="Regular;23" foregroundColor="#dbefff" transparent="1" />',
            ]

        widgets.extend(_bottom_widgets(self.hd, 'AKTUALIZOVAŤ', 'Nainštalovať novú verziu'))
        widgets.extend(p._system_header_widgets(self.hd))
        self.skin = '<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>' % (
            self.w, self.h, ''.join(widgets))

        Screen.__init__(self, session)
        self['bg'] = p.Pixmap()
        self['version'] = Label('')
        p._setup_system_header(self)
        self['section'] = Label('AKTUALIZÁCIA PICONHUBU')
        self['question'] = Label('JE DOSTUPNÁ NOVÁ VERZIA')
        self['current'] = Label('Aktuálna verzia:  %s' % (self.result.get('current_version') or '—'))
        self['remote'] = Label('Nová verzia:      %s' % (self.result.get('remote_version') or '—'))
        self['restart'] = Label('Po úspešnej aktualizácii sa Enigma2 GUI automaticky reštartuje.')
        self['notes_title'] = Label('ČO JE NOVÉ')
        self['notes'] = Label(self.result.get('notes') or 'Bez poznámok k vydaniu.')
        _bind_bottom(self, 'AKTUALIZOVAŤ', 'Nainštalovať novú verziu', 'ČERVENÁ = späť    ZELENÁ / OK = pokračovať')
        self['actions'] = ActionMap(
            ['OkCancelActions', 'ColorActions'],
            {'ok': self.accept, 'green': self.accept, 'cancel': self.reject, 'red': self.reject}, -1)
        self.onLayoutFinish.append(self.ready)

    def ready(self):
        try:
            mode = 'hd' if self.hd else 'fhd'
            self['bg'].instance.setPixmapFromFile(p.os.path.join(p.ASSET_PATH, 'missing_%s_base.jpg' % mode))
        except Exception:
            pass

    def accept(self):
        self.close(True)

    def reject(self):
        self.close(False)


class PrettyUpdateMenu(Screen):
    def __init__(self, session):
        self.session = session
        self.selected = 0
        self.checking = False
        self.pending = None
        self._check_done = False
        self._check_result = None
        self._check_error = None
        self.w, self.h = _desktop()
        self.hd = self.w <= 1280

        if self.hd:
            widgets = [
                '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="72,153" size="900,42" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="subtitle" position="72,205" size="1100,32" zPosition="4" font="Regular;18" foregroundColor="#b9d7e8" transparent="1" />',
                '<widget name="row1" position="170,285" size="940,52" zPosition="4" font="Regular;29" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="desc1" position="215,340" size="860,42" zPosition="4" font="Regular;18" foregroundColor="#8fbad0" transparent="1" />',
                '<widget name="row2" position="170,415" size="940,52" zPosition="4" font="Regular;29" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="desc2" position="215,470" size="860,42" zPosition="4" font="Regular;18" foregroundColor="#8fbad0" transparent="1" />',
                '<widget name="status" position="170,535" size="940,42" zPosition="4" font="Regular;18" foregroundColor="#6fdcff" transparent="1" halign="center" />',
            ]
        else:
            widgets = [
                '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="108,230" size="1350,60" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="subtitle" position="108,307" size="1650,46" zPosition="4" font="Regular;26" foregroundColor="#b9d7e8" transparent="1" />',
                '<widget name="row1" position="255,430" size="1410,76" zPosition="4" font="Regular;43" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="desc1" position="325,510" size="1290,56" zPosition="4" font="Regular;27" foregroundColor="#8fbad0" transparent="1" />',
                '<widget name="row2" position="255,625" size="1410,76" zPosition="4" font="Regular;43" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="desc2" position="325,705" size="1290,56" zPosition="4" font="Regular;27" foregroundColor="#8fbad0" transparent="1" />',
                '<widget name="status" position="255,805" size="1410,58" zPosition="4" font="Regular;27" foregroundColor="#6fdcff" transparent="1" halign="center" />',
            ]

        widgets.extend(_bottom_widgets(self.hd))
        widgets.extend(p._system_header_widgets(self.hd))
        self.skin = '<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>' % (
            self.w, self.h, ''.join(widgets))

        Screen.__init__(self, session)
        self['bg'] = p.Pixmap()
        self['version'] = Label('')
        p._setup_system_header(self)
        self['section'] = Label('AKTUALIZÁCIA')
        self['subtitle'] = Label('Vyber, čo chceš aktualizovať.')
        self['row1'] = Label('')
        self['desc1'] = Label('Stiahne chýbajúce alebo zmenené picony podľa tvojich nastavení.')
        self['row2'] = Label('')
        self['desc2'] = Label('Skontroluje novú verziu PiconHubu a bezpečne ju nainštaluje.')
        self['status'] = Label('')
        _bind_bottom(self, 'VYBRAŤ', 'Spustiť označenú voľbu', 'HORE / DOLE = výber')
        self['actions'] = ActionMap(
            ['OkCancelActions', 'DirectionActions', 'ColorActions'],
            {
                'ok': self.open_selected,
                'green': self.open_selected,
                'cancel': self.go_back,
                'red': self.go_back,
                'up': self.up,
                'down': self.down,
            }, -1)
        self.poll_timer = eTimer()
        self.poll_timer.callback.append(self._poll_check)
        self.onLayoutFinish.append(self.ready)
        self._refresh_rows()

    def ready(self):
        try:
            mode = 'hd' if self.hd else 'fhd'
            self['bg'].instance.setPixmapFromFile(p.os.path.join(p.ASSET_PATH, 'missing_%s_base.jpg' % mode))
        except Exception:
            pass

    def _refresh_rows(self):
        self['row1'].setText(('>  ' if self.selected == 0 else '    ') + 'AKTUALIZOVAŤ PICONY')
        self['row2'].setText(('>  ' if self.selected == 1 else '    ') + 'AKTUALIZOVAŤ PLUGIN')

    def up(self):
        if self.checking:
            return
        self.selected = 0
        self._refresh_rows()

    def down(self):
        if self.checking:
            return
        self.selected = 1
        self._refresh_rows()

    def go_back(self):
        if not self.checking:
            self.close()

    def open_selected(self):
        if self.checking:
            return
        if self.selected == 0:
            self.session.open(p.PiconHubUpdateScreen)
            return
        self._start_plugin_check()

    def _start_plugin_check(self):
        self.checking = True
        self._check_done = False
        self._check_result = None
        self._check_error = None
        self['status'].setText('Kontrolujem dostupnú verziu...')
        self['help'].setText('Kontrola prebieha na pozadí')

        def worker():
            try:
                self._check_result = pu.PiconHubPluginUpdater(timeout=6).check()
            except Exception as e:
                self._check_error = str(e)
            self._check_done = True

        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()
        self.poll_timer.start(100, True)

    def _poll_check(self):
        if not self._check_done:
            self.poll_timer.start(100, True)
            return

        self.checking = False
        self['status'].setText('')
        self['help'].setText('HORE / DOLE = výber')

        if self._check_error:
            self.session.open(
                MessageBox,
                'Kontrola aktualizácie zlyhala:\n\n%s' % self._check_error,
                MessageBox.TYPE_ERROR,
                timeout=12)
            return

        result = self._check_result or {}
        if not result.get('available'):
            self.session.open(
                MessageBox,
                'PiconHub %s\n\nPoužívaš najnovšiu dostupnú verziu.' % pu.RELEASE_VERSION,
                MessageBox.TYPE_INFO,
                timeout=9)
            return

        self.pending = result.get('manifest')
        self.session.openWithCallback(self.confirmed, PluginUpdateConfirm, result)

    def confirmed(self, answer):
        if answer and self.pending:
            self.session.open(um.PluginProgress, self.pending)


def _async_layout_ready(self):
    pu._original_layout_ready(self)
    if pu._AUTO_CHECK_DONE:
        return
    pu._AUTO_CHECK_DONE = True

    self._piconhub_auto_result = None
    self._piconhub_auto_error = None
    self._piconhub_auto_done = False
    self._piconhub_auto_delay = eTimer()
    self._piconhub_auto_poll = eTimer()

    def worker():
        try:
            self._piconhub_auto_result = pu.PiconHubPluginUpdater(timeout=4).check()
        except Exception as e:
            self._piconhub_auto_error = str(e)
        self._piconhub_auto_done = True

    def begin():
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()
        self._piconhub_auto_poll.start(100, True)

    def poll():
        if not self._piconhub_auto_done:
            self._piconhub_auto_poll.start(100, True)
            return
        if self._piconhub_auto_error:
            print('[PiconHub] automatic plugin update check error:', self._piconhub_auto_error)
            return
        try:
            pu._offer_update(self, self._piconhub_auto_result or {}, manual=False)
        except Exception as e:
            print('[PiconHub] automatic plugin update offer error:', e)

    self._piconhub_auto_delay.callback.append(begin)
    self._piconhub_auto_poll.callback.append(poll)
    self._piconhub_auto_delay.start(1800, True)


um.UpdateMenu = PrettyUpdateMenu
p.PiconHubUpdateMenu = PrettyUpdateMenu
p.PiconHubMain._layoutReady = _async_layout_ready
