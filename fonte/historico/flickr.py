"""Busca fotos de licença livre no Flickr (CC BY, CC BY-SA, CC0, domínio público, sem restrições conhecidas)
para cada item com 'q' nos artigos reescritos. Saída: photos2/img/*.webp e photos2/meta.json"""
import json, re, os, sys, time, glob, io, urllib.parse, subprocess
from PIL import Image
OUT = '/home/claude/dkat/photos2'; os.makedirs(OUT + '/img', exist_ok=True)
LIC = {4: 'CC BY 2.0', 5: 'CC BY-SA 2.0', 7: 'sem restrições de direitos conhecidas', 8: 'obra do governo dos EUA', 9: 'CC0', 10: 'domínio público'}
meta = json.load(open(OUT + '/meta.json')) if os.path.exists(OUT + '/meta.json') else {}

UA = 'AtlasDoMundoEdu/1.0 (educational atlas for children; contact via claude.ai)'
def get(url, binary=False):
    r = subprocess.run(['curl', '-s', '-L', '--max-time', '60', '-A', UA, url], capture_output=True)
    return r.stdout if binary else r.stdout.decode('utf-8', 'ignore')

import html as _h
def strip(x): return _h.unescape(re.sub(r'<[^>]+>', '', x or '')).strip()
def search(q):
    u = 'https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrlimit=12&prop=imageinfo&iiprop=url|extmetadata|size|mime&iiurlwidth=960&format=json&gsrsearch=' + urllib.parse.quote(q + ' filetype:bitmap')
    for _ in range(4):
        t = get(u)
        try: d = json.loads(t); break
        except Exception: time.sleep(10)
    else: return []
    pages = sorted((d.get('query') or {}).get('pages', {}).values(), key=lambda p: p.get('index', 99))
    out = []
    for p in pages:
        ii = (p.get('imageinfo') or [{}])[0]; md = ii.get('extmetadata', {})
        if ii.get('mime') not in ('image/jpeg', 'image/png', 'image/webp'): continue
        if re.search(r'map|karte|carte|mapa|flag|logo|coat of arms|diagram', p['title'], re.I): continue
        lic = strip(md.get('LicenseShortName', {}).get('value'))
        if re.search(r'fair use|non-free', lic, re.I): continue
        out.append({'id': str(p['pageid']), 'title': p['title'][5:], 'user': strip(md.get('Artist', {}).get('value'))[:80], 'lic': lic, 'url': ii.get('thumburl'), 'w': ii.get('thumbwidth', 0), 'h': ii.get('thumbheight', 0), 'page': ii.get('descriptionurl')})
    return out
def search_flickr(q):
    html = get('https://www.flickr.com/search/?text=' + urllib.parse.quote(q) + '&license=4%2C5%2C7%2C8%2C9%2C10')
    out = []
    for m in re.finditer(r'\{"_flickrModelRegistry":"photo-lite-models",(.*?)"id":"(\d+)"\}', html):
        blob = m.group(1)
        def f(k):
            mm = re.search(r'"%s":("(?:[^"\\]|\\.)*"|\d+)' % k, blob); return json.loads(mm.group(1)) if mm else None
        lic = f('license')
        if lic not in LIC: continue
        sizes = {}
        for sm in re.finditer(r'"(\w+)":\{"data":\{"displayUrl":"([^"]+)","width":(\d+),"height":(\d+)', blob):
            sizes[sm.group(1)] = (sm.group(2).replace('\\/', '/'), int(sm.group(3)), int(sm.group(4)))
        best = sizes.get('c') or sizes.get('z') or sizes.get('l')
        if not best: continue
        out.append({'id': m.group(2), 'title': f('title') or '', 'user': f('realname') or f('username') or '', 'nsid': f('ownerNsid'), 'alias': f('pathAlias'), 'lic': lic, 'url': 'https:' + best[0], 'w': best[1], 'h': best[2]})
    return out

BAD = json.load(open(OUT + '/bad.json')) if os.path.exists(OUT + '/bad.json') else {}
def pick(res):
    res = [r for r in res if r['h'] and .55 < r['w'] / r['h'] < 2.1 and not re.search(r'september 11|9/11|wtc|corpse|dead|war|attack|nude', r['title'], re.I)]
    land = [r for r in res if r['w'] >= r['h'] and r['w'] >= 600]
    return (land or res or [None])[0]

if __name__ == '__main__':
    arts = []
    for f in sorted(glob.glob('/home/claude/dkat/rw/out/r*.json')): arts += json.load(open(f))
    jobs = [(a['p'], i, it['q']) for a in arts for i, it in enumerate(a['items']) if it.get('q')]
    print(len(jobs), 'buscas')
    used = {m['id'] for m in meta.values() if m}
    for p, i, q in jobs:
        key = f'{p}_{i}'
        if key in meta and meta[key] and meta[key].get('q') == q and meta[key]['id'] not in BAD.get(key, []): continue
        if key in BAD: used |= set(BAD[key])
        w = q.split(); tries = [q]
        if len(w) > 3: tries += [' '.join(w[:3]), ' '.join(w[:2] + w[-1:]), ' '.join(w[-2:]), ' '.join(w[:2])]
        elif len(w) == 3: tries += [' '.join(w[:2]), ' '.join(w[::2])]
        res = []
        for tq in dict.fromkeys(tries):
            try: res = [r for r in search(tq) if r['id'] not in used]
            except Exception as e: print('erro', tq, e); res = []
            if res: break
            time.sleep(.4)
        r = pick(res)
        if not r:
            meta[key] = None; print(key, 'sem resultado:', q, flush=True); continue
        b = b''
        for _ in range(5):
            b = get(r['url'], True)
            if len(b) > 2000: break
            time.sleep(15)
        try: im = Image.open(io.BytesIO(b)).convert('RGB')
        except Exception: meta[key] = None; continue
        im.thumbnail((900, 900)); im.save(f'{OUT}/img/{key}.webp', 'WEBP', quality=72)
        r.update(q=q, iw=im.width, ih=im.height, img=key); meta[key] = r; used.add(r['id'])
        print(time.strftime('%H:%M:%S'), key, r['lic'], '|', r['title'][:50], flush=True)
        json.dump(meta, open(OUT + '/meta.json', 'w'), ensure_ascii=False)
        time.sleep(4)
    json.dump(meta, open(OUT + '/meta.json', 'w'), ensure_ascii=False)
