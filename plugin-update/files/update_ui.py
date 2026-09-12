# -*- coding: utf-8 -*-
from __future__ import print_function

import hashlib
import os
import shutil
import time
from threading import Thread

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Screens.Screen import Screen
from enigma import eTimer, getDesktop, ePoint

from . import plugin as p
from . import plugin_updater as pu

BG = '#022635'
PANEL = '#032b3a'
PANEL_FOCUS = '#07506a'
CYAN = '#55d8ff'
CYAN_DIM = '#1c5368'
FOOTER = '#021f2c'
WHITE = '#ffffff'
TEXT = '#dbefff'
TEXT_DIM = '#9fc4d7'
GREEN = '#4ee878'
RED = '#ff5968'


def _desktop():
    try:
        return getDesktop(0).size().width(), getDesktop(0).size().height()
    except Exception:
        return 1920, 1080


def _base_widgets(hd, buttons=True):
    if hd:
        widgets = [
            '<widget name="bg" position="0,0" size="1280,127" zPosition="0" alphatest="blend" />',
            '<widget name="body" position="20,127" size="1240,485" zPosition="0" backgroundColor="%s" transparent="0" />' % BG,
            '<widget name="footer" position="20,612" size="1240,108" zPosition="0" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (FOOTER, CYAN_DIM),
        ]
        if buttons:
            widgets += [
                '<widget name="red_btn" position="38,620" size="278,56" zPosition="4" alphatest="blend" />',
                '<widget name="red_icon" position="50,626" size="42,42" zPosition="6" font="Regular;31" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % RED,
                '<widget name="red_title" position="102,628" size="194,21" zPosition="6" font="Regular;18" foregroundColor="%s" transparent="1" valign="center" />' % WHITE,
                '<widget name="red_sub" position="102,650" size="194,17" zPosition="6" font="Regular;11" foregroundColor="#d9d9d9" transparent="1" valign="center" />',
                '<widget name="green_btn" position="347,620" size="278,56" zPosition="4" alphatest="blend" />',
                '<widget name="green_icon" position="359,626" size="42,42" zPosition="6" font="Regular;14" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />',
                '<widget name="green_title" position="411,628" size="194,21" zPosition="6" font="Regular;15" foregroundColor="%s" transparent="1" valign="center" />' % WHITE,
                '<widget name="green_sub" position="411,650" size="194,17" zPosition="6" font="Regular;11" foregroundColor="#d9d9d9" transparent="1" valign="center" />',
            ]
        return widgets

    widgets = [
        '<widget name="bg" position="0,0" size="1920,190" zPosition="0" alphatest="blend" />',
        '<widget name="body" position="30,190" size="1860,728" zPosition="0" backgroundColor="%s" transparent="0" />' % BG,
        '<widget name="footer" position="30,918" size="1860,162" zPosition="0" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (FOOTER, CYAN_DIM),
    ]
    if buttons:
        widgets += [
            '<widget name="red_btn" position="58,930" size="416,84" zPosition="4" alphatest="blend" />',
            '<widget name="red_icon" position="76,941" size="62,58" zPosition="6" font="Regular;46" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % RED,
            '<widget name="red_title" position="156,942" size="286,31" zPosition="6" font="Regular;27" foregroundColor="%s" transparent="1" valign="center" />' % WHITE,
            '<widget name="red_sub" position="156,977" size="286,22" zPosition="6" font="Regular;16" foregroundColor="#d9d9d9" transparent="1" valign="center" />',
            '<widget name="green_btn" position="521,930" size="416,84" zPosition="4" alphatest="blend" />',
            '<widget name="green_icon" position="539,941" size="62,58" zPosition="6" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />',
            '<widget name="green_title" position="619,942" size="286,31" zPosition="6" font="Regular;22" foregroundColor="%s" transparent="1" valign="center" />' % WHITE,
            '<widget name="green_sub" position="619,977" size="286,22" zPosition="6" font="Regular;16" foregroundColor="#d9d9d9" transparent="1" valign="center" />',
        ]
    return widgets


def _common_header(hd):
    if hd:
        return [
            '<widget name="section" position="72,153" size="570,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
            '<widget name="summary" position="660,153" size="570,42" zPosition="4" font="Regular;19" foregroundColor="%s" transparent="1" halign="right" />' % WHITE,
        ]
    return [
        '<widget name="section" position="108,230" size="840,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
        '<widget name="summary" position="1010,230" size="790,60" zPosition="4" font="Regular;27" foregroundColor="%s" transparent="1" halign="right" />' % WHITE,
    ]


