#!/usr/bin/env python3
"""Download all Castlemania product images from Cloudinary to the repo.
Run on your machine:  python tools/download_images.py
Saves originals to castlemania-site/img/originals/<slug>.<ext>"""
import json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'castlemania-site', 'img', 'originals')
os.makedirs(DEST, exist_ok=True)
DATA = json.load(open(os.path.join(ROOT, 'tools', 'site_data.json'), encoding='utf-8'))

BASE = 'https://bouncycastlenetwork-res.cloudinary.com/image/upload/'
EXT = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp'}

ok = fail = 0
for p in DATA['products']:
    slug = p['path'].split('/')[-1][:-5]
    iid = p['img'].split('/')[-1]
    url = BASE + iid  # no transformation = original quality
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            ext = EXT.get(r.headers.get('Content-Type', '').split(';')[0], '.jpg')
        out = os.path.join(DEST, slug + ext)
        with open(out, 'wb') as f:
            f.write(body)
        print(f'ok   {slug}{ext}  {len(body)//1024} KB')
        ok += 1
    except Exception as e:
        print(f'FAIL {slug}: {e}')
        fail += 1
print(f'\n{ok} downloaded, {fail} failed -> {DEST}')
