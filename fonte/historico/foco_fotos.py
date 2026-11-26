"""Fotos (Wikimedia Commons) para os itens novos da seção Em foco."""
import json, glob, os, io, time, re
from PIL import Image
import flickr as F   # funções de busca no Commons
import sys
W, NW = int(sys.argv[1]), int(sys.argv[2])
MF = f'{OUT}/meta_foco_{W}.json' if False else None
OUT = '/home/claude/dkat/photos2'
meta = json.load(open(OUT + '/meta.json'))
MW = f'{OUT}/meta_foco_{W}.json'
if os.path.exists(MW): meta.update(json.load(open(MW)))
mine = {}
used = {m['id'] for m in meta.values() if isinstance(m, dict)}
for f in sorted(glob.glob('foco2/out/b*.json')):
    for k, items in json.load(open(f)).items():
        for n, it in enumerate(items):
            if it.get('usar') or not it.get('q'): continue
            key = f'foco_{k}_{n}'
            if sum(map(ord, key)) % NW != W: continue
            if key in meta and meta[key] and meta[key].get('q') == it['q']: continue
            if key in meta and meta[key] is None and meta.get(key + '_q') == it['q']: continue
            w = it['q'].split(); tries = [it['q']]
            if len(w) > 3: tries += [' '.join(w[:3]), ' '.join(w[-2:]), ' '.join(w[:2])]
            r = None
            for tq in dict.fromkeys(tries):
                res = [x for x in F.search(tq) if x['id'] not in used and x.get('user')]
                r = F.pick(res)
                if r: break
            if not r:
                meta[key] = None; meta[key + '_q'] = it['q']; print(key, 'sem foto', flush=True); continue
            b = b''
            for _ in range(5):
                b = F.get(r['url'], True)
                if len(b) > 2000: break
                time.sleep(6)
            try: im = Image.open(io.BytesIO(b)).convert('RGB')
            except Exception: meta[key] = None; continue
            im.thumbnail((900, 900)); im.save(f'{OUT}/img/{key}.webp', 'WEBP', quality=72)
            r.update(q=it['q'], iw=im.width, ih=im.height, img=key); meta[key] = r; used.add(r['id'])
            print(time.strftime('%H:%M:%S'), key, r['lic'], '|', r['title'][:50], flush=True)
            json.dump({kk: vv for kk, vv in meta.items() if kk.startswith('foco_')}, open(MW, 'w'), ensure_ascii=False)
            time.sleep(1)
json.dump({kk: vv for kk, vv in meta.items() if kk.startswith('foco_')}, open(MW, 'w'), ensure_ascii=False)