def _init_base(obj, session, name, widgets, buttons=True):
    all_widgets = _base_widgets(obj.hd, buttons) + _common_header(obj.hd) + list(widgets)
    all_widgets.extend(p._system_header_widgets(obj.hd))
    obj.skin = '<screen name="%s" position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="%s">%s</screen>' % (
        name, obj.gui_w, obj.gui_h, BG, ''.join(all_widgets))
    Screen.__init__(obj, session)
    obj['bg'] = Pixmap()
    obj['body'] = Label('')
    obj['footer'] = Label('')
    obj['version'] = Label('')
    p._setup_system_header(obj)
    if buttons:
        obj['red_btn'] = Pixmap()
        obj['red_icon'] = Label('←')
        obj['red_title'] = Label('')
        obj['red_sub'] = Label('')
        obj['green_btn'] = Pixmap()
        obj['green_icon'] = Label('OK')
        obj['green_title'] = Label('')
        obj['green_sub'] = Label('')


def _ready_base(obj):
    mode = 'hd' if obj.hd else 'fhd'
    try:
        obj['bg'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH, 'updater_header_%s.jpg' % mode))
    except Exception as e:
        print('[PiconHub] updater header error:', e)
    try:
        if 'red_btn' in obj:
            obj['red_btn'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH, 'picons_btn_red_%s.png' % mode))
            obj['green_btn'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH, 'picons_btn_green_%s.png' % mode))
    except Exception as e:
        print('[PiconHub] updater button error:', e)


def _set_buttons(obj, red_title='SPÄŤ', red_sub='Návrat späť', green_title='OK, SPUSTIŤ', green_sub='Potvrdiť vybranú aktualizáciu'):
    obj['red_title'].setText(red_title)
    obj['red_sub'].setText(red_sub)
    obj['green_title'].setText(green_title)
    obj['green_sub'].setText(green_sub)


def _choice_widgets(hd):
    if hd:
        return [
            '<widget name="card" position="62,214" size="790,156" zPosition="1" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (PANEL, CYAN_DIM),
            '<widget name="focus" position="70,222" size="774,68" zPosition="2" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (PANEL_FOCUS, CYAN),
            '<widget name="list" position="88,230" size="742,126" zPosition="4" font="Regular;22" itemHeight="62" transparent="1" selectionDisabled="1" />',
            '<widget name="divider" position="880,214" size="1,330" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
            '<widget name="name" position="900,275" size="320,45" zPosition="5" font="Regular;25" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
            '<widget name="state" position="900,335" size="320,38" zPosition="5" font="Regular;20" foregroundColor="%s" transparent="1" halign="center" />' % GREEN,
            '<widget name="detail" position="890,395" size="340,105" zPosition="5" font="Regular;17" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
        ]
    return [
        '<widget name="card" position="92,322" size="1185,234" zPosition="1" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (PANEL, CYAN_DIM),
        '<widget name="focus" position="104,334" size="1161,102" zPosition="2" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (PANEL_FOCUS, CYAN),
        '<widget name="list" position="132,346" size="1110,190" zPosition="4" font="Regular;30" itemHeight="92" transparent="1" selectionDisabled="1" />',
        '<widget name="divider" position="1320,322" size="2,495" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
        '<widget name="name" position="1365,410" size="430,65" zPosition="5" font="Regular;34" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
        '<widget name="state" position="1365,500" size="430,50" zPosition="5" font="Regular;26" foregroundColor="%s" transparent="1" halign="center" />' % GREEN,
        '<widget name="detail" position="1345,590" size="470,150" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
    ]


