# -*- coding: utf-8 -*-
from __future__ import print_function

import os
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from . import plugin as p
from . import update_ui as ui


def _frame(hd, buttons=True):
    if hd:
        w = [
            '<widget name="body" position="20,127" size="1240,485" zPosition="0" backgroundColor="#022635" transparent="0" />',
            '<widget name="topline" position="20,206" size="1240,1" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
            '<widget name="midline" position="880,207" size="1,405" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
            '<widget name="bottomline" position="20,611" size="1240,1" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
            '<widget name="footer" position="20,612" size="1240,72" zPosition="0" backgroundColor="#021f2c" transparent="0" />']
        if buttons:
            w += [
                '<widget name="red_pic" position="37,624" size="263,53" zPosition="5" alphatest="blend" />',
                '<widget name="green_pic" position="344,624" size="263,53" zPosition="5" alphatest="blend" />',
                '<widget name="red_title" position="93,629" size="190,20" zPosition="6" font="Regular;15" foregroundColor="#ffffff" transparent="1" halign="center" />',
                '<widget name="red_sub" position="93,649" size="190,16" zPosition="6" font="Regular;9" foregroundColor="#dbefff" transparent="1" halign="center" />',
                '<widget name="green_title" position="400,629" size="190,20" zPosition="6" font="Regular;13" foregroundColor="#ffffff" transparent="1" halign="center" />',
                '<widget name="green_sub" position="400,649" size="190,16" zPosition="6" font="Regular;9" foregroundColor="#dbefff" transparent="1" halign="center" />']
        return w
    w = [
        '<widget name="body" position="30,190" size="1860,728" zPosition="0" backgroundColor="#022635" transparent="0" />',
        '<widget name="topline" position="30,310" size="1860,2" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
        '<widget name="midline" position="1320,312" size="2,606" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
        '<widget name="bottomline" position="30,916" size="1860,2" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
        '<widget name="footer" position="30,918" size="1860,108" zPosition="0" backgroundColor="#021f2c" transparent="0" />']
    if buttons:
        w += [
            '<widget name="red_pic" position="55,936" size="395,79" zPosition="5" alphatest="blend" />',
            '<widget name="green_pic" position="516,936" size="395,79" zPosition="5" alphatest="blend" />',
            '<widget name="red_title" position="140,944" size="285,30" zPosition="6" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="red_sub" position="140,974" size="285,24" zPosition="6" font="Regular;14" foregroundColor="#dbefff" transparent="1" halign="center" />',
            '<widget name="green_title" position="601,944" size="285,30" zPosition="6" font="Regular;19" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="green_sub" position="601,974" size="285,24" zPosition="6" font="Regular;14" foregroundColor="#dbefff" transparent="1" halign="center" />']
    return w


def _choice_widgets(hd):
    if hd:
        w = [
            '<widget name="bg" position="0,0" size="1280,127" zPosition="0" alphatest="blend" />',
            '<widget name="section" position="72,153" size="570,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />',
            '<widget name="summary" position="660,153" size="570,42" zPosition="4" font="Regular;19" foregroundColor="#ffffff" transparent="1" halign="right" />',
            '<widget name="row1" position="63,220" size="785,70" zPosition="1" backgroundColor="#07384a" borderWidth="1" borderColor="#287c9d" transparent="0" />',
            '<widget name="row2" position="63,294" size="785,70" zPosition="1" backgroundColor="#07384a" borderWidth="1" borderColor="#287c9d" transparent="0" />',
            '<widget name="list" position="72,225" size="770,135" zPosition="4" font="Regular;22" itemHeight="58" transparent="1" />',
            '<widget name="name" position="900,300" size="320,48" zPosition="5" font="Regular;25" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="state" position="900,365" size="320,38" zPosition="5" font="Regular;20" foregroundColor="#4ee878" transparent="1" halign="center" />',
            '<widget name="detail" position="880,430" size="360,115" zPosition="5" font="Regular;17" foregroundColor="#dbefff" transparent="1" halign="center" />']
    else:
        w = [
            '<widget name="bg" position="0,0" size="1920,190" zPosition="0" alphatest="blend" />',
            '<widget name="section" position="108,230" size="840,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />',
            '<widget name="summary" position="1010,230" size="790,60" zPosition="4" font="Regular;27" foregroundColor="#ffffff" transparent="1" halign="right" />',
            '<widget name="row1" position="95,330" size="1180,105" zPosition="1" backgroundColor="#07384a" borderWidth="2" borderColor="#287c9d" transparent="0" />',
            '<widget name="row2" position="95,441" size="1180,105" zPosition="1" backgroundColor="#07384a" borderWidth="2" borderColor="#287c9d" transparent="0" />',
            '<widget name="list" position="108,338" size="1150,200" zPosition="4" font="Regular;30" itemHeight="82" transparent="1" />',
            '<widget name="name" position="1365,450" size="430,65" zPosition="5" font="Regular;34" foregroundColor="#ffffff" transparent="1" halign="center" />',
            '<widget name="state" position="1365,530" size="430,50" zPosition="5" font="Regular;26" foregroundColor="#4ee878" transparent="1" halign="center" />',
            '<widget name="detail" position="1335,610" size="490,165" zPosition="5" font="Regular;23" foregroundColor="#dbefff" transparent="1" halign="center" />']
    return w + _frame(hd, True)


