# -*- coding: utf-8 -*-
from __future__ import print_function

import os
from threading import Thread
from time import localtime, strftime

from enigma import eTimer

from . import plugin as p


def _local_latest_cached_path(row, index):
    """Main screen previews must never block GUI on network I/O."""
    filename = str((row or {}).get('_file') or '').strip()
    settings = p.load_settings()
    target = settings.get('target_dir', p.DEFAULTS['target_dir'])
    if filename:
        local_path = os.path.join(target, filename)
        if os.path.isfile(local_path):
            return local_path

    safe = p.re.sub(r'[^A-Za-z0-9_.-]+', '_', filename or ('latest_%d.png' % index))
    cache = os.path.join('/tmp', 'piconhub_main_latest_%s' % safe)
    return cache if os.path.isfile(cache) else ''


def _async_database_loader(self):
    if getattr(self, '_piconhub_db_loading', False):
        return

    self._piconhub_db_loading = True
    self._piconhub_db_done = False
    self._piconhub_db_result = None
    self._piconhub_db_error = None

    try:
        self['db_lastcheck'].setText('Načítavam...')
    except Exception:
        pass

    def worker():
        try:
            settings = p.load_settings()
            target = settings.get('target_dir', p.DEFAULTS['target_dir'])
            engine = p.PiconHubStyleUpdateEngine(settings, timeout=4)
            catalog = engine._fetch_json(settings.get('catalog_url') or p.DEFAULT_CATALOG_URL)

            result = {
                'database_version': str(catalog.get('database_version') or '').strip(),
                'latest_rows': p._latest_rows_from_catalog(engine, catalog),
                'news_rows': p._news_rows_from_catalog(engine, catalog),
                'lastcheck': strftime('%d.%m.%Y %H:%M', localtime()),
                'total': 0,
                'installed': 0,
                'missing': 0,
                'updates': 0,
                'percent': 0.0,
            }

            scan = p.scan_summary(target)
            services = list((scan.get('services') or {}).values())
            clean = []
            seen = set()
            for row in services:
                name = (row.get('name') or '').strip()
                ref = (row.get('service_reference') or '').strip()
                if not name or not ref or ref in seen:
                    continue
                parts = ref.split(':')
                if len(parts) < 7 or parts[0] != '1' or parts[1] != '0':
                    continue
                try:
                    stype = int(parts[2], 16)
                except Exception:
                    continue
                if stype not in (1, 4, 5, 17, 19, 22, 25, 31):
                    continue
                seen.add(ref)
                clean.append(row)

            total = len(clean)
            installed = 0
            for row in clean:
                picon = row.get('picon') or ''
                if picon and os.path.isfile(os.path.join(target, picon)):
                    installed += 1

            result['total'] = total
            result['installed'] = installed
            result['missing'] = max(0, total - installed)
            result['percent'] = (100.0 * installed / total) if total else 0.0

            try:
                plan = engine.plan()
                result['updates'] = int(plan.get('download_count', 0) or 0)
            except Exception as e:
                print('[PiconHub] async database update-count error:', e)

            self._piconhub_db_result = result
        except Exception as e:
            self._piconhub_db_error = str(e)
        self._piconhub_db_done = True

    def poll():
        if not getattr(self, '_piconhub_db_done', False):
            try:
                self._piconhub_db_poll.start(100, True)
            except Exception:
                pass
            return

        self._piconhub_db_loading = False
        error = getattr(self, '_piconhub_db_error', None)
        result = getattr(self, '_piconhub_db_result', None) or {}

        if error:
            print('[PiconHub] async database status read error:', error)
            try:
                self['db_version'].setText('—')
                for name in ('db_lastcheck', 'db_total', 'db_available', 'db_missing', 'db_updates', 'db_percent'):
                    self[name].setText('—')
            except Exception:
                pass
            return

        try:
            self['db_version'].setText(result.get('database_version') or '—')
            self.latest_rows = list(result.get('latest_rows') or [])
            self.news_rows = list(result.get('news_rows') or [])
            self._updateLatestMainPicons()
            self._updateNewsRows()
            self['db_lastcheck'].setText(result.get('lastcheck') or '—')
            self['db_total'].setText(str(result.get('total', 0)))
            self['db_available'].setText(str(result.get('installed', 0)))
            self['db_missing'].setText(str(result.get('missing', 0)))
            self['db_updates'].setText(str(result.get('updates', 0)))
            self['db_percent'].setText('%.1f%%' % float(result.get('percent', 0.0)))
        except Exception as e:
            print('[PiconHub] async database UI update error:', e)

    self._piconhub_db_poll = eTimer()
    self._piconhub_db_poll.callback.append(poll)
    thread = Thread(target=worker)
    thread.daemon = True
    thread.start()
    self._piconhub_db_poll.start(100, True)


# The main screen becomes interactive immediately. Network catalog/update work is
# done in a worker thread and only the final widget updates happen in the GUI thread.
p._main_latest_cached_path = _local_latest_cached_path
p.PiconHubMain._loadDatabaseVersion = _async_database_loader