class PiconHubUpdateChoice(Screen):
    def __init__(self, session):
        self.session = session
        self.gui_w, self.gui_h = _desktop()
        self.hd = self.gui_w <= 1280
        self.checking = False
        self.pending = None
        self._check_done = False
        self._check_result = None
        self._check_error = None
        _init_base(self, session, 'PiconHubUpdateChoice', _choice_widgets(self.hd), True)
        self['section'] = Label('↻  AKTUALIZÁCIA')
        self['summary'] = Label('Vyber, čo chceš aktualizovať')
        self['card'] = Label('')
        self['focus'] = Label('')
        self['divider'] = Label('')
        self['list'] = MenuList(['AKTUALIZOVAŤ PICONY', 'AKTUALIZOVAŤ PLUGIN'])
        self['name'] = Label('')
        self['state'] = Label('')
        self['detail'] = Label('')
        _set_buttons(self, 'SPÄŤ', 'Návrat do hlavnej ponuky', 'OK, SPUSTIŤ', 'Potvrdiť vybranú aktualizáciu')
        self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions'], {
            'cancel': self.close, 'red': self.close,
            'ok': self.open_selected, 'green': self.open_selected,
            'up': self.up, 'down': self.down,
        }, -1)
        self.poll_timer = eTimer()
        self.poll_timer.callback.append(self._poll_check)
        self.onLayoutFinish.append(self._ready)

    def _ready(self):
        _ready_base(self)
        self._selected()

    def _index(self):
        try:
            return self['list'].getSelectedIndex()
        except Exception:
            return 0

    def _selected(self):
        idx = self._index()
        try:
            x = 70 if self.hd else 104
            y = (222 if idx == 0 else 284) if self.hd else (334 if idx == 0 else 426)
            self['focus'].instance.move(ePoint(x, y))
        except Exception:
            pass
        if idx == 0:
            self['name'].setText('PICONY')
            self['state'].setText('AKTUALIZÁCIA DATABÁZY')
            self['detail'].setText('Stiahne chýbajúce alebo zmenené\npicony podľa tvojich nastavení.')
        else:
            self['name'].setText('PLUGIN')
            self['state'].setText('AKTUALIZÁCIA PICONHUBU')
            self['detail'].setText('Skontroluje novú verziu PiconHubu\na bezpečne ju nainštaluje.')

    def up(self):
        if not self.checking:
            self['list'].up()
            self._selected()

    def down(self):
        if not self.checking:
            self['list'].down()
            self._selected()

    def open_picons(self):
        if not self.checking:
            self.session.open(p.PiconHubUpdateScreen)

    def open_plugin(self):
        if not self.checking:
            self._start_check()

    def open_selected(self):
        if self.checking:
            return
        if self._index() == 0:
            self.open_picons()
        else:
            self.open_plugin()

    def _start_check(self):
        self.checking = True
        self._check_done = False
        self._check_result = None
        self._check_error = None
        self['summary'].setText('Kontrolujem dostupnú verziu...')
        self['state'].setText('KONTROLA PREBIEHA')
        self['detail'].setText('Kontrola GitHub manifestu beží na pozadí.')

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
        self['summary'].setText('Vyber, čo chceš aktualizovať')
        self._selected()
        if self._check_error:
            self.session.open(PiconHubUpdateStatus, 'KONTROLA AKTUALIZÁCIE ZLYHALA', 'Nepodarilo sa overiť dostupnú verziu PiconHubu.', self._check_error, True)
            return
        result = self._check_result or {}
        if not result.get('available'):
            version = result.get('remote_version') or result.get('current_version') or pu.RELEASE_VERSION
            self.session.open(PiconHubUpdateStatus, 'POUŽÍVAŠ NAJNOVŠIU VERZIU', 'PiconHub %s je aktuálny.' % version, 'Nie je potrebná žiadna aktualizácia pluginu.', False)
            return
        self.pending = result.get('manifest')
        self.session.openWithCallback(self._confirmed, PiconHubPluginConfirm, result)

    def _confirmed(self, answer):
        if answer and self.pending:
            self.session.open(PiconHubPluginProgress, self.pending)


