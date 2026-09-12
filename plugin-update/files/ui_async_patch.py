# -*- coding: utf-8 -*-
from __future__ import print_function
from threading import Thread
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.Screen import Screen
from enigma import eTimer, getDesktop
from . import plugin as p
from . import plugin_updater as pu
from . import update_menu as um

def _desktop():
    try:return getDesktop(0).size().width(),getDesktop(0).size().height()
    except Exception:return 1920,1080

def _key(x,y,w,h,c,t,hd):
    if not t:return ''
    return ('<eLabel position="%d,%d" size="%d,%d" zPosition="9" backgroundColor="#08283a" borderWidth="%d" borderColor="%s" />''<eLabel text="●" position="%d,%d" size="%d,%d" zPosition="10" font="Regular;%d" foregroundColor="%s" transparent="1" halign="center" valign="center" />''<eLabel text="%s" position="%d,%d" size="%d,%d" zPosition="10" font="Regular;%d" foregroundColor="#ffffff" transparent="1" valign="center" />')%(x,y,w,h,2 if hd else 3,c,x+12 if hd else x+18,y+3,44 if hd else 62,h-6,26 if hd else 38,c,t,x+62 if hd else x+90,y+3,w-(74 if hd else 104),h-6,18 if hd else 27)

def _bottom_widgets(hd,action='VYBRAŤ'):
    colors=('#ff4b55','#31df6b','#f2c94c','#3c9cff');labels=('SPÄŤ',action,'PICONY','PLUGIN') if action=='VYBRAŤ' else ('SPÄŤ',action,'','')
    if hd:panel=(25,600,1230,90);x,y,w,h,g=38,612,280,62,12
    else:panel=(38,900,1844,135);x,y,w,h,g=58,918,416,92,18
    a=['<eLabel position="%d,%d" size="%d,%d" zPosition="8" backgroundColor="#062d40" />'%panel]
    for i,t in enumerate(labels):a.append(_key(x+i*(w+g),y,w,h,colors[i],t,hd))
    return a

class PluginUpdateConfirm(Screen):
    def __init__(self,session,result):
        self.session=session;self.result=result or {};self.w,self.h=_desktop();self.hd=self.w<=1280
        if self.hd:w=['<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />','<widget name="section" position="72,153" size="900,42" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />','<eLabel position="65,228" size="650,330" zPosition="2" backgroundColor="#021d2b" />','<eLabel position="735,228" size="480,330" zPosition="2" backgroundColor="#021d2b" />','<widget name="question" position="95,258" size="590,52" zPosition="4" font="Regular;28" foregroundColor="#fff" transparent="1" />','<widget name="current" position="95,335" size="590,34" zPosition="4" font="Regular;20" foregroundColor="#c9e4f1" transparent="1" />','<widget name="remote" position="95,380" size="590,34" zPosition="4" font="Regular;20" foregroundColor="#6fdcff" transparent="1" />','<widget name="restart" position="95,455" size="590,64" zPosition="4" font="Regular;16" foregroundColor="#9fc4d7" transparent="1" />','<widget name="notes_title" position="765,252" size="420,36" zPosition="4" font="Regular;21" foregroundColor="#6fdcff" transparent="1" />','<widget name="notes" position="765,300" size="420,225" zPosition="4" font="Regular;16" foregroundColor="#dbefff" transparent="1" />']
        else:w=['<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />','<widget name="section" position="108,230" size="1350,60" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />','<eLabel position="98,340" size="970,490" zPosition="2" backgroundColor="#021d2b" />','<eLabel position="1100,340" size="720,490" zPosition="2" backgroundColor="#021d2b" />','<widget name="question" position="145,385" size="875,72" zPosition="4" font="Regular;41" foregroundColor="#ffffff" transparent="1" />','<widget name="current" position="145,510" size="875,48" zPosition="4" font="Regular;30" foregroundColor="#c9e4f1" transparent="1" />','<widget name="remote" position="145,575" size="875,48" zPosition="4" font="Regular;30" foregroundColor="#6fdcff" transparent="1" />','<widget name="restart" position="145,690" size="875,92" zPosition="4" font="Regular;24" foregroundColor="#9fc4d7" transparent="1" />','<widget name="notes_title" position="1145,380" size="630,52" zPosition="4" font="Regular;31" foregroundColor="#6fdcff" transparent="1" />','<widget name="notes" position="1145,455" size="630,320" zPosition="4" font="Regular;23" foregroundColor="#dbefff" transparent="1" />']
        w.extend(_bottom_widgets(self.hd,'AKTUALIZOVAŤ'));w.extend(p._system_header_widgets(self.hd));self.skin='<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>'%(self.w,self.h,''.join(w));Screen.__init__(self,session);self['bg']=p.Pixmap();self['version']=Label('');p._setup_system_header(self);self['section']=Label('AKTUALIZÁCIA PICONHUBU');self['question']=Label('JE DOSTUPNÁ NOVÁ VERZIA');self['current']=Label('Aktuálna verzia:  %s'%(self.result.get('current_version') or '—'));self['remote']=Label('Nová verzia:      %s'%(self.result.get('remote_version') or '—'));self['restart']=Label('Po úspešnej aktualizácii sa Enigma2 GUI automaticky reštartuje.');self['notes_title']=Label('ČO JE NOVÉ');self['notes']=Label(self.result.get('notes') or 'Bez poznámok k vydaniu.');self['actions']=ActionMap(['OkCancelActions','ColorActions'],{'ok':lambda:self.close(True),'green':lambda:self.close(True),'cancel':lambda:self.close(False),'red':lambda:self.close(False)},-1);self.onLayoutFinish.append(self.ready)
    def ready(self):
        try:self['bg'].instance.setPixmapFromFile(p.os.path.join(p.ASSET_PATH,'missing_%s_base.jpg'%('hd' if self.hd else 'fhd')))
        except Exception:pass

