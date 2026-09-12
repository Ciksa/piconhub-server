# -*- coding: utf-8 -*-
from __future__ import print_function

import hashlib
import os
import shutil
import time

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ProgressBar import ProgressBar
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import eTimer, getDesktop

from . import plugin as p
from .plugin_updater import (
    PiconHubPluginUpdater,
    PiconHubPluginUpdateError,
    RELEASE_VERSION,
    _safe_relative_path,
    _ALLOWED_UPDATE_PREFIX,
    _restart_gui,
)


class UpdateMenu(Screen):
    def __init__(self, session):
        self.session = session
        try:
            self.w = getDesktop(0).size().width()
            self.h = getDesktop(0).size().height()
        except Exception:
            self.w, self.h = 1920, 1080
        self.hd = self.w <= 1280
        if self.hd:
            widgets = [
                '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="72,153" size="700,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="list" position="170,270" size="940,180" zPosition="4" font="Regular;27" itemHeight="65" transparent="1" />',
            ]
        else:
            widgets = [
                '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="108,230" size="1000,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="list" position="260,405" size="1400,270" zPosition="4" font="Regular;40" itemHeight="95" transparent="1" />',
            ]
        widgets.extend(p._system_header_widgets(self.hd))
        self.skin = '<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>' % (
            self.w, self.h, ''.join(widgets))
        Screen.__init__(self, session)
        self['bg'] = p.Pixmap()
        self['version'] = Label('')
        p._setup_system_header(self)
        self['section'] = Label('↻  AKTUALIZOVAŤ')
        self['list'] = MenuList(['AKTUALIZOVAŤ PICONY', 'AKTUALIZOVAŤ PLUGIN'])
        self['actions'] = ActionMap(
            ['OkCancelActions', 'DirectionActions', 'ColorActions'],
            {
                'ok': self.open,
                'green': self.open,
                'cancel': self.close,
                'red': self.close,
                'up': self['list'].up,
                'down': self['list'].down,
            }, -1)
        self.onLayoutFinish.append(self.ready)

    def ready(self):
        try:
            self['bg'].instance.setPixmapFromFile(
                os.path.join(p.ASSET_PATH, 'missing_%s_base.jpg' % ('hd' if self.hd else 'fhd')))
        except Exception:
            pass

    def open(self):
        try:
            idx = self['list'].getSelectedIndex()
        except Exception:
            idx = 0
        if idx == 0:
            self.session.open(p.PiconHubUpdateScreen)
            return
        try:
            result = PiconHubPluginUpdater(timeout=6).check()
        except Exception as e:
            self.session.open(
                MessageBox,
                'Kontrola aktualizácie zlyhala:\n\n%s' % e,
                MessageBox.TYPE_ERROR,
                timeout=12)
            return
        if not result.get('available'):
            self.session.open(
                MessageBox,
                'PiconHub %s\n\nPoužívaš najnovšiu dostupnú verziu.' % RELEASE_VERSION,
                MessageBox.TYPE_INFO,
                timeout=9)
            return
        self.pending = result.get('manifest')
        text = (
            'Aktuálna verzia: %s\nNová verzia: %s\n\n%s\n\n'
            'Po aktualizácii sa Enigma2 GUI automaticky reštartuje.\nPokračovať?'
        ) % (result.get('current_version'), result.get('remote_version'), result.get('notes') or '')
        self.session.openWithCallback(
            self.confirmed, MessageBox, text, MessageBox.TYPE_YESNO, default=True)

    def confirmed(self, answer):
        if answer and getattr(self, 'pending', None):
            self.session.open(PluginProgress, self.pending)


