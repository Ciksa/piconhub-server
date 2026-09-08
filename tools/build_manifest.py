#!/usr/bin/env python3
from __future__ import print_function
import argparse
import datetime
import hashlib
import json
import os
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def utc_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description='Build a PiconHub package manifest from source data and local PNG files.')
    ap.add_argument('--repo-root', default='.', help='Repository root (default: current directory)')
    ap.add_argument('--data', default='data/skylink_23.5e.json', help='Source data JSON relative to repo root')
    ap.add_argument('--output', default='skylink_23.5e.json', help='Output manifest relative to repo root')
    ap.add_argument('--fresh-timestamp', action='store_true', help='Ignore data.generated and use current UTC time')
    args = ap.parse_args()

    root = os.path.abspath(args.repo_root)
    data_path = os.path.join(root, args.data)
    out_path = os.path.join(root, args.output)
    src = load_json(data_path)

    required = ('schema', 'package', 'name', 'base_url', 'picons')
    for key in required:
        if key not in src:
            raise SystemExit('Missing required data key: %s' % key)

    base_url = src['base_url'].rstrip('/')
    generated = utc_now() if args.fresh_timestamp else src.get('generated', utc_now())
    manifest = {
        'schema': src['schema'],
        'package': src['package'],
        'name': src['name'],
        'generated': generated,
        'picons': []
    }

    seen_ref = set()
    seen_file = set()
    for idx, item in enumerate(src['picons'], 1):
        for key in ('name', 'service_reference', 'file'):
            if key not in item or not item[key]:
                raise SystemExit('Item %d missing %s' % (idx, key))
        ref = item['service_reference']
        logical_file = item['file']
        source_file = item.get('source_file', logical_file)
        if ref in seen_ref:
            raise SystemExit('Duplicate service_reference: %s' % ref)
        if logical_file in seen_file:
            raise SystemExit('Duplicate manifest file: %s' % logical_file)
        seen_ref.add(ref)
        seen_file.add(logical_file)

        png_path = os.path.join(root, 'picons', source_file)
        if not os.path.isfile(png_path):
            raise SystemExit('Missing PNG: %s' % png_path)

        manifest['picons'].append({
            'name': item['name'],
            'service_reference': ref,
            'file': logical_file,
            'sha256': sha256_file(png_path),
            'url': base_url + '/' + source_file
        })

    tmp = out_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, out_path)
    print('OK: wrote %s (%d picons)' % (out_path, len(manifest['picons'])))


if __name__ == '__main__':
    main()
