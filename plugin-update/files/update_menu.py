# -*- coding: utf-8 -*-
from __future__ import print_function
import hashlib, os, shutil, time
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ProgressBar import ProgressBar
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import eTimer, getDesktop
from . import plugin as p
from .plugin_updater import PiconHubPluginUpdater, PiconHubPluginUpdateError, RELEASE_VERSION, _safe_relative_path, _ALLOWED_UPDATE_PREFIX, _restart_gui

class UpdateMenu(Screen):
 def __init__(self,session):
  self.session=session
  try: self.w=getDesktop(0).size().width(); self.h=getDesktop(0).size().height()
  except Exception: self.w,self.h=1920,1080
  self.hd=self.w<=1280
  if self.hd: widgets=['<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />','<widget name="section" position="72,153" size="700,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />','<widget name="list" position="170,270" size="940,180" zPosition="4" font="Regular;27" itemHeight="65" transparent="1" />']
  else: widgets=['<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />','<widget name="section" position="108,230" size="1000,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />','<widget name="list" position="260,405" size="1400,270" zPosition="4" font="Regular;40" itemHeight="95" transparent="1" />']
  widgets.extend(p._system_header_widgets(self.hd)); self.skin='<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>'%(self.w,self.h,''.join(widgets))
  Screen.__init__(self,session); self['bg']=p.Pixmap(); self['version']=Label(''); p._setup_system_header(self); self['section']=Label('↻  AKTUALIZOVAŤ'); self['list']=MenuList(['AKTUALIZOVAŤ PICONY','AKTUALIZOVAŤ PLUGIN'])
  self['actions']=ActionMap(['OkCancelActions','DirectionActions','ColorActions'],{'ok':self.open,'green':self.open,'cancel':self.close,'red':self.close,'up':self['list'].up,'down':self['list'].down},-1); self.onLayoutFinish.append(self.ready)
 def ready(self):
  try: self['bg'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH,'missing_%s_base.jpg'%('hd' if self.hd else 'fhd')))
  except Exception: pass
 def open(self):
  try: idx=self['list'].getSelectedIndex()
  except Exception: idx=0
  if idx==0: self.session.open(p.PiconHubUpdateScreen); return
  try: result=PiconHubPluginUpdater(timeout=6).check()
  except Exception as e: self.session.open(MessageBox,'Kontrola aktualizácie zlyhala:\n\n%s'%e,MessageBox.TYPE_ERROR,timeout=12); return
  if not result.get('available'): self.session.open(MessageBox,'PiconHub %s\n\nPoužívaš najnovšiu dostupnú verziu.'%RELEASE_VERSION,MessageBox.TYPE_INFO,timeout=9); return
  self.pending=result.get('manifest'); text='Aktuálna verzia: %s\nNová verzia: %s\n\n%s\n\nPo aktualizácii sa Enigma2 GUI automaticky reštartuje.\nPokračovať?'%(result.get('current_version'),result.get('remote_version'),result.get('notes') or '')
  self.session.openWithCallback(self.confirmed,MessageBox,text,MessageBox.TYPE_YESNO,default=True)
 def confirmed(self,answer):
  if answer and getattr(self,'pending',None): self.session.open(PluginProgress,self.pending)