def _dialog_widgets(hd, status=False, error=False):
    icon_color = RED if error else GREEN
    if hd:
        widgets = ['<widget name="divider" position="880,214" size="1,330" zPosition="2" backgroundColor="#39bff8" transparent="0" />']
        if status:
            widgets += [
                '<widget name="icon" position="145,285" size="150,150" zPosition="5" font="Regular;96" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % icon_color,
                '<widget name="title" position="330,280" size="800,60" zPosition="5" font="Regular;31" foregroundColor="%s" transparent="1" />' % WHITE,
                '<widget name="message" position="330,360" size="800,55" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" />' % TEXT,
                '<widget name="detail" position="330,430" size="800,90" zPosition="5" font="Regular;18" foregroundColor="%s" transparent="1" />' % TEXT_DIM,
            ]
        else:
            widgets += [
                '<widget name="title" position="95,260" size="700,60" zPosition="5" font="Regular;31" foregroundColor="%s" transparent="1" />' % WHITE,
                '<widget name="versions" position="95,345" size="700,150" zPosition="5" font="Regular;22" foregroundColor="%s" transparent="1" />' % TEXT,
                '<widget name="notes_title" position="900,270" size="320,42" zPosition="5" font="Regular;24" foregroundColor="%s" transparent="1" halign="center" />' % CYAN,
                '<widget name="notes" position="890,330" size="340,210" zPosition="5" font="Regular;17" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
            ]
        return widgets
    widgets = ['<widget name="divider" position="1320,322" size="2,495" zPosition="2" backgroundColor="#39bff8" transparent="0" />']
    if status:
        widgets += [
            '<widget name="icon" position="220,430" size="220,220" zPosition="5" font="Regular;140" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % icon_color,
            '<widget name="title" position="500,425" size="1180,85" zPosition="5" font="Regular;45" foregroundColor="%s" transparent="1" />' % WHITE,
            '<widget name="message" position="500,545" size="1180,75" zPosition="5" font="Regular;33" foregroundColor="%s" transparent="1" />' % TEXT,
            '<widget name="detail" position="500,650" size="1180,135" zPosition="5" font="Regular;25" foregroundColor="%s" transparent="1" />' % TEXT_DIM,
        ]
    else:
        widgets += [
            '<widget name="title" position="145,390" size="1050,80" zPosition="5" font="Regular;44" foregroundColor="%s" transparent="1" />' % WHITE,
            '<widget name="versions" position="145,520" size="1050,200" zPosition="5" font="Regular;31" foregroundColor="%s" transparent="1" />' % TEXT,
            '<widget name="notes_title" position="1365,405" size="430,55" zPosition="5" font="Regular;34" foregroundColor="%s" transparent="1" halign="center" />' % CYAN,
            '<widget name="notes" position="1345,490" size="470,320" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
        ]
    return widgets


class PiconHubPluginConfirm(Screen):
    def __init__(self, session, result):
        self.session = session
        self.result = result or {}
        self.gui_w, self.gui_h = _desktop()
        self.hd = self.gui_w <= 1280
        _init_base(self, session, 'PiconHubPluginConfirm', _dialog_widgets(self.hd, False, False), True)
        self['section'] = Label('↻  AKTUALIZÁCIA PICONHUBU')
        self['summary'] = Label('Je dostupná nová verzia')
        self['divider'] = Label('')
        self['title'] = Label('SPUSTIŤ AKTUALIZÁCIU?')
        self['versions'] = Label('Aktuálna verzia: %s\nNová verzia: %s\n\nPo dokončení sa Enigma2 GUI automaticky reštartuje.' % (
            self.result.get('current_version') or '—', self.result.get('remote_version') or '—'))
        self['notes_title'] = Label('ČO JE NOVÉ')
        self['notes'] = Label(self.result.get('notes') or 'Bez poznámok k vydaniu.')
        _set_buttons(self, 'SPÄŤ', 'Zrušiť aktualizáciu', 'AKTUALIZOVAŤ', 'Nainštalovať novú verziu')
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {
            'cancel': self.reject, 'red': self.reject,
            'ok': self.accept, 'green': self.accept,
        }, -1)
        self.onLayoutFinish.append(self._ready)

    def _ready(self):
        _ready_base(self)

    def accept(self):
        self.close(True)

    def reject(self):
        self.close(False)


class PiconHubUpdateStatus(Screen):
    def __init__(self, session, title, message, detail='', error=False):
        self.session = session
        self.error = bool(error)
        self.gui_w, self.gui_h = _desktop()
        self.hd = self.gui_w <= 1280
        _init_base(self, session, 'PiconHubUpdateStatus', _dialog_widgets(self.hd, True, self.error), True)
        self['section'] = Label('↻  AKTUALIZÁCIA PICONHUBU')
        self['summary'] = Label('Stav aktualizácie')
        self['divider'] = Label('')
        self['icon'] = Label('!' if self.error else '✓')
        self['title'] = Label(title)
        self['message'] = Label(message)
        self['detail'] = Label(detail)
        _set_buttons(self, 'SPÄŤ', 'Návrat do aktualizácie', 'OK', 'Zavrieť obrazovku')
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {
            'cancel': self.close, 'red': self.close,
            'ok': self.close, 'green': self.close,
        }, -1)
        self.onLayoutFinish.append(self._ready)

    def _ready(self):
        _ready_base(self)


