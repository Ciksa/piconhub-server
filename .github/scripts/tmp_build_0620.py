from pathlib import Path
import re

path = Path('plugin-update/files/update_ui.py')
s = path.read_text()

new_base = '''def _base_widgets(hd, buttons=True):
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
'''
s, n = re.subn(r'def _base_widgets\(hd, buttons=True\):.*?(?=\ndef _common_header)', new_base, s, flags=re.S)
assert n == 1, n

s = s.replace("obj['red_btn'] = Label(''); obj['red_dot'] = Label('●'); obj['red_title'] = Label(''); obj['red_sub'] = Label('')\n        obj['green_btn'] = Label(''); obj['green_dot'] = Label('●'); obj['green_title'] = Label(''); obj['green_sub'] = Label('')", "obj['red_btn'] = Label(''); obj['red_dot'] = Label('←'); obj['red_title'] = Label(''); obj['red_sub'] = Label('')\n        obj['green_btn'] = Label(''); obj['green_dot'] = Label('▶'); obj['green_title'] = Label(''); obj['green_sub'] = Label('')")
s = s.replace("os.path.join(p.ASSET_PATH, 'header_dynamic_%s.png' % mode)", "os.path.join(p.ASSET_PATH, 'updater_header_%s.jpg' % mode)")

new_choice_widgets = '''def _choice_widgets(hd):
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
'''
s, n = re.subn(r'def _choice_widgets\(hd\):.*?(?=\n\nclass PiconHubUpdateChoice)', new_choice_widgets, s, flags=re.S)
assert n == 1, n

new_choice_class = '''class PiconHubUpdateChoice(Screen):
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
'''
s, n = re.subn(r'class PiconHubUpdateChoice\(Screen\):.*?(?=\n\ndef _dialog_widgets)', new_choice_class, s, flags=re.S)
assert n == 1, n

path.write_text(s)
Path('plugin-update/files/release.py').write_text("# -*- coding: utf-8 -*-\n# PiconHub release version used by the GitHub self-updater.\nVERSION = '0.6.12.20'\n")
