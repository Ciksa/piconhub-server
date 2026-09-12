from pathlib import Path
import re, hashlib, json
p=Path('plugin-update/files/update_ui.py')
s=p.read_text()

base='''def _base_widgets(hd, buttons=True):
    if hd:
        w=[
            '<widget name="bg" position="0,0" size="1280,127" zPosition="0" alphatest="blend" />',
            '<widget name="body" position="20,127" size="1240,485" zPosition="0" backgroundColor="%s" transparent="0" />' % BG,
            '<widget name="footer" position="20,612" size="1240,72" zPosition="0" backgroundColor="%s" transparent="0" />' % FOOTER,
        ]
        if buttons:
            w += [
                '<widget name="red_btn" position="38,620" size="278,56" zPosition="4" alphatest="blend" />',
                '<widget name="red_title" position="102,628" size="194,21" zPosition="6" font="Regular;18" foregroundColor="%s" transparent="1" halign="left" valign="center" />' % WHITE,
                '<widget name="red_sub" position="102,650" size="194,17" zPosition="6" font="Regular;11" foregroundColor="#d9d9d9" transparent="1" halign="left" valign="center" />',
                '<widget name="green_btn" position="347,620" size="278,56" zPosition="4" alphatest="blend" />',
                '<widget name="green_title" position="411,628" size="194,21" zPosition="6" font="Regular;15" foregroundColor="%s" transparent="1" halign="left" valign="center" />' % WHITE,
                '<widget name="green_sub" position="411,650" size="194,17" zPosition="6" font="Regular;11" foregroundColor="#d9d9d9" transparent="1" halign="left" valign="center" />',
            ]
        return w
    w=[
        '<widget name="bg" position="0,0" size="1920,190" zPosition="0" alphatest="blend" />',
        '<widget name="body" position="30,190" size="1860,728" zPosition="0" backgroundColor="%s" transparent="0" />' % BG,
        '<widget name="footer" position="30,918" size="1860,108" zPosition="0" backgroundColor="%s" transparent="0" />' % FOOTER,
    ]
    if buttons:
        w += [
            '<widget name="red_btn" position="58,930" size="416,84" zPosition="4" alphatest="blend" />',
            '<widget name="red_title" position="156,942" size="286,31" zPosition="6" font="Regular;27" foregroundColor="%s" transparent="1" halign="left" valign="center" />' % WHITE,
            '<widget name="red_sub" position="156,977" size="286,22" zPosition="6" font="Regular;16" foregroundColor="#d9d9d9" transparent="1" halign="left" valign="center" />',
            '<widget name="green_btn" position="521,930" size="416,84" zPosition="4" alphatest="blend" />',
            '<widget name="green_title" position="619,942" size="286,31" zPosition="6" font="Regular;22" foregroundColor="%s" transparent="1" halign="left" valign="center" />' % WHITE,
            '<widget name="green_sub" position="619,977" size="286,22" zPosition="6" font="Regular;16" foregroundColor="#d9d9d9" transparent="1" halign="left" valign="center" />',
        ]
    return w
'''
s,n=re.subn(r'def _base_widgets\(hd, buttons=True\):.*?(?=\ndef _common_header)',base,s,flags=re.S); assert n==1,n

init='''def _init_base(obj, session, name, widgets, buttons=True):
    all_widgets = _base_widgets(obj.hd, buttons) + _common_header(obj.hd) + list(widgets)
    all_widgets.extend(p._system_header_widgets(obj.hd))
    obj.skin = '<screen name="%s" position="0,0" size="%d,%d" flags="wfNoBorder" backgroundColor="#00000000">%s</screen>' % (name, obj.gui_w, obj.gui_h, ''.join(all_widgets))
    Screen.__init__(obj, session)
    obj['bg']=Pixmap(); obj['body']=Label(''); obj['footer']=Label(''); obj['version']=Label('')
    p._setup_system_header(obj)
    if buttons:
        obj['red_btn']=Pixmap(); obj['red_title']=Label(''); obj['red_sub']=Label('')
        obj['green_btn']=Pixmap(); obj['green_title']=Label(''); obj['green_sub']=Label('')


def _ready_base(obj):
    mode='hd' if obj.hd else 'fhd'
    try:
        obj['bg'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH,'updater_header_%s.jpg' % mode))
    except Exception as e:
        print('[PiconHub] updater header error:',e)
    try:
        if 'red_btn' in obj:
            obj['red_btn'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH,'picons_btn_red_%s.png' % mode))
            obj['green_btn'].instance.setPixmapFromFile(os.path.join(p.ASSET_PATH,'picons_btn_green_%s.png' % mode))
    except Exception as e:
        print('[PiconHub] updater button error:',e)
'''
s,n=re.subn(r'def _init_base\(obj, session, name, widgets, buttons=True\):.*?(?=\ndef _set_buttons)',init,s,flags=re.S); assert n==1,n

