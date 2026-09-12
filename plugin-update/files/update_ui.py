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
        w = [
            '<widget name="bg" position="0,0" size="1280,127" zPosition="0" alphatest="blend" />',
            '<widget name="body" position="20,127" size="1240,485" zPosition="0" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (BG, CYAN),
            '<widget name="footer" position="20,612" size="1240,72" zPosition="0" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (FOOTER, CYAN_DIM),
        ]
        if buttons:
            w += [
                '<widget name="red_btn" position="38,620" size="278,56" zPosition="4" backgroundColor="#430d16" borderWidth="2" borderColor="%s" transparent="0" />' % RED,
                '<widget name="red_dot" position="50,627" size="42,42" zPosition="5" font="Regular;31" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % RED,
                '<widget name="red_title" position="100,626" size="200,22" zPosition="6" font="Regular;18" foregroundColor="%s" transparent="1" halign="left" valign="center" />' % WHITE,
                '<widget name="red_sub" position="100,649" size="200,17" zPosition="6" font="Regular;11" foregroundColor="#d9d9d9" transparent="1" halign="left" valign="center" />',
                '<widget name="green_btn" position="347,620" size="278,56" zPosition="4" backgroundColor="#063e1d" borderWidth="2" borderColor="%s" transparent="0" />' % GREEN,
                '<widget name="green_dot" position="359,627" size="42,42" zPosition="5" font="Regular;27" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % GREEN,
                '<widget name="green_title" position="407,626" size="205,22" zPosition="6" font="Regular;13" foregroundColor="%s" transparent="1" halign="left" valign="center" />' % WHITE,
                '<widget name="green_sub" position="407,649" size="205,17" zPosition="6" font="Regular;10" foregroundColor="#d9d9d9" transparent="1" halign="left" valign="center" />',
            ]
        return w
    w = [
        '<widget name="bg" position="0,0" size="1920,190" zPosition="0" alphatest="blend" />',
        '<widget name="body" position="30,190" size="1860,728" zPosition="0" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (BG, CYAN),
        '<widget name="footer" position="30,918" size="1860,108" zPosition="0" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (FOOTER, CYAN_DIM),
    ]
    if buttons:
        w += [
            '<widget name="red_btn" position="55,936" size="395,79" zPosition="4" backgroundColor="#430d16" borderWidth="3" borderColor="%s" transparent="0" />' % RED,
            '<widget name="red_dot" position="72,946" size="62,58" zPosition="5" font="Regular;46" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % RED,
            '<widget name="red_title" position="145,943" size="285,31" zPosition="6" font="Regular;27" foregroundColor="%s" transparent="1" halign="left" valign="center" />' % WHITE,
            '<widget name="red_sub" position="145,977" size="285,22" zPosition="6" font="Regular;16" foregroundColor="#d9d9d9" transparent="1" halign="left" valign="center" />',
            '<widget name="green_btn" position="516,936" size="395,79" zPosition="4" backgroundColor="#063e1d" borderWidth="3" borderColor="%s" transparent="0" />' % GREEN,
            '<widget name="green_dot" position="533,946" size="62,58" zPosition="5" font="Regular;39" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % GREEN,
            '<widget name="green_title" position="602,943" size="295,31" zPosition="6" font="Regular;19" foregroundColor="%s" transparent="1" halign="left" valign="center" />' % WHITE,
            '<widget name="green_sub" position="602,977" size="295,22" zPosition="6" font="Regular;15" foregroundColor="#d9d9d9" transparent="1" halign="left" valign="center" />',
        ]
    return w

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
    obj.skin = '<screen name="%s" position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>' % (name, obj.gui_w, obj.gui_h, ''.join(all_widgets))
    Screen.__init__(obj, session)
    obj['bg'] = Pixmap(); obj['body'] = Label(''); obj['footer'] = Label(''); obj['version'] = Label('')
    p._setup_system_header(obj)
    if buttons:
        obj['red_btn'] = Label(''); obj['red_dot'] = Label('←'); obj['red_title'] = Label(''); obj['red_sub'] = Label('')
        obj['green_btn'] = Label(''); obj['green_dot'] = Label('▶'); obj['green_title'] = Label(''); obj['green_sub'] = Label('')


def _ready_base(obj):
    mode = 'hd' if obj.hd else 'fhd'
    try:
        obj['bg'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH, 'updater_header_%s.jpg' % mode))
    except Exception as e:
        print('[PiconHub] updater header error:', e)


