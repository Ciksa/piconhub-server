# -*- coding: utf-8 -*-
from __future__ import print_function

from Components.ActionMap import ActionMap
from . import ui_async_patch as ua
from . import update_menu as um
from . import update_status_patch as us

COLORS = ('#ff4b55', '#31df6b', '#f2c94c', '#3c9cff')


def _card(x, y, w, h, color, text, hd):
    if not text:
        return ''
    bw = 2 if hd else 3
    fs = 18 if hd else 27
    dot = 26 if hd else 38
    return ('<eLabel position="%d,%d" size="%d,%d" zPosition="9" backgroundColor="#08283a" borderWidth="%d" borderColor="%s" />'
            '<eLabel text="●" position="%d,%d" size="%d,%d" zPosition="10" font="Regular;%d" foregroundColor="%s" transparent="1" halign="center" valign="center" />'
            '<eLabel text="%s" position="%d,%d" size="%d,%d" zPosition="10" font="Regular;%d" foregroundColor="#ffffff" transparent="1" valign="center" />') % (x,y,w,h,bw,color,x+(12 if hd else 18),y+3,(44 if hd else 62),h-6,dot,color,text,x+(62 if hd else 90),y+3,w-(74 if hd else 104),h-6,fs)


def _bar(hd, labels, named=True):
    if hd:
        panel='<eLabel position="25,600" size="1230,90" zPosition="8" backgroundColor="#062d40" />'; x0,y,w,h,gap=38,612,280,62,12
    else:
        panel='<eLabel position="38,900" size="1844,135" zPosition="8" backgroundColor="#062d40" />'; x0,y,w,h,gap=58,918,416,92,18
    out=[panel]
    for i,text in enumerate(labels[:4]): out.append(_card(x0+i*(w+gap),y,w,h,COLORS[i],text,hd))
    if named:
        for name in ('back_icon','back_title','back_sub','action_icon','action_title','action_sub','help'): out.append('<widget name="%s" position="0,0" size="1,1" transparent="1" />' % name)
    return ''.join(out)


def _bottom_widgets(hd, action_title='VYBRAŤ', action_sub=''):
    labels=('SPÄŤ',action_title,'PICONY','PLUGIN') if action_title=='VYBRAŤ' else ('SPÄŤ',action_title,'','')
    return [_bar(hd,labels,True)]
ua._bottom_widgets=_bottom_widgets

_old_pretty_init=ua.PrettyUpdateMenu.__init__
def _pretty_init(self,session):
    _old_pretty_init(self,session)
    self['actions']=ActionMap(['OkCancelActions','DirectionActions','ColorActions'],{'ok':self.open_selected,'green':self.open_selected,'cancel':self.go_back,'red':self.go_back,'up':self.up,'down':self.down,'yellow':lambda:_direct(self,0),'blue':lambda:_direct(self,1)},-1)
ua.PrettyUpdateMenu.__init__=_pretty_init

def _direct(screen,index):
    if screen.checking:return
    screen.selected=index; screen._refresh_rows(); screen.open_selected()

_old_status_init=us.PluginUpdateStatus.__init__
def _status_init(self,session,title,message,detail='',error=False):
    _old_status_init(self,session,title,message,detail,error); s=self.skin
    if self.hd:
        old_panel='<eLabel position="25,600" size="1230,90" zPosition="8" backgroundColor="#062d40" />'; old_card='<eLabel position="38,612" size="280,62" zPosition="9" backgroundColor="#481018" borderWidth="2" borderColor="#ff5968" />'; repl=[('position="50,620" size="52,44"','position="0,0" size="1,1"'),('position="112,618" size="185,24"','position="0,0" size="1,1"'),('position="112,645" size="185,18"','position="0,0" size="1,1"')]
    else:
        old_panel='<eLabel position="38,900" size="1844,135" zPosition="8" backgroundColor="#062d40" />'; old_card='<eLabel position="58,918" size="416,92" zPosition="9" backgroundColor="#481018" borderWidth="3" borderColor="#ff5968" />'; repl=[('position="76,930" size="70,60"','position="0,0" size="1,1"'),('position="158,930" size="285,36"','position="0,0" size="1,1"'),('position="158,970" size="285,25"','position="0,0" size="1,1"')]
    s=s.replace(old_panel+old_card,_bar(self.hd,('SPÄŤ','','',''),False),1)
    for a,b in repl:s=s.replace(a,b)
    self.skin=s
us.PluginUpdateStatus.__init__=_status_init

_old_progress_init=um.PluginProgress.__init__
def _progress_init(self,session,manifest):
    _old_progress_init(self,session,manifest); s=self.skin; labels=('NEVYPÍNAŤ','SHA-256','ZÁLOHA','REŠTART GUI')
    if self.hd:
        s=s.replace('<eLabel position="25,600" size="1230,90" zPosition="8" backgroundColor="#062d40" />',_bar(True,labels,False),1); s=s.replace('position="65,617" size="1150,48"','position="0,0" size="1,1"')
    else:
        s=s.replace('<eLabel position="38,900" size="1844,135" zPosition="8" backgroundColor="#062d40" />',_bar(False,labels,False),1); s=s.replace('position="98,930" size="1720,68"','position="0,0" size="1,1"')
    self.skin=s
um.PluginProgress.__init__=_progress_init