choice='''def _choice_widgets(hd):
    if hd:
        return [
            '<widget name="card" position="62,214" size="790,156" zPosition="1" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (PANEL,CYAN_DIM),
            '<widget name="focus" position="70,222" size="774,68" zPosition="2" backgroundColor="%s" borderWidth="1" borderColor="%s" transparent="0" />' % (PANEL_FOCUS,CYAN),
            '<widget name="list" position="88,230" size="742,126" zPosition="4" font="Regular;22" itemHeight="62" transparent="1" selectionDisabled="1" />',
            '<widget name="divider" position="880,214" size="1,330" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
            '<widget name="name" position="900,275" size="320,45" zPosition="5" font="Regular;25" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
            '<widget name="state" position="900,335" size="320,38" zPosition="5" font="Regular;20" foregroundColor="%s" transparent="1" halign="center" />' % GREEN,
            '<widget name="detail" position="890,395" size="340,105" zPosition="5" font="Regular;17" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
        ]
    return [
        '<widget name="card" position="92,322" size="1185,234" zPosition="1" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (PANEL,CYAN_DIM),
        '<widget name="focus" position="104,334" size="1161,102" zPosition="2" backgroundColor="%s" borderWidth="2" borderColor="%s" transparent="0" />' % (PANEL_FOCUS,CYAN),
        '<widget name="list" position="132,346" size="1110,190" zPosition="4" font="Regular;30" itemHeight="92" transparent="1" selectionDisabled="1" />',
        '<widget name="divider" position="1320,322" size="2,495" zPosition="2" backgroundColor="#39bff8" transparent="0" />',
        '<widget name="name" position="1365,410" size="430,65" zPosition="5" font="Regular;34" foregroundColor="%s" transparent="1" halign="center" />' % WHITE,
        '<widget name="state" position="1365,500" size="430,50" zPosition="5" font="Regular;26" foregroundColor="%s" transparent="1" halign="center" />' % GREEN,
        '<widget name="detail" position="1345,590" size="470,150" zPosition="5" font="Regular;23" foregroundColor="%s" transparent="1" halign="center" />' % TEXT,
    ]
'''
s,n=re.subn(r'def _choice_widgets\(hd\):.*?(?=\n\nclass PiconHubUpdateChoice)',choice,s,flags=re.S); assert n==1,n

