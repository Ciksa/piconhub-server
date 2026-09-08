#!/usr/bin/env python3
from __future__ import print_function
import argparse
import hashlib
import json
import os
import re
import sys

HEX64 = re.compile(r'^[0-9a-f]{64}$')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description='Validate a PiconHub package manifest.')
    ap.add_argument('--repo-root', default='.')
    ap.add_argument('--manifest', default='skylink_23.5e.json')
    args = ap.parse_args()

    root = os.path.abspath(args.repo_root)
    path = os.path.join(root, args.manifest)
    with open(path, 'r', encoding='utf-8') as f:
        m = json.load(f)

    errors = []
    for k in ('schema', 'package', 'name', 'generated', 'picons'):
        if k not in m:
            errors.append('missing top-level key: %s' % k)
    if not isinstance(m.get('picons'), list):
        errors.append('picons must be a list')

    refs, files = set(), set()
    for i, p in enumerate(m.get('picons', []), 1):
        for k in ('name', 'service_reference', 'file', 'sha256', 'url'):
            if not p.get(k):
                errors.append('item %d missing %s' % (i, k))
        if p.get('service_reference') in refs:
            errors.append('duplicate service_reference: %s' % p.get('service_reference'))
        refs.add(p.get('service_reference'))
        if p.get('file') in files:
            errors.append('duplicate file: %s' % p.get('file'))
        files.add(p.get('file'))
        if p.get('sha256') and not HEX64.match(p['sha256']):
            errors.append('invalid sha256 for %s' % p.get('name', i))

        # If URL points to this repository's /picons/ path and file exists locally,
        # verify the hash. This also supports the temporary Markiza alias test where
        # manifest file and physical source filename differ.
        url = p.get('url', '')
        marker = '/picons/'
        if marker in url:
            source_file = url.split(marker, 1)[1].split('?', 1)[0]
            local = os.path.join(root, 'picons', source_file)
            if os.path.isfile(local):
                actual = sha256_file(local)
                if actual != p.get('sha256'):
                    errors.append('sha256 mismatch: %s' % source_file)

    if errors:
        print('FAILED: %d error(s)' % len(errors))
        for e in errors:
            print(' - ' + e)
        return 1

    print('OK: %s (%d picons)' % (path, len(m.get('picons', []))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
