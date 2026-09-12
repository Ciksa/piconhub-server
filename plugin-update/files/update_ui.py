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
from enigma import eTimer, getDesktop

from . import plugin as p
from . import plugin_updater as pu


def _desktop():
    try:
        return getDesktop(0).size().width(), getDesktop(0).size().height()
    except Exception:
        return 1920, 1080


def _init_base(obj, session, name, widgets):
    # 0.6.12.11: intentionally NO updater footer widgets.
    # The untouched footer area comes only from picons_*_base.jpg so we can
    # inspect the real native bottom panel before adding buttons next release.
    widgets.extend(p._system_header_widgets(obj.hd))
    obj.skin = '<screen name="%s" position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>' % (
        name, obj.gui_w, obj.gui_h, ''.join(widgets))
    Screen.__init__(obj, session)
    obj['bg'] = Pixmap()
    obj['version'] = Label('')
    p._setup_system_header(obj)


def _ready_base(obj):
    mode = 'hd' if obj.hd else 'fhd'
    try:
        obj['bg'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH, 'picons_%s_base.jpg' % mode))
    except Exception as e:
        print('[PiconHub] update UI background error:', e)


def _choice_widgets(hd):
    if hd:
        return [
            '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
            '<widget name="section" position="72,153" size="570,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
            '<widget name="summary" position="660,153" size="570,42" zPosition="4" font="Regular;19" foregroundColor="#ffffff" transparent="1" halign="right" />',
            '<widget name="list" position="72,212" size="790,390" zPosition="4" font="Regular;22" itemHeight="58" transparent="1" />',
            '<widget name="name" position="900,300" size="320,48" zPosition="5" font="Regular;25" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="state" position="900,365" size="320,38" zPosition="5" font="Regular;20" foregroundColor="#4ee878" transparent="1" halign="center" />',
            '<widget name="detail" position="880,430" size="360,115" zPosition="5" font="Regular;17" foregroundColor="#dbefff" transparent="1" halign="center" />',
        ]
    return [
        '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
        '<widget name="section" position="108,230" size="840,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
        '<widget name="summary" position="1010,230" size="790,60" zPosition="4" font="Regular;27" foregroundColor="#ffffff" transparent="1" halign="right" />',
        '<widget name="list" position="108,325" size="1160,565" zPosition="4" font="Regular;30" itemHeight="82" transparent="1" />',
        '<widget name="name" position="1365,450" size="430,65" zPosition="5" font="Regular;34" foregroundColor="#ffffff" transparent="1" halign="center" />',
        '<widget name="state" position="1365,530" size="430,50" zPosition="5" font="Regular;26" foregroundColor="#4ee878" transparent="1" halign="center" />',
        '<widget name="detail" position="1335,610" size="490,165" zPosition="5" font="Regular;23" foregroundColor="#dbefff" transparent="1" halign="center" />',
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
        _init_base(self, session, 'PiconHubUpdateChoice', _choice_widgets(self.hd))
        self['section'] = Label('↻  AKTUALIZÁCIA')
        self['summary'] = Label('Vyber, čo chceš aktualizovať')
        self['list'] = MenuList(['AKTUALIZOVAŤ PICONY', 'AKTUALIZOVAŤ PLUGIN'])
        self['name'] = Label('')
        self['state'] = Label('')
        self['detail'] = Label('')
        self['actions'] = ActionMap(['OkCancelActions','DirectionActions','ColorActions'], {
            'cancel': self.close, 'red': self.close,
            'ok': self.open_selected, 'green': self.open_selected,
            'yellow': self.open_picons, 'blue': self.open_plugin,
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
        if self._index() == 0:
            self['name'].setText('PICONY')
            self['state'].setText('AKTUALIZÁCIA DATABÁZY')
            self['detail'].setText('Stiahne chýbajúce alebo zmenené picony podľa tvojich nastavení.')
        else:
            self['name'].setText('PLUGIN')
            self['state'].setText('AKTUALIZÁCIA PICONHUBU')
            self['detail'].setText('Skontroluje novú verziu PiconHubu a bezpečne ju nainštaluje.')

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
            self.session.open(PiconHubUpdateStatus,
                'KONTROLA AKTUALIZÁCIE ZLYHALA',
                'Nepodarilo sa overiť dostupnú verziu PiconHubu.',
                self._check_error, True)
            return
        result = self._check_result or {}
        if not result.get('available'):
            version = result.get('remote_version') or result.get('current_version') or pu.RELEASE_VERSION
            self.session.open(PiconHubUpdateStatus,
                'POUŽÍVAŠ NAJNOVŠIU VERZIU',
                'PiconHub %s je aktuálny.' % version,
                'Nie je potrebná žiadna aktualizácia pluginu.', False)
            return
        self.pending = result.get('manifest')
        self.session.openWithCallback(self._confirmed, PiconHubPluginConfirm, result)

    def _confirmed(self, answer):
        if answer and self.pending:
            self.session.open(PiconHubPluginProgress, self.pending)


def _dialog_widgets(hd, status=False, error=False):
    icon_color = '#ff5968' if error else '#4ee878'
    if hd:
        w = [
            '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
            '<widget name="section" position="72,153" size="570,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
            '<widget name="summary" position="660,153" size="570,42" zPosition="4" font="Regular;19" foregroundColor="#ffffff" transparent="1" halign="right" />',
        ]
        if status:
            w += [
                '<widget name="icon" position="170,290" size="140,140" zPosition="5" font="Regular;90" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % icon_color,
                '<widget name="title" position="340,285" size="810,55" zPosition="5" font="Regular;31" foregroundColor="#ffffff" transparent="1" />',
                '<widget name="message" position="340,365" size="810,52" zPosition="5" font="Regular;23" foregroundColor="#dbefff" transparent="1" />',
                '<widget name="detail" position="340,435" size="810,90" zPosition="5" font="Regular;18" foregroundColor="#9fc4d7" transparent="1" />',
            ]
        else:
            w += [
                '<widget name="title" position="90,260" size="720,55" zPosition="5" font="Regular;30" foregroundColor="#ffffff" transparent="1" halign="center" />',
                '<widget name="versions" position="90,345" size="720,120" zPosition="5" font="Regular;22" foregroundColor="#dbefff" transparent="1" halign="center" />',
                '<widget name="notes_title" position="900,270" size="320,42" zPosition="5" font="Regular;24" foregroundColor="#6fdcff" transparent="1" halign="center" />',
                '<widget name="notes" position="880,330" size="360,220" zPosition="5" font="Regular;17" foregroundColor="#dbefff" transparent="1" halign="center" />',
            ]
        return w

    w = [
        '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
        '<widget name="section" position="108,230" size="840,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
        '<widget name="summary" position="1010,230" size="790,60" zPosition="4" font="Regular;27" foregroundColor="#ffffff" transparent="1" halign="right" />',
    ]
    if status:
        w += [
            '<widget name="icon" position="255,430" size="210,210" zPosition="5" font="Regular;135" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % icon_color,
            '<widget name="title" position="510,425" size="1210,80" zPosition="5" font="Regular;45" foregroundColor="#ffffff" transparent="1" />',
            '<widget name="message" position="510,545" size="1210,75" zPosition="5" font="Regular;33" foregroundColor="#dbefff" transparent="1" />',
            '<widget name="detail" position="510,650" size="1210,135" zPosition="5" font="Regular;25" foregroundColor="#9fc4d7" transparent="1" />',
        ]
    else:
        w += [
            '<widget name="title" position="135,390" size="1080,80" zPosition="5" font="Regular;44" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="versions" position="135,520" size="1080,180" zPosition="5" font="Regular;31" foregroundColor="#dbefff" transparent="1" halign="center" />',
            '<widget name="notes_title" position="1365,405" size="430,55" zPosition="5" font="Regular;34" foregroundColor="#6fdcff" transparent="1" halign="center" />',
            '<widget name="notes" position="1335,490" size="490,330" zPosition="5" font="Regular;23" foregroundColor="#dbefff" transparent="1" halign="center" />',
        ]
    return w


class PiconHubPluginConfirm(Screen):
    def __init__(self, session, result):
        self.session = session
        self.result = result or {}
        self.gui_w, self.gui_h = _desktop()
        self.hd = self.gui_w <= 1280
        _init_base(self, session, 'PiconHubPluginConfirm', _dialog_widgets(self.hd, False, False))
        self['section'] = Label('↻  AKTUALIZÁCIA PICONHUBU')
        self['summary'] = Label('Je dostupná nová verzia')
        self['title'] = Label('SPUSTIŤ AKTUALIZÁCIU?')
        self['versions'] = Label('Aktuálna verzia: %s\nNová verzia: %s\n\nPo dokončení sa Enigma2 GUI automaticky reštartuje.' % (
            self.result.get('current_version') or '—', self.result.get('remote_version') or '—'))
        self['notes_title'] = Label('ČO JE NOVÉ')
        self['notes'] = Label(self.result.get('notes') or 'Bez poznámok k vydaniu.')
        self['actions'] = ActionMap(['OkCancelActions','ColorActions'], {
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
        _init_base(self, session, 'PiconHubUpdateStatus', _dialog_widgets(self.hd, True, self.error))
        self['section'] = Label('↻  AKTUALIZÁCIA PICONHUBU')
        self['summary'] = Label('Stav aktualizácie')
        self['icon'] = Label('!' if self.error else '✓')
        self['title'] = Label(title)
        self['message'] = Label(message)
        self['detail'] = Label(detail)
        self['actions'] = ActionMap(['OkCancelActions','ColorActions'], {
            'cancel': self.close, 'red': self.close, 'ok': self.close,
        }, -1)
        self.onLayoutFinish.append(self._ready)

    def _ready(self):
        _ready_base(self)


def _progress_widgets(hd):
    if hd:
        return [
            '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
            '<widget name="section" position="72,153" size="570,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
            '<widget name="summary" position="660,153" size="570,42" zPosition="4" font="Regular;19" foregroundColor="#ffffff" transparent="1" halign="right" />',
            '<widget name="phase" position="90,300" size="720,60" zPosition="5" font="Regular;29" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="info" position="90,390" size="720,130" zPosition="5" font="Regular;20" foregroundColor="#dbefff" transparent="1" halign="center" />',
            '<widget name="progress_title" position="910,300" size="300,40" zPosition="5" font="Regular;24" foregroundColor="#6fdcff" transparent="1" halign="center" />',
            '<widget name="progress" position="900,365" size="320,28" zPosition="5" borderWidth="2" borderColor="#6fdcff" />',
            '<widget name="percent" position="900,410" size="320,55" zPosition="5" font="Regular;31" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="detail" position="880,480" size="360,75" zPosition="5" font="Regular;16" foregroundColor="#9fc4d7" transparent="1" halign="center" />',
        ]
    return [
        '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
        '<widget name="section" position="108,230" size="840,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
        '<widget name="summary" position="1010,230" size="790,60" zPosition="4" font="Regular;27" foregroundColor="#ffffff" transparent="1" halign="right" />',
        '<widget name="phase" position="135,450" size="1080,90" zPosition="5" font="Regular;42" foregroundColor="#ffffff" transparent="1" halign="center" />',
        '<widget name="info" position="135,585" size="1080,195" zPosition="5" font="Regular;29" foregroundColor="#dbefff" transparent="1" halign="center" />',
        '<widget name="progress_title" position="1365,450" size="430,55" zPosition="5" font="Regular;34" foregroundColor="#6fdcff" transparent="1" halign="center" />',
        '<widget name="progress" position="1360,545" size="440,40" zPosition="5" borderWidth="2" borderColor="#6fdcff" />',
        '<widget name="percent" position="1360,610" size="440,80" zPosition="5" font="Regular;45" foregroundColor="#ffffff" transparent="1" halign="center" />',
        '<widget name="detail" position="1335,720" size="490,110" zPosition="5" font="Regular;23" foregroundColor="#9fc4d7" transparent="1" halign="center" />',
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
        _init_base(self, session, 'PiconHubPluginProgress', _progress_widgets(self.hd))
        self['section'] = Label('↻  AKTUALIZÁCIA PICONHUBU')
        self['summary'] = Label('Bezpečná inštalácia')
        self['phase'] = Label('PRIPRAVUJEM AKTUALIZÁCIU')
        self['info'] = Label('Aktualizácia prebieha bezpečne.\nPo dokončení sa Enigma2 GUI automaticky reštartuje.')
        self['progress_title'] = Label('PRIEBEH')
        self['progress'] = ProgressBar()
        self['progress'].setRange((0, 100))
        self['progress'].setValue(0)
        self['percent'] = Label('0 %')
        self['detail'] = Label('Pripravujem súbory...')
        self['actions'] = ActionMap(['OkCancelActions','ColorActions'], {
            'cancel': self.ignore, 'ok': self.ignore, 'red': self.ignore,
            'green': self.ignore, 'yellow': self.ignore, 'blue': self.ignore,
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
        self['actions'] = ActionMap(['OkCancelActions','ColorActions'], {
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
    screen.session.open(PiconHubUpdateStatus,
        'POUŽÍVAŠ NAJNOVŠIU VERZIU',
        'PiconHub %s je aktuálny.' % version,
        'Nie je potrebná žiadna aktualizácia pluginu.', False)


def _show_error(screen, error):
    screen.session.open(PiconHubUpdateStatus,
        'KONTROLA AKTUALIZÁCIE ZLYHALA',
        'Nepodarilo sa overiť dostupnú verziu PiconHubu.',
        str(error or 'Neznáma chyba.'), True)


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