class PrettyUpdateMenu(Screen):
    def __init__(self,session):
        self.session=session;self.selected=0;self.checking=False;self.pending=None;self._check_done=False;self._check_result=None;self._check_error=None;self.w,self.h=_desktop();self.hd=self.w<=1280
        if self.hd:w=['<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />','<widget name="section" position="72,153" size="900,42" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />','<widget name="subtitle" position="72,205" size="1100,32" zPosition="4" font="Regular;18" foregroundColor="#b9d7e8" transparent="1" />','<widget name="row1" position="170,285" size="940,52" zPosition="4" font="Regular;29" foregroundColor="#fff" transparent="1" />','<widget name="desc1" position="215,340" size="860,42" zPosition="4" font="Regular;18" foregroundColor="#8fbad0" transparent="1" />','<widget name="row2" position="170,415" size="940,52" zPosition="4" font="Regular;29" foregroundColor="#fff" transparent="1" />','<widget name="desc2" position="215,470" size="860,42" zPosition="4" font="Regular;18" foregroundColor="#8fbad0" transparent="1" />','<widget name="status" position="170,535" size="940,42" zPosition="4" font="Regular;18" foregroundColor="#6fdcff" transparent="1" />']
        else:w=['<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />','<widget name="section" position="108,230" size="1350,60" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />','<widget name="subtitle" position="108,307" size="1650,46" zPosition="4" font="Regular;26" foregroundColor="#b9d7e8" transparent="1" />','<widget name="row1" position="255,430" size="1410,76" zPosition="4" font="Regular;43" foregroundColor="#fff" transparent="1" />','<widget name="desc1" position="325,510" size="1290,56" zPosition="4" font="Regular;27" foregroundColor="#8fbad0" transparent="1" />','<widget name="row2" position="255,625" size="1410,76" zPosition="4" font="Regular;43" foregroundColor="#fff" transparent="1" />','<widget name="desc2" position="325,705" size="1290,56" zPosition="4" font="Regular;27" foregroundColor="#8fbad0" transparent="1" />','<widget name="status" position="255,805" size="1410,58" zPosition="4" font="Regular;27" foregroundColor="#6fdcff" transparent="1" />']
        w.extend(_bottom_widgets(self.hd));w.extend(p._system_header_widgets(self.hd));self.skin='<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>'%(self.w,self.h,''.join(w));Screen.__init__(self,session);self['bg']=p.Pixmap();self['version']=Label('');p._setup_system_header(self);self['section']=Label('AKTUALIZÁCIA');self['subtitle']=Label('Vyber, čo chceš aktualizovať.');self['row1']=Label('');self['desc1']=Label('Stiahne chýbajúce alebo zmenené picony podľa tvojich nastavení.');self['row2']=Label('');self['desc2']=Label('Skontroluje novú verziu PiconHubu a bezpečne ju nainštaluje.');self['status']=Label('');self.refresh();self['actions']=ActionMap(['OkCancelActions','DirectionActions','ColorActions'],{'ok':self.open,'green':self.open,'cancel':self.close,'red':self.close,'up':lambda:self.sel(0),'down':lambda:self.sel(1),'yellow':lambda:self.direct(0),'blue':lambda:self.direct(1)},-1);self.timer=eTimer();self.timer.callback.append(self.poll);self.onLayoutFinish.append(self.ready)
    def ready(self):
        try:self['bg'].instance.setPixmapFromFile(p.os.path.join(p.ASSET_PATH,'missing_%s_base.jpg'%('hd' if self.hd else 'fhd')))
        except Exception:pass
    def refresh(self):self['row1'].setText(('>  ' if self.selected==0 else '   ')+'AKTUALIZOVAŤ PICONY');self['row2'].setText(('>  ' if self.selected==1 else '   ')+'AKTUALIZOVAŤ PLUGIN')
    def sel(self,i):self.selected=i;self.refresh()
    def direct(self,i):
        if not self.checking:self.sel(i);self.open()
    def open(self):
        if self.checking:return
        if self.selected==0:self.session.open(p.PiconHubUpdateScreen);return
        self.checking=True;self['status'].setText('Kontrolujem dostupnú verziu...');self._check_done=False
        def worker():
            try:self._check_result=pu.PiconHubPluginUpdater().check()
            except Exception as e:self._check_error=e
            self._check_done=True
        Thread(target=worker).start();self.timer.start(100,True)
    def poll(self):
        if not self._check_done:self.timer.start(100,True);return
        self.checking=False;self['status'].setText('')
        if self._check_error:
            from .update_status_patch import _show_error;_show_error(self,self._check_error);return
        r=self._check_result or {}
        if not r.get('available'):
            from .update_status_patch import _show_latest;_show_latest(self,r);return
        self.pending=r.get('manifest');self.session.openWithCallback(self.confirmed,PluginUpdateConfirm,r)
    def confirmed(self,a):
        if a and self.pending:self.session.open(um.PluginProgress,self.pending)

um.UpdateMenu=PrettyUpdateMenu
p.PiconHubUpdateMenu=PrettyUpdateMenu