cls='''class PiconHubUpdateChoice(Screen):
    def __init__(self, session):
        self.session=session; self.gui_w,self.gui_h=_desktop(); self.hd=self.gui_w<=1280
        self.checking=False; self.pending=None; self._check_done=False; self._check_result=None; self._check_error=None
        _init_base(self,session,'PiconHubUpdateChoice',_choice_widgets(self.hd),True)
        self['section']=Label('↻  AKTUALIZÁCIA'); self['summary']=Label('Vyber, čo chceš aktualizovať')
        self['card']=Label(''); self['focus']=Label(''); self['divider']=Label('')
        self['list']=MenuList(['AKTUALIZOVAŤ PICONY','AKTUALIZOVAŤ PLUGIN'])
        self['name']=Label(''); self['state']=Label(''); self['detail']=Label('')
        _set_buttons(self,'SPÄŤ','Návrat do hlavnej ponuky','OK, SPUSTIŤ AKTUALIZÁCIU','Potvrdiť vybranú aktualizáciu')
        self['actions']=ActionMap(['OkCancelActions','DirectionActions','ColorActions'],{'cancel':self.close,'red':self.close,'ok':self.open_selected,'green':self.open_selected,'up':self.up,'down':self.down},-1)
        self.poll_timer=eTimer(); self.poll_timer.callback.append(self._poll_check); self.onLayoutFinish.append(self._ready)
    def _ready(self): _ready_base(self); self._selected()
    def _index(self):
        try: return self['list'].getSelectedIndex()
        except Exception: return 0
    def _selected(self):
        idx=self._index()
        try:
            x=70 if self.hd else 104; y=(222 if idx==0 else 284) if self.hd else (334 if idx==0 else 426)
            self['focus'].instance.move(ePoint(x,y))
        except Exception: pass
        if idx==0:
            self['name'].setText('PICONY'); self['state'].setText('AKTUALIZÁCIA DATABÁZY'); self['detail'].setText('Stiahne chýbajúce alebo zmenené picony podľa tvojich nastavení.')
        else:
            self['name'].setText('PLUGIN'); self['state'].setText('AKTUALIZÁCIA PICONHUBU'); self['detail'].setText('Skontroluje novú verziu PiconHubu a bezpečne ju nainštaluje.')
    def up(self):
        if not self.checking: self['list'].up(); self._selected()
    def down(self):
        if not self.checking: self['list'].down(); self._selected()
    def open_picons(self):
        if not self.checking: self.session.open(p.PiconHubUpdateScreen)
    def open_plugin(self):
        if not self.checking: self._start_check()
    def open_selected(self):
        if self.checking: return
        self.open_picons() if self._index()==0 else self.open_plugin()
    def _start_check(self):
        self.checking=True; self._check_done=False; self._check_result=None; self._check_error=None
        self['summary'].setText('Kontrolujem dostupnú verziu...'); self['state'].setText('KONTROLA PREBIEHA'); self['detail'].setText('Kontrola GitHub manifestu beží na pozadí.')
        def worker():
            try: self._check_result=pu.PiconHubPluginUpdater(timeout=6).check()
            except Exception as e: self._check_error=str(e)
            self._check_done=True
        t=Thread(target=worker); t.daemon=True; t.start(); self.poll_timer.start(100,True)
    def _poll_check(self):
        if not self._check_done: self.poll_timer.start(100,True); return
        self.checking=False; self['summary'].setText('Vyber, čo chceš aktualizovať'); self._selected()
        if self._check_error:
            self.session.open(PiconHubUpdateStatus,'KONTROLA AKTUALIZÁCIE ZLYHALA','Nepodarilo sa overiť dostupnú verziu PiconHubu.',self._check_error,True); return
        result=self._check_result or {}
        if not result.get('available'):
            version=result.get('remote_version') or result.get('current_version') or pu.RELEASE_VERSION
            self.session.open(PiconHubUpdateStatus,'POUŽÍVAŠ NAJNOVŠIU VERZIU','PiconHub %s je aktuálny.' % version,'Nie je potrebná žiadna aktualizácia pluginu.',False); return
        self.pending=result.get('manifest'); self.session.openWithCallback(self._confirmed,PiconHubPluginConfirm,result)
    def _confirmed(self,answer):
        if answer and self.pending: self.session.open(PiconHubPluginProgress,self.pending)
'''
s,n=re.subn(r'class PiconHubUpdateChoice\(Screen\):.*?(?=\n\ndef _dialog_widgets)',cls,s,flags=re.S); assert n==1,n

p.write_text(s)
Path('plugin-update/files/release.py').write_text("# -*- coding: utf-8 -*-\n# PiconHub release version used by the GitHub self-updater.\nVERSION = '0.6.12.21'\n")

files=['release.py','update_ui.py','update_menu_patch.py','assets/updater_header_fhd.jpg','assets/updater_header_hd.jpg']
entries=[]
for rel in files:
    fp=Path('plugin-update/files')/rel
    entries.append({'path':rel,'url':'https://raw.githubusercontent.com/PiconHub-Warder/piconhub-server/main/plugin-update/files/'+rel,'sha256':hashlib.sha256(fp.read_bytes()).hexdigest()})
manifest={'schema':1,'version':'0.6.12.21','notes':'Oprava updatera: odstránené chybné statické cyan riadky a unicode ikony z 0.6.12.20. Výber je späť na stabilnom native MenuList/focus layoute, hlavička ostáva z pôvodného PiconHub grafického podkladu a spodné červené/zelené tlačidlá používajú pôvodné PiconHub button assety.','files':entries}
Path('plugin-update/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