def _progress_widgets(hd):
    if hd:
        return [
            '<widget name="divider" position="880,214" size="1,330" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
            '<widget name="phase" position="95,285" size="700,60" zPosition="5" font="Regular;29" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
            '<widget name="info" position="95,380" size="700,140" zPosition="5" font="Regular;20" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
            '<widget name="progress_title" position="900,285" size="320,42" zPosition="5" font="Regular;24" foregroundColor="%s" transparent="1" halign="center" />' % CYAN,
            '<widget name="progress" position="900,355" size="320,28" zPosition="5" borderWidth="2" borderColor="%s" />' % CYAN,
            '<widget name="percent" position="900,405" size="320,55" zPosition="5" font="Regular;31" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
            '<widget name="detail" position="890,470" size="340,80" zPosition="5" font="Regular;16" foregroundColor="%s" transparent="1" halign="center" />' % TEXT_DIM,
        ]
    return [
        '<widget name="divider" position="1320,322" size="2,495" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
        '<widget name="phase" position="145,430" size="1050,90" zPosition="5" font="Regular;42" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
        '<widget name="info" position="145,570" size="1050,210" zPosition="5" font="Regular;29" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
        '<widget name="progress_title" position="1365,430" size="430,55" zPosition="5" font="Regular;34" foregroundColor="%s" transparent="1" halign="center" />' % CYAN,
        '<widget name="progress" position="1360,525" size="440,40" zPosition="5" borderWidth="2" borderColor="%s" />' % CYAN,
        '<widget name="percent" position="1360,595" size="440,80" zPosition="5" font="Regular;45" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
        '<widget name="detail" position="1345,705" size="470,110" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" halign="center" />' % TEXT_DIM,
    ]