def _install(self, rt, rs, gt, gs, buttons=True):
    for name in ('body','topline','midline','bottomline','footer'):
        self[name] = Label('')
    if buttons:
        self['red_pic'] = Pixmap(); self['green_pic'] = Pixmap()
        self['red_title'] = Label(rt); self['red_sub'] = Label(rs)
        self['green_title'] = Label(gt); self['green_sub'] = Label(gs)


def _buttons(self):
    mode = 'hd' if self.hd else 'fhd'
    try:
        self['red_pic'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH, 'picons_btn_red_%s.png' % mode))
        self['green_pic'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH, 'picons_btn_green_%s.png' % mode))
    except Exception as e:
        print('[PiconHub] updater buttons:', e)


ui._choice_widgets = _choice_widgets
_oc_i = ui.PiconHubUpdateChoice.__init__; _oc_r = ui.PiconHubUpdateChoice._ready
def _ci(self, session):
    _oc_i(self, session); self['row1']=Label(''); self['row2']=Label('')
    _install(self,'SPÄŤ','Návrat do hlavnej ponuky','OK, SPUSTIŤ AKTUALIZÁCIU','Potvrdiť vybranú aktualizáciu')
    self['actions']=ActionMap(['OkCancelActions','DirectionActions','ColorActions'],{'cancel':self.close,'red':self.close,'ok':self.open_selected,'green':self.open_selected,'up':self.up,'down':self.down},-1)
def _cr(self): _oc_r(self); _buttons(self)
ui.PiconHubUpdateChoice.__init__=_ci; ui.PiconHubUpdateChoice._ready=_cr

_odw=ui._dialog_widgets
def _dw(hd,status=False,error=False):
    w=_odw(hd,status,error); w[0]='<widget name="bg" position="0,0" size="%s" zPosition="0" alphatest="blend" />' % ('1280,127' if hd else '1920,190'); return w+_frame(hd,True)
ui._dialog_widgets=_dw

_oci=ui.PiconHubPluginConfirm.__init__; _ocr=ui.PiconHubPluginConfirm._ready
def _coni(self,session,result): _oci(self,session,result); _install(self,'SPÄŤ','Zrušiť aktualizáciu','OK, SPUSTIŤ AKTUALIZÁCIU','Nainštalovať novú verziu')
def _conr(self): _ocr(self); _buttons(self)
ui.PiconHubPluginConfirm.__init__=_coni; ui.PiconHubPluginConfirm._ready=_conr

_osi=ui.PiconHubUpdateStatus.__init__; _osr=ui.PiconHubUpdateStatus._ready
def _sti(self,session,title,message,detail='',error=False):
    _osi(self,session,title,message,detail,error); _install(self,'SPÄŤ','Návrat na výber','OK','Zavrieť stav aktualizácie')
    self['actions']=ActionMap(['OkCancelActions','ColorActions'],{'cancel':self.close,'red':self.close,'ok':self.close,'green':self.close},-1)
def _str(self): _osr(self); _buttons(self)
ui.PiconHubUpdateStatus.__init__=_sti; ui.PiconHubUpdateStatus._ready=_str

_opw=ui._progress_widgets
def _pw(hd):
    w=_opw(hd); w[0]='<widget name="bg" position="0,0" size="%s" zPosition="0" alphatest="blend" />' % ('1280,127' if hd else '1920,190'); return w+_frame(hd,False)
ui._progress_widgets=_pw
_opi=ui.PiconHubPluginProgress.__init__
def _pi(self,session,manifest): _opi(self,session,manifest); _install(self,'','','','',False)
ui.PiconHubPluginProgress.__init__=_pi


def _open(self): self.session.open(ui.PiconHubUpdateChoice)
p.PiconHubMain.quickUpdate=_open
p.PiconHubUpdateMenu=ui.PiconHubUpdateChoice