class PluginProgress(Screen):
 def __init__(self,session,manifest):
  self.session=session; self.manifest=manifest; self.up=PiconHubPluginUpdater(timeout=8); self.stage='download'; self.index=0; self.prepared=[]; self.changed=[]; self.backup='/tmp/piconhub-plugin-backup-%d'%int(time.time()); self.countdown=3
  try: self.w=getDesktop(0).size().width(); self.h=getDesktop(0).size().height()
  except Exception: self.w,self.h=1920,1080
  self.hd=self.w<=1280
  if self.hd: widgets=['<widget name="bg" position="0,0" size="1280,720" zPosition="0" alphatest="blend" />','<widget name="section" position="72,153" size="800,38" zPosition="4" font="Regular;28" foregroundColor="#6fdcff" transparent="1" />','<widget name="phase" position="170,290" size="940,55" zPosition="4" font="Regular;27" foregroundColor="#ffffff" transparent="1" halign="center" />','<widget name="progress" position="220,380" size="840,30" zPosition="4" borderWidth="2" borderColor="#6fdcff" />','<widget name="info" position="170,435" size="940,100" zPosition="4" font="Regular;20" foregroundColor="#dbefff" transparent="1" halign="center" />']
  else: widgets=['<widget name="bg" position="0,0" size="1920,1080" zPosition="0" alphatest="blend" />','<widget name="section" position="108,230" size="1100,55" zPosition="4" font="Regular;40" foregroundColor="#6fdcff" transparent="1" />','<widget name="phase" position="260,435" size="1400,80" zPosition="4" font="Regular;40" foregroundColor="#ffffff" transparent="1" halign="center" />','<widget name="progress" position="330,570" size="1260,44" zPosition="4" borderWidth="2" borderColor="#6fdcff" />','<widget name="info" position="260,650" size="1400,150" zPosition="4" font="Regular;29" foregroundColor="#dbefff" transparent="1" halign="center" />']
  widgets.extend(p._system_header_widgets(self.hd)); self.skin='<screen position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>'%(self.w,self.h,''.join(widgets))
  Screen.__init__(self,session); self['bg']=p.Pixmap(); self['version']=Label(''); p._setup_system_header(self); self['section']=Label('⬇  AKTUALIZÁCIA PICONHUBU'); self['phase']=Label('Pripravujem...'); self['progress']=ProgressBar(); self['progress'].setRange((0,100)); self['info']=Label('Po dokončení sa Enigma2 GUI automaticky reštartuje.'); self['actions']=ActionMap(['OkCancelActions'],{'ok':self.ignore,'cancel':self.ignore},-1); self.timer=eTimer(); self.timer.callback.append(self.step); self.onLayoutFinish.append(self.start)
 def ignore(self): return
 def start(self):
  try: self['bg'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH,'missing_%s_base.jpg'%('hd' if self.hd else 'fhd')))
  except Exception: pass
  try: os.makedirs(self.backup)
  except Exception: pass
  self.files=self.manifest.get('files') or []; self.timer.start(100,True)
 def pct(self,done,total,base=0,span=100): return base+int((float(done)/max(1,total))*span)
 def step(self):
  try:
   total=len(self.files)
   if self.stage=='download':
    if self.index>=total: self.stage='install'; self.index=0; self.timer.start(80,True); return
    item=self.files[self.index]; rel=_safe_relative_path(item.get('path')); url=str(item.get('url') or ''); digest=str(item.get('sha256') or '').lower()
    if not url.startswith(_ALLOWED_UPDATE_PREFIX) or len(digest)!=64: raise PiconHubPluginUpdateError('Neplatný update manifest pre %s.'%rel)
    self['phase'].setText('SŤAHUJEM A OVERUJEM SHA-256'); self['info'].setText(rel); data=self.up._fetch(url)
    if hashlib.sha256(data).hexdigest().lower()!=digest: raise PiconHubPluginUpdateError('SHA-256 nesúhlasí pre %s.'%rel)
    self.prepared.append((rel,data)); self.index+=1; self['progress'].setValue(self.pct(self.index,total,0,60)); self.timer.start(60,True); return
   if self.stage=='install':
    if self.index>=total: self.finish(); return
    rel,data=self.prepared[self.index]; target=os.path.join(self.up.plugin_path,rel); parent=os.path.dirname(target)
    if not os.path.isdir(parent): os.makedirs(parent)
    backup=os.path.join(self.backup,rel)
    if os.path.exists(target):
     bdir=os.path.dirname(backup)
     if not os.path.isdir(bdir): os.makedirs(bdir)
     shutil.copy2(target,backup)
    tmp=target+'.piconhub-update'; f=open(tmp,'wb'); f.write(data); f.flush()
    try: os.fsync(f.fileno())
    except Exception: pass
    f.close(); os.rename(tmp,target); self.changed.append((target,backup if os.path.exists(backup) else None)); self.index+=1; self['phase'].setText('INŠTALUJEM'); self['info'].setText(rel); self['progress'].setValue(self.pct(self.index,total,60,40)); self.timer.start(60,True)
  except Exception as e: self.rollback(e)
 def rollback(self,error):
  for target,backup in reversed(self.changed):
   try:
    if backup: shutil.copy2(backup,target)
    elif os.path.exists(target): os.remove(target)
   except Exception: pass
  self['phase'].setText('AKTUALIZÁCIA ZLYHALA'); self['info'].setText('%s\nGUI sa nereštartuje.'%error)
 def finish(self):
  self['progress'].setValue(100); self['phase'].setText('AKTUALIZÁCIA DOKONČENÁ'); self['info'].setText('Nová verzia je nainštalovaná.\nEnigma2 GUI sa reštartuje za 3 sekundy.'); self.timer.callback.remove(self.step); self.timer.callback.append(self.tick); self.timer.start(1000,True)
 def tick(self):
  self.countdown-=1
  if self.countdown<=0: self['info'].setText('Reštartujem Enigma2 GUI...'); _restart_gui(self.session); return
  self['info'].setText('Nová verzia je nainštalovaná.\nEnigma2 GUI sa reštartuje za %d sekundy.'%self.countdown); self.timer.start(1000,True)

_old_quick=p.PiconHubMain.quickUpdate
def quick_menu(self): self.session.open(UpdateMenu)
p.PiconHubMain.quickUpdate=quick_menu
p.PiconHubUpdateMenu=UpdateMenu
