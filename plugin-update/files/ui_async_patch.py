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


class PrettyUpdateMenu(Screen):
    def __init__(self, session):
        self.session = session
        self.selected = 0
        self.checking = False
        self.pending = None
        self._check_done = False
        self._check_result = None
        self._check_error = None
        try:
            self.w = getDesktop(0).size().width()
            self.h = getDesktop(0).size().height()
        except Exception:
            self.w, self.h = 1920, 1080
        self.hd = self.w <= 1280

        if self.hd:
            widgets = [
                '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
                '<eLabel position="0,600" size="1280,120" zPosition="2" backgroundColor="#062d40" />',
                '<widget name="section" position="72,153" size="900,42" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="subtitle" position="72,205" size="1100,32" zPosition="4" font="Regular;18" foregroundColor="#b9d7e8" transparent="1" />',
                '<widget name="row1" position="170,285" size="940,52" zPosition="4" font="Regular;29" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="desc1" position="215,340" size="860,42" zPosition="4" font="Regular;18" foregroundColor="#8fbad0" transparent="1" />',
                '<widget name="row2" position="170,415" size="940,52" zPosition="4" font="Regular;29" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="desc2" position="215,470" size="860,42" zPosition="4" font="Regular;18" foregroundColor="#8fbad0" transparent="1" />',
                '<widget name="status" position="170,535" size="940,42" zPosition="4" font="Regular;18" foregroundColor="#6fdcff" transparent="1" halign="center" />',
                '<widget name="help" position="120,635" size="1040,40" zPosition="4" font="Regular;18" foregroundColor="#dbefff" transparent="1" halign="center" />',
            ]
        else:
            widgets = [
                '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
                '<eLabel position="0,900" size="1920,180" zPosition="2" backgroundColor="#062d40" />',
                '<widget name="section" position="108,230" size="1350,60" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="subtitle" position="108,307" size="1650,46" zPosition="4" font="Regular;26" foregroundColor="#b9d7e8" transparent="1" />',
                '<widget name="row1" position="255,430" size="1410,76" zPosition="4" font="Regular;43" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="desc1" position="325,510" size="1290,56" zPosition="4" font="Regular;27" foregroundColor="#8fbad0" transparent="1" />',
                '<widget name="row2" position="255,625" size="1410,76" zPosition="4" font="Regular;43" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="desc2" position="325,705" size="1290,56" zPosition="4" font="Regular;27" foregroundColor="#8fbad0" transparent="1" />',
                '<widget name="status" position="255,805" size="1410,58" zPosition="4" font="Regular;27" foregroundColor="#6fdcff" transparent="1" halign="center" />',
                '<widget name="help" position="180,952" size="1560,60" zPosition="4" font="Regular;27" foregroundColor="#dbefff" transparent="1" halign="center" />',
            ]

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
        self['help'] = Label('OK / ZELENÁ = potvrdiť     HORE / DOLE = výber     ČERVENÁ = späť')
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
            self['bg'].instance.setPixmapFromFile(
                p.os.path.join(p.ASSET_PATH, 'missing_%s_base.jpg' % mode))
        except Exception:
            pass

    def _refresh_rows(self):
        self['row1'].setText(('>  ' if self.selected == 0 else '   ') + 'AKTUALIZOVAŤ PICONY')
        self['row2'].setText(('>  ' if self.selected == 1 else '   ') + 'AKTUALIZOVAŤ PLUGIN')

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
        self['status'].setText('Kontrolujem dostupnú verziu na GitHube...')
        self['help'].setText('Prebieha kontrola aktualizácie. Prosím čakaj.')

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
        self['help'].setText('OK / ZELENÁ = potvrdiť     HORE / DOLE = výber     ČERVENÁ = späť')

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
        text = (
            'Aktuálna verzia: %s\n'
            'Nová verzia: %s\n\n'
            '%s\n\n'
            'Po úspešnej aktualizácii sa Enigma2 GUI automaticky reštartuje.\n'
            'Pokračovať?'
        ) % (
            result.get('current_version'),
            result.get('remote_version'),
            result.get('notes') or '')
        self.session.openWithCallback(
            self.confirmed,
            MessageBox,
            text,
            MessageBox.TYPE_YESNO,
            default=True)

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


# Replace only the update chooser and the startup update check.
# Picon downloading, provider browsing and the update installer remain untouched.
um.UpdateMenu = PrettyUpdateMenu
p.PiconHubUpdateMenu = PrettyUpdateMenu
p.PiconHubMain._layoutReady = _async_layout_ready