class PluginProgress(Screen):
    def __init__(self, session, manifest):
        self.session = session
        self.manifest = manifest
        self.up = PiconHubPluginUpdater(timeout=8)
        self.stage = 'download'
        self.index = 0
        self.prepared = []
        self.changed = []
        self.backup = '/tmp/piconhub-plugin-backup-%d' % int(time.time())
        self.countdown = 3
        try:
            self.w = getDesktop(0).size().width()
            self.h = getDesktop(0).size().height()
        except Exception:
            self.w, self.h = 1920, 1080
        self.hd = self.w <= 1280

        if self.hd:
            widgets = [
                '<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="72,153" size="800,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
                '<eLabel position="65,228" size="660,330" zPosition="2" backgroundColor="#021d2b" borderWidth="1" borderColor="#2e9dce" />',
                '<eLabel position="745,228" size="470,330" zPosition="2" backgroundColor="#021d2b" borderWidth="1" borderColor="#2e9dce" />',
                '<widget name="phase" position="95,300" size="600,62" zPosition="4" font="Regular;27" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />',
                '<widget name="info" position="95,385" size="600,115" zPosition="4" font="Regular;18" foregroundColor="#b9d7e8" transparent="1" halign="center" valign="center" />',
                '<widget name="progress_title" position="775,270" size="410,36" zPosition="4" font="Regular;22" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="progress" position="790,350" size="365,30" zPosition="4" borderWidth="2" borderColor="#6fdcff" />',
                '<widget name="percent" position="790,392" size="365,44" zPosition="4" font="Regular;28" foregroundColor="#ffffff" transparent="1" halign="center" />',
                '<widget name="detail" position="775,455" size="410,68" zPosition="4" font="Regular;15" foregroundColor="#9fc4d7" transparent="1" halign="center" />',
                '<eLabel position="25,600" size="1230,90" zPosition="8" backgroundColor="#062d40" />',
                '<widget name="footer" position="65,617" size="1150,48" zPosition="9" font="Regular;17" foregroundColor="#9fc4d7" transparent="1" halign="center" valign="center" />',
            ]
        else:
            widgets = [
                '<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />',
                '<widget name="section" position="108,230" size="1100,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
                '<eLabel position="98,340" size="1180,490" zPosition="2" backgroundColor="#021d2b" borderWidth="2" borderColor="#2e9dce" />',
                '<eLabel position="1320,340" size="500,490" zPosition="2" backgroundColor="#021d2b" borderWidth="2" borderColor="#2e9dce" />',
                '<widget name="phase" position="145,455" size="1085,90" zPosition="4" font="Regular;40" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />',
                '<widget name="info" position="145,585" size="1085,170" zPosition="4" font="Regular;27" foregroundColor="#b9d7e8" transparent="1" halign="center" valign="center" />',
                '<widget name="progress_title" position="1370,405" size="400,52" zPosition="4" font="Regular;31" foregroundColor="#6fdcff" transparent="1" />',
                '<widget name="progress" position="1360,515" size="420,42" zPosition="4" borderWidth="2" borderColor="#6fdcff" />',
                '<widget name="percent" position="1360,575" size="420,60" zPosition="4" font="Regular;40" foregroundColor="#ffffff" transparent="1" halign="center" />',
                '<widget name="detail" position="1360,670" size="420,105" zPosition="4" font="Regular;22" foregroundColor="#9fc4d7" transparent="1" halign="center" />',
                '<eLabel position="38,900" size="1844,135" zPosition="8" backgroundColor="#062d40" />',
                '<widget name="footer" position="98,930" size="1720,68" zPosition="9" font="Regular;24" foregroundColor="#9fc4d7" transparent="1" halign="center" valign="center" />',
            ]

        widgets.extend(p._system_header_widgets(self.hd))
        self.skin = '<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>' % (
            self.w, self.h, ''.join(widgets))
        Screen.__init__(self, session)
        self['bg'] = p.Pixmap()
        self['version'] = Label('')
        p._setup_system_header(self)
        self['section'] = Label('AKTUALIZÁCIA PICONHUBU')
        self['phase'] = Label('Pripravujem aktualizáciu...')
        self['progress'] = ProgressBar()
        self['progress'].setRange((0, 100))
        self['progress_title'] = Label('PRIEBEH')
        self['percent'] = Label('0 %')
        self['detail'] = Label('Pripravujem súbory...')
        self['info'] = Label('Aktualizácia prebieha bezpečne na pozadí.\nPo dokončení sa Enigma2 GUI automaticky reštartuje.')
        self['footer'] = Label('Počas aktualizácie PiconHub nevypínaj.')
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.ignore, 'cancel': self.ignore}, -1)
        self.timer = eTimer()
        self.timer.callback.append(self.step)
        self.onLayoutFinish.append(self.start)

    def ignore(self):
        return

    def _set_progress(self, value):
        value = max(0, min(100, int(value)))
        self['progress'].setValue(value)
        self['percent'].setText('%d %%' % value)

    def start(self):
        try:
            self['bg'].instance.setPixmapFromFile(
                os.path.join(p.ASSET_PATH, 'missing_%s_base.jpg' % ('hd' if self.hd else 'fhd')))
        except Exception:
            pass
        try:
            os.makedirs(self.backup)
        except Exception:
            pass
        self.files = self.manifest.get('files') or []
        self._set_progress(0)
        self.timer.start(100, True)

    def pct(self, done, total, base=0, span=100):
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
                rel = _safe_relative_path(item.get('path'))
                url = str(item.get('url') or '')
                digest = str(item.get('sha256') or '').lower()
                if not url.startswith(_ALLOWED_UPDATE_PREFIX) or len(digest) != 64:
                    raise PiconHubPluginUpdateError('Neplatný update manifest pre %s.' % rel)
                self['phase'].setText('SŤAHUJEM A OVERUJEM')
                self['detail'].setText(rel)
                data = self.up._fetch(url)
                if hashlib.sha256(data).hexdigest().lower() != digest:
                    raise PiconHubPluginUpdateError('SHA-256 nesúhlasí pre %s.' % rel)
                self.prepared.append((rel, data))
                self.index += 1
                self._set_progress(self.pct(self.index, total, 0, 60))
                self.timer.start(60, True)
                return

            if self.stage == 'install':
                if self.index >= total:
                    self.finish()
                    return
                rel, data = self.prepared[self.index]
                target = os.path.join(self.up.plugin_path, rel)
                parent = os.path.dirname(target)
                if not os.path.isdir(parent):
                    os.makedirs(parent)
                backup = os.path.join(self.backup, rel)
                if os.path.exists(target):
                    bdir = os.path.dirname(backup)
                    if not os.path.isdir(bdir):
                        os.makedirs(bdir)
                    shutil.copy2(target, backup)
                tmp = target + '.piconhub-update'
                f = open(tmp, 'wb')
                f.write(data)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass
                f.close()
                os.rename(tmp, target)
                self.changed.append((target, backup if os.path.exists(backup) else None))
                self.index += 1
                self['phase'].setText('INŠTALUJEM')
                self['detail'].setText(rel)
                self._set_progress(self.pct(self.index, total, 60, 40))
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
        self['info'].setText('%s\nGUI sa nereštartuje.' % error)
        self['detail'].setText('Zmeny boli vrátené späť.')
        self['footer'].setText('Aktualizácia nebola dokončená.')

    def finish(self):
        self._set_progress(100)
        self['phase'].setText('AKTUALIZÁCIA DOKONČENÁ')
        self['detail'].setText('Nová verzia je nainštalovaná.')
        self['info'].setText('Enigma2 GUI sa automaticky reštartuje za 3 sekundy.')
        self['footer'].setText('Aktualizácia prebehla úspešne.')
        self.timer.callback.remove(self.step)
        self.timer.callback.append(self.tick)
        self.timer.start(1000, True)

    def tick(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self['info'].setText('Reštartujem Enigma2 GUI...')
            _restart_gui(self.session)
            return
        self['info'].setText('Enigma2 GUI sa automaticky reštartuje za %d sekundy.' % self.countdown)
        self.timer.start(1000, True)


_old_quick = p.PiconHubMain.quickUpdate


def quick_menu(self):
    self.session.open(UpdateMenu)


p.PiconHubMain.quickUpdate = quick_menu
p.PiconHubUpdateMenu = UpdateMenu