class PiconHubPluginProgress(Screen):
    def __init__(self, session, manifest):
        self.session = session
        self.manifest = manifest or {}
        self.updater = pu.PiconHubPluginUpdater(timeout=8)
        self.stage = 'download'
        self.index = 0
        self.files = self.manifest.get('files') or []
        self.prepared = []
        self.changed = []
        self.backup = '/tmp/piconhub-plugin-backup-%d' % int(time.time())
        self.countdown = 3
        self.gui_w, self.gui_h = _desktop()
        self.hd = self.gui_w <= 1280
        _init_base(self, session, 'PiconHubPluginProgress', _progress_widgets(self.hd), False)
        self['section'] = Label('↻  AKTUALIZÁCIA PICONHUBU')
        self['summary'] = Label('Bezpečná inštalácia')
        self['divider'] = Label('')
        self['phase'] = Label('PRIPRAVUJEM AKTUALIZÁCIU')
        self['info'] = Label('Aktualizácia prebieha bezpečne.\nPo dokončení sa Enigma2 GUI automaticky reštartuje.')
        self['progress_title'] = Label('PRIEBEH')
        self['progress'] = ProgressBar()
        self['progress'].setRange((0, 100))
        self['progress'].setValue(0)
        self['percent'] = Label('0 %')
        self['detail'] = Label('Pripravujem súbory...')
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {
            'cancel': self.ignore, 'ok': self.ignore,
            'red': self.ignore, 'green': self.ignore,
            'yellow': self.ignore, 'blue': self.ignore,
        }, -1)
        self.timer = eTimer()
        self.timer.callback.append(self.step)
        self.onLayoutFinish.append(self.start)

    def ignore(self):
        return

    def start(self):
        _ready_base(self)
        try:
            os.makedirs(self.backup)
        except Exception:
            pass
        self.timer.start(100, True)

    def _progress(self, value):
        value = max(0, min(100, int(value)))
        self['progress'].setValue(value)
        self['percent'].setText('%d %%' % value)

    def _pct(self, done, total, base, span):
        return base + int((float(done) / max(1, total)) * span)

    def step(self):
        try:
            total = len(self.files)
            if self.stage == 'download':
                if self.index >= total:
                    self.stage = 'install'
                    self.index = 0
                    self.timer.start(80, True)
                    return
                item = self.files[self.index]
                rel = pu._safe_relative_path(item.get('path'))
                url = str(item.get('url') or '')
                digest = str(item.get('sha256') or '').lower()
                if not url.startswith(pu._ALLOWED_UPDATE_PREFIX) or len(digest) != 64:
                    raise pu.PiconHubPluginUpdateError('Neplatný update manifest pre %s.' % rel)
                self['phase'].setText('SŤAHUJEM A OVERUJEM')
                self['detail'].setText(rel)
                data = self.updater._fetch(url)
                if hashlib.sha256(data).hexdigest().lower() != digest:
                    raise pu.PiconHubPluginUpdateError('SHA-256 nesúhlasí pre %s.' % rel)
                self.prepared.append((rel, data))
                self.index += 1
                self._progress(self._pct(self.index, total, 0, 60))
                self.timer.start(60, True)
                return

            if self.stage == 'install':
                if self.index >= total:
                    self.finish()
                    return
                rel, data = self.prepared[self.index]
                target = os.path.join(self.updater.plugin_path, rel)
                parent = os.path.dirname(target)
                if not os.path.isdir(parent):
                    os.makedirs(parent)
                backup = os.path.join(self.backup, rel)
                if os.path.exists(target):
                    backup_dir = os.path.dirname(backup)
                    if not os.path.isdir(backup_dir):
                        os.makedirs(backup_dir)
                    shutil.copy2(target, backup)
                tmp = target + '.piconhub-update'
                handle = open(tmp, 'wb')
                handle.write(data)
                handle.flush()
                try:
                    os.fsync(handle.fileno())
                except Exception:
                    pass
                handle.close()
                try:
                    os.chmod(tmp, 0o644)
                except Exception:
                    pass
                os.rename(tmp, target)
                self.changed.append((target, backup if os.path.exists(backup) else None))
                self.index += 1
                self['phase'].setText('INŠTALUJEM')
                self['detail'].setText(rel)
                self._progress(self._pct(self.index, total, 60, 40))
                self.timer.start(60, True)
        except Exception as e:
            self.rollback(e)

    def rollback(self, error):
        for target, backup in reversed(self.changed):
            try:
                if backup:
                    shutil.copy2(backup, target)
                elif os.path.exists(target):
                    os.remove(target)
            except Exception:
                pass
        self['phase'].setText('AKTUALIZÁCIA ZLYHALA')
        self['summary'].setText('Zmeny boli vrátené späť')
        self['info'].setText('%s\nGUI sa nereštartuje.' % error)
        self['detail'].setText('Pôvodná verzia zostala zachovaná.')
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {
            'cancel': self.close, 'ok': self.close, 'red': self.close,
        }, -1)

    def finish(self):
        self._progress(100)
        self['phase'].setText('AKTUALIZÁCIA DOKONČENÁ')
        self['summary'].setText('Nová verzia je nainštalovaná')
        self['detail'].setText('Overenie a inštalácia prebehli úspešne.')
        self['info'].setText('Enigma2 GUI sa automaticky reštartuje za 3 sekundy.')
        try:
            self.timer.callback.remove(self.step)
        except Exception:
            pass
        self.timer.callback.append(self.tick)
        self.timer.start(1000, True)

    def tick(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self['info'].setText('Reštartujem Enigma2 GUI...')
            pu._restart_gui(self.session)
            return
        self['info'].setText('Enigma2 GUI sa automaticky reštartuje za %d sekundy.' % self.countdown)
        self.timer.start(1000, True)


def _show_latest(screen, result=None):
    result = result or {}
    version = result.get('remote_version') or result.get('current_version') or pu.RELEASE_VERSION
    screen.session.open(PiconHubUpdateStatus, 'POUŽÍVAŠ NAJNOVŠIU VERZIU', 'PiconHub %s je aktuálny.' % version, 'Nie je potrebná žiadna aktualizácia pluginu.', False)


def _show_error(screen, error):
    screen.session.open(PiconHubUpdateStatus, 'KONTROLA AKTUALIZÁCIE ZLYHALA', 'Nepodarilo sa overiť dostupnú verziu PiconHubu.', str(error or 'Neznáma chyba.'), True)


def _offer_update(screen, result, manual=False):
    result = result or {}
    if result.get('available'):
        def confirmed(answer):
            if answer and result.get('manifest'):
                screen.session.open(PiconHubPluginProgress, result.get('manifest'))
        screen.session.openWithCallback(confirmed, PiconHubPluginConfirm, result)
        return
    if manual:
        _show_latest(screen, result)


def _manual_update_check(screen):
    try:
        result = pu.PiconHubPluginUpdater().check()
    except Exception as e:
        _show_error(screen, e)
        return
    _offer_update(screen, result, manual=True)


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
            _offer_update(self, self._piconhub_auto_result or {}, manual=False)
        except Exception as e:
            print('[PiconHub] automatic plugin update offer error:', e)

    self._piconhub_auto_delay.callback.append(begin)
    self._piconhub_auto_poll.callback.append(poll)
    self._piconhub_auto_delay.start(1800, True)


p.PiconHubUpdateMenu = PiconHubUpdateChoice
pu._offer_update = _offer_update
pu._manual_update_check = _manual_update_check
p.PiconHubMain._layoutReady = _async_layout_ready