def _set_buttons(obj, red_title='SPÄŤ', red_sub='Návrat späť', green_title='OK, SPUSTIŤ AKTUALIZÁCIU', green_sub='Potvrdiť vybranú aktualizáciu'):
    obj['red_title'].setText(red_title); obj['red_sub'].setText(red_sub); obj['green_title'].setText(green_title); obj['green_sub'].setText(green_sub)


def _choice_widgets(hd):
    if hd:
        return [
            '<widget name="row1" position="63,220" size="785,70" zPosition="1" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (PANEL, CYAN_DIM),
            '<widget name="row2" position="63,294" size="785,70" zPosition="1" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (PANEL, CYAN_DIM),
            '<widget name="focus" position="63,220" size="785,70" zPosition="2" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (PANEL_FOCUS, CYAN),
            '<widget name="list" position="0,0" size="1,1" zPosition="0" font="Regular;1" itemHeight="1" transparent="1" selectionDisabled="1" />',
            '<widget name="row1_icon" position="82,229" size="52,50" zPosition="4" font="Regular;31" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
            '<widget name="row1_title" position="155,225" size="610,28" zPosition="4" font="Regular;22" foregroundColor="%s" transparent="1" valign="center" />' % CYAN,
            '<widget name="row1_sub" position="155,254" size="610,25" zPosition="4" font="Regular;15" foregroundColor="%s" transparent="1" valign="center" />' % TEXT,
            '<widget name="row1_arrow" position="793,229" size="38,50" zPosition="4" font="Regular;34" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
            '<widget name="row2_icon" position="82,303" size="52,50" zPosition="4" font="Regular;31" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
            '<widget name="row2_title" position="155,299" size="610,28" zPosition="4" font="Regular;22" foregroundColor="%s" transparent="1" valign="center" />' % CYAN,
            '<widget name="row2_sub" position="155,328" size="610,25" zPosition="4" font="Regular;15" foregroundColor="%s" transparent="1" valign="center" />' % TEXT,
            '<widget name="row2_arrow" position="793,303" size="38,50" zPosition="4" font="Regular;34" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
            '<widget name="divider" position="880,214" size="1,330" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
            '<widget name="right_icon" position="1020,235" size="90,70" zPosition="5" font="Regular;42" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
            '<widget name="name" position="900,310" size="320,45" zPosition="5" font="Regular;25" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
            '<widget name="state" position="900,365" size="320,38" zPosition="5" font="Regular;20" foregroundColor="%s" transparent="1" halign="center" />' % GREEN,
            '<widget name="detail" position="890,425" size="340,105" zPosition="5" font="Regular;17" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
        ]
    return [
        '<widget name="row1" position="95,330" size="1180,105" zPosition="1" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (PANEL, CYAN_DIM),
        '<widget name="row2" position="95,441" size="1180,105" zPosition="1" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (PANEL, CYAN_DIM),
        '<widget name="focus" position="95,330" size="1180,105" zPosition="2" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (PANEL_FOCUS, CYAN),
        '<widget name="list" position="0,0" size="1,1" zPosition="0" font="Regular;1" itemHeight="1" transparent="1" selectionDisabled="1" />',
        '<widget name="row1_icon" position="122,344" size="78,76" zPosition="4" font="Regular;47" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
        '<widget name="row1_title" position="230,338" size="900,43" zPosition="4" font="Regular;31" foregroundColor="%s" transparent="1" valign="center" />' % CYAN,
        '<widget name="row1_sub" position="230,383" size="900,38" zPosition="4" font="Regular;22" foregroundColor="%s" transparent="1" valign="center" />' % TEXT,
        '<widget name="row1_arrow" position="1185,344" size="60,76" zPosition="4" font="Regular;50" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
        '<widget name="row2_icon" position="122,455" size="78,76" zPosition="4" font="Regular;47" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
        '<widget name="row2_title" position="230,449" size="900,43" zPosition="4" font="Regular;31" foregroundColor="%s" transparent="1" valign="center" />' % CYAN,
        '<widget name="row2_sub" position="230,494" size="900,38" zPosition="4" font="Regular;22" foregroundColor="%s" transparent="1" valign="center" />' % TEXT,
        '<widget name="row2_arrow" position="1185,455" size="60,76" zPosition="4" font="Regular;50" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
        '<widget name="divider" position="1320,322" size="2,495" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
        '<widget name="right_icon" position="1510,350" size="120,95" zPosition="5" font="Regular;61" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % CYAN,
        '<widget name="name" position="1365,455" size="430,65" zPosition="5" font="Regular;34" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
        '<widget name="state" position="1365,535" size="430,50" zPosition="5" font="Regular;26" foregroundColor="%s" transparent="1" halign="center" />' % GREEN,
        '<widget name="detail" position="1345,625" size="470,150" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
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
        self['row1'] = Label(''); self['row2'] = Label(''); self['focus'] = Label(''); self['divider'] = Label('')
        self['row1_icon'] = Label('▤'); self['row1_title'] = Label('AKTUALIZOVAŤ PICONY'); self['row1_sub'] = Label('Aktualizácia databázy piconov zo servera'); self['row1_arrow'] = Label('›')
        self['row2_icon'] = Label('⚙'); self['row2_title'] = Label('AKTUALIZOVAŤ PLUGIN'); self['row2_sub'] = Label('Skontrolovať a nainštalovať novú verziu PiconHubu'); self['row2_arrow'] = Label('›')
        self['right_icon'] = Label('▤')
        self['list'] = MenuList(['PICONY', 'PLUGIN'])
        self['name'] = Label(''); self['state'] = Label(''); self['detail'] = Label('')
        _set_buttons(self, 'SPÄŤ', 'Návrat do hlavnej ponuky', 'OK, SPUSTIŤ AKTUALIZÁCIU', 'Vybratú položku aktualizovať')
        self['actions'] = ActionMap(['OkCancelActions','DirectionActions','ColorActions'], {
            'cancel': self.close, 'red': self.close,
            'ok': self.open_selected, 'green': self.open_selected,
            'up': self.up, 'down': self.down,
        }, -1)
        self.poll_timer = eTimer(); self.poll_timer.callback.append(self._poll_check)
        self.onLayoutFinish.append(self._ready)

    def _ready(self):
        _ready_base(self)
        self._selected()

    def _index(self):
        try: return self['list'].getSelectedIndex()
        except Exception: return 0

    def _selected(self):
        idx = self._index()
        try:
            x = 63 if self.hd else 95
            y = (220 if idx == 0 else 294) if self.hd else (330 if idx == 0 else 441)
            self['focus'].instance.move(ePoint(x, y))
        except Exception:
            pass
        if idx == 0:
            self['right_icon'].setText('▤')
            self['name'].setText('PICONY')
            self['state'].setText('AKTUALIZÁCIA DATABÁZY')
            self['detail'].setText('Stiahne chýbajúce alebo zmenené picony podľa tvojich nastavení.')
        else:
            self['right_icon'].setText('⚙')
            self['name'].setText('PLUGIN')
            self['state'].setText('AKTUALIZÁCIA PICONHUBU')
            self['detail'].setText('Skontroluje novú verziu PiconHubu a bezpečne ju nainštaluje.')

    def up(self):
        if not self.checking:
            self['list'].up(); self._selected()

    def down(self):
        if not self.checking:
            self['list'].down(); self._selected()

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
            try: self._check_result = pu.PiconHubPluginUpdater(timeout=6).check()
            except Exception as e: self._check_error = str(e)
            self._check_done = True
        thread = Thread(target=worker); thread.daemon = True; thread.start()
        self.poll_timer.start(100, True)

    def _poll_check(self):
        if not self._check_done:
            self.poll_timer.start(100, True); return
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


def _dialog_widgets(hd,status=False,error=False):
    icon_color=RED if error else GREEN
    if hd:
        w=['<widget name="divider" position="880,214" size="1,330" zPosition="2" backgroundColor="#39bff8" transparent="0" />']
        if status:
            w += ['<widget name="icon" position="145,285" size="150,150" zPosition="5" font="Regular;96" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % icon_color,'<widget name="title" position="330,280" size="800,60" zPosition="5" font="Regular;31" foregroundColor="%s" transparent="1" />' % WHITE,'<widget name="message" position="330,360" size="800,55" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" />' % TEXT,'<widget name="detail" position="330,430" size="800,90" zPosition="5" font="Regular;18" foregroundColor="%s" transparent="1" />' % TEXT_DIM]
        else:
            w += ['<widget name="title" position="90,260" size="720,55" zPosition="5" font="Regular;30" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,'<widget name="versions" position="90,345" size="720,120" zPosition="5" font="Regular;22" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,'<widget name="notes_title" position="900,270" size="320,42" zPosition="5" font="Regular;24" foregroundColor="#6fdcff" transparent="1" halign="center" />','<widget name="notes" position="880,330" size="360,220" zPosition="5" font="Regular;17" foregroundColor="%s" transparent="1" halign="center" />' % TEXT]
        return w
    w=['<widget name="divider" position="1320,322" size="2,495" zPosition="2" backgroundColor="#39bff8" transparent="0" />']
    if status:
        w += ['<widget name="icon" position="220,420" size="220,220" zPosition="5" font="Regular;140" foregroundColor="%s" transparent="1" halign="center" valign="center" />' % icon_color,'<widget name="title" position="500,420" size="1120,80" zPosition="5" font="Regular;45" foregroundColor="%s" transparent="1" />' % WHITE,'<widget name="message" position="500,540" size="1120,75" zPosition="5" font="Regular;33" foregroundColor="%s" transparent="1" />' % TEXT,'<widget name="detail" position="500,645" size="1120,135" zPosition="5" font="Regular;25" foregroundColor="%s" transparent="1" />' % TEXT_DIM]
    else:
        w += ['<widget name="title" position="135,390" size="1080,80" zPosition="5" font="Regular;44" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,'<widget name="versions" position="135,520" size="1080,180" zPosition="5" font="Regular;31" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,'<widget name="notes_title" position="1365,405" size="430,55" zPosition="5" font="Regular;34" foregroundColor="#6fdcff" transparent="1" halign="center" />','<widget name="notes" position="1335,490" size="490,330" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" halign="center" />' % TEXT]
    return w


class PiconHubPluginConfirm(Screen):
    def __init__(self,session,result):
        self.result=result or {}; self.gui_w,self.gui_h=_desktop(); self.hd=self.gui_w<=1280
        _init_base(self,session,'PiconHubPluginConfirm',_dialog_widgets(self.hd,False,False),True)
        self['section']=Label('↻  AKTUALIZÁCIA PICONHUBU'); self['summary']=Label('Je dostupná nová verzia'); self['divider']=Label(''); self['title']=Label('SPUSTIŤ AKTUALIZÁCIU?')
        self['versions']=Label('Aktuálna verzia: %s\nNová verzia: %s\n\nPo dokončení sa Enigma2 GUI automaticky reštartuje.' % (self.result.get('current_version') or '—',self.result.get('remote_version') or '—')); self['notes_title']=Label('ČO JE NOVÉ'); self['notes']=Label(self.result.get('notes') or 'Bez poznámok k vydaniu.')
        _set_buttons(self,'SPÄŤ','Zrušiť aktualizáciu','OK, SPUSTIŤ AKTUALIZÁCIU','Nainštalovať novú verziu'); self['actions']=ActionMap(['OkCancelActions','ColorActions'],{'cancel':self.reject,'red':self.reject,'ok':self.accept,'green':self.accept},-1); self.onLayoutFinish.append(self._ready)
    def _ready(self): _ready_base(self)
    def accept(self): self.close(True)
    def reject(self): self.close(False)


class PiconHubUpdateStatus(Screen):
    def __init__(self,session,title,message,detail='',error=False):
        self.error=bool(error); self.gui_w,self.gui_h=_desktop(); self.hd=self.gui_w<=1280
        _init_base(self,session,'PiconHubUpdateStatus',_dialog_widgets(self.hd,True,self.error),True)
        self['section']=Label('↻  AKTUALIZÁCIA PICONHUBU'); self['summary']=Label('Stav aktualizácie'); self['divider']=Label(''); self['icon']=Label('!' if self.error else '✓'); self['title']=Label(title); self['message']=Label(message); self['detail']=Label(detail)
        _set_buttons(self,'SPÄŤ','Návrat na výber','OK','Zavrieť stav aktualizácie'); self['actions']=ActionMap(['OkCancelActions','ColorActions'],{'cancel':self.close,'red':self.close,'ok':self.close,'green':self.close},-1); self.onLayoutFinish.append(self._ready)
    def _ready(self): _ready_base(self)


def _progress_widgets(hd):
    if hd:
        return ['<widget name="phase" position="90,300" size="720,60" zPosition="5" font="Regular;29" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,'<widget name="info" position="90,390" size="720,130" zPosition="5" font="Regular;20" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,'<widget name="progress_title" position="910,300" size="300,40" zPosition="5" font="Regular;24" foregroundColor="#6fdcff" transparent="1" halign="center" />','<widget name="progress" position="900,365" size="320,28" zPosition="5" borderWidth="2" borderColor="#6fdcff" />','<widget name="percent" position="900,410" size="320,55" zPosition="5" font="Regular;31" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,'<widget name="detail" position="880,480" size="360,75" zPosition="5" font="Regular;16" foregroundColor="%s" transparent="1" halign="center" />' % TEXT_DIM]
    return ['<widget name="phase" position="135,450" size="1080,90" zPosition="5" font="Regular;42" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,'<widget name="info" position="135,585" size="1080,195" zPosition="5" font="Regular;29" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,'<widget name="progress_title" position="1365,450" size="430,55" zPosition="5" font="Regular;34" foregroundColor="#6fdcff" transparent="1" halign="center" />','<widget name="progress" position="1360,545" size="440,40" zPosition="5" borderWidth="2" borderColor="#6fdcff" />','<widget name="percent" position="1360,610" size="440,80" zPosition="5" font="Regular;45" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,'<widget name="detail" position="1335,720" size="490,110" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" halign="center" />' % TEXT_DIM]


class PiconHubPluginProgress(Screen):
    def __init__(self,session,manifest):
        self.session=session; self.manifest=manifest or {}; self.updater=pu.PiconHubPluginUpdater(timeout=8); self.stage='download'; self.index=0; self.files=self.manifest.get('files') or []; self.prepared=[]; self.changed=[]; self.backup='/tmp/piconhub-plugin-backup-%d' % int(time.time()); self.countdown=3; self.gui_w,self.gui_h=_desktop(); self.hd=self.gui_w<=1280
        _init_base(self,session,'PiconHubPluginProgress',_progress_widgets(self.hd),False)
        self['section']=Label('↻  AKTUALIZÁCIA PICONHUBU'); self['summary']=Label('Bezpečná inštalácia'); self['phase']=Label('PRIPRAVUJEM AKTUALIZÁCIU'); self['info']=Label('Aktualizácia prebieha bezpečne.\nPo dokončení sa Enigma2 GUI automaticky reštartuje.'); self['progress_title']=Label('PRIEBEH'); self['progress']=ProgressBar(); self['progress'].setRange((0,100)); self['progress'].setValue(0); self['percent']=Label('0 %'); self['detail']=Label('Pripravujem súbory...'); self['actions']=ActionMap(['OkCancelActions','ColorActions'],{'cancel':self.ignore,'ok':self.ignore,'red':self.ignore,'green':self.ignore,'yellow':self.ignore,'blue':self.ignore},-1); self.timer=eTimer(); self.timer.callback.append(self.step); self.onLayoutFinish.append(self.start)
    def ignore(self): return
    def start(self):
        _ready_base(self)
        try: os.makedirs(self.backup)
        except Exception: pass
        self.timer.start(100,True)
    def _progress(self,value): value=max(0,min(100,int(value))); self['progress'].setValue(value); self['percent'].setText('%d %%' % value)
    def _pct(self,done,total,base,span): return base+int((float(done)/max(1,total))*span)
    def step(self):
        try:
            total=len(self.files)
            if self.stage=='download':
                if self.index>=total: self.stage='install'; self.index=0; self.timer.start(80,True); return
                item=self.files[self.index]; rel=pu._safe_relative_path(item.get('path')); url=str(item.get('url') or ''); digest=str(item.get('sha256') or '').lower()
                if not url.startswith(pu._ALLOWED_UPDATE_PREFIX) or len(digest)!=64: raise pu.PiconHubPluginUpdateError('Neplatný update manifest pre %s.' % rel)
                self['phase'].setText('SŤAHUJEM A OVERUJEM'); self['detail'].setText(rel); data=self.updater._fetch(url)
                if hashlib.sha256(data).hexdigest().lower()!=digest: raise pu.PiconHubPluginUpdateError('SHA-256 nesúhlasí pre %s.' % rel)
                self.prepared.append((rel,data)); self.index+=1; self._progress(self._pct(self.index,total,0,60)); self.timer.start(60,True); return
            if self.index>=total: self.finish(); return
            rel,data=self.prepared[self.index]; target=os.path.join(self.updater.plugin_path,rel); parent=os.path.dirname(target)
            if not os.path.isdir(parent): os.makedirs(parent)
            backup=os.path.join(self.backup,rel)
            if os.path.exists(target):
                bd=os.path.dirname(backup)
                if not os.path.isdir(bd): os.makedirs(bd)
                shutil.copy2(target,backup)
            tmp=target+'.piconhub-update'; h=open(tmp,'wb'); h.write(data); h.flush()
            try: os.fsync(h.fileno())
            except Exception: pass
            h.close()
            try: os.chmod(tmp,0o644)
            except Exception: pass
            os.rename(tmp,target); self.changed.append((target,backup if os.path.exists(backup) else None)); self.index+=1; self['phase'].setText('INŠTALUJEM'); self['detail'].setText(rel); self._progress(self._pct(self.index,total,60,40)); self.timer.start(60,True)
        except Exception as e: self.rollback(e)
    def rollback(self,error):
        for target,backup in reversed(self.changed):
            try:
                if backup: shutil.copy2(backup,target)
                elif os.path.exists(target): os.remove(target)
            except Exception: pass
        self['phase'].setText('AKTUALIZÁCIA ZLYHALA'); self['summary'].setText('Zmeny boli vrátené späť'); self['info'].setText('%s\nGUI sa nereštartuje.' % error); self['detail'].setText('Pôvodná verzia zostala zachovaná.'); self['actions']=ActionMap(['OkCancelActions','ColorActions'],{'cancel':self.close,'ok':self.close,'red':self.close},-1)
    def finish(self):
        self._progress(100); self['phase'].setText('AKTUALIZÁCIA DOKONČENÁ'); self['summary'].setText('Nová verzia je nainštalovaná'); self['detail'].setText('Overenie a inštalácia prebehli úspešne.'); self['info'].setText('Enigma2 GUI sa automaticky reštartuje za 3 sekundy.')
        try: self.timer.callback.remove(self.step)
        except Exception: pass
        self.timer.callback.append(self.tick); self.timer.start(1000,True)
    def tick(self):
        self.countdown-=1
        if self.countdown<=0: self['info'].setText('Reštartujem Enigma2 GUI...'); pu._restart_gui(self.session); return
        self['info'].setText('Enigma2 GUI sa automaticky reštartuje za %d sekundy.' % self.countdown); self.timer.start(1000,True)


def _show_latest(screen,result=None):
    result=result or {}; version=result.get('remote_version') or result.get('current_version') or pu.RELEASE_VERSION; screen.session.open(PiconHubUpdateStatus,'POUŽÍVAŠ NAJNOVŠIU VERZIU','PiconHub %s je aktuálny.' % version,'Nie je potrebná žiadna aktualizácia pluginu.',False)
def _show_error(screen,error): screen.session.open(PiconHubUpdateStatus,'KONTROLA AKTUALIZÁCIE ZLYHALA','Nepodarilo sa overiť dostupnú verziu PiconHubu.',str(error or 'Neznáma chyba.'),True)
def _offer_update(screen,result,manual=False):
    result=result or {}
    if result.get('available'):
        def confirmed(answer):
            if answer and result.get('manifest'): screen.session.open(PiconHubPluginProgress,result.get('manifest'))
        screen.session.openWithCallback(confirmed,PiconHubPluginConfirm,result); return
    if manual: _show_latest(screen,result)
def _manual_update_check(screen):
    try: result=pu.PiconHubPluginUpdater().check()
    except Exception as e: _show_error(screen,e); return
    _offer_update(screen,result,manual=True)
def _async_layout_ready(self):
    pu._original_layout_ready(self)
    if pu._AUTO_CHECK_DONE: return
    pu._AUTO_CHECK_DONE=True; self._piconhub_auto_result=None; self._piconhub_auto_error=None; self._piconhub_auto_done=False; self._piconhub_auto_delay=eTimer(); self._piconhub_auto_poll=eTimer()
    def worker():
        try: self._piconhub_auto_result=pu.PiconHubPluginUpdater(timeout=4).check()
        except Exception as e: self._piconhub_auto_error=str(e)
        self._piconhub_auto_done=True
    def begin(): t=Thread(target=worker); t.daemon=True; t.start(); self._piconhub_auto_poll.start(100,True)
    def poll():
        if not self._piconhub_auto_done: self._piconhub_auto_poll.start(100,True); return
        if self._piconhub_auto_error: print('[PiconHub] automatic plugin update check error:',self._piconhub_auto_error); return
        try: _offer_update(self,self._piconhub_auto_result or {},manual=False)
        except Exception as e: print('[PiconHub] automatic plugin update offer error:',e)
    self._piconhub_auto_delay.callback.append(begin); self._piconhub_auto_poll.callback.append(poll); self._piconhub_auto_delay.start(1800,True)


p.PiconHubUpdateMenu=PiconHubUpdateChoice
pu._offer_update=_offer_update
pu._manual_update_check=_manual_update_check
p.PiconHubMain._layoutReady=_async_layout_ready
