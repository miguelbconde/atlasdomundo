"""Gera o app (pasta web/) a partir de fonte/base e fonte/midia.

Uso, na raiz do repositório:  python3 fonte/build.py
Precisa só de Python 3 e Pillow (pip install pillow).
Arquivos de web/ que não são gerados (privacidade.html, priv.html) são preservados.
"""
import json, gzip, base64, os, re, io, shutil, hashlib
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FON = os.path.join(RAIZ, 'fonte')
WEB = os.path.join(RAIZ, 'web')
B = lambda *p: os.path.join(FON, 'base', *p)
M = lambda *p: os.path.join(FON, 'midia', *p)

def ch(k, o):
    z = gzip.compress(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode(), 9, mtime=0)
    return f'<script type="application/octet-stream" id="c-{k}">' + base64.b64encode(z).decode() + '</script>\n'

def ff(fam, f, w, style='normal'):
    p = os.path.join(FON, 'fontes', f)
    if not os.path.exists(p): return ''
    rng = ';unicode-range:U+0100-024F,U+1E00-1EFF' if 'ext' in f else ';unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2190-21FF'
    return "@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')%s}" % (
        fam, style, w, base64.b64encode(open(p, 'rb').read()).decode(), rng)

fonts = ''.join(ff('Literata', f'literata-{s}-{w}-normal.woff2', w) for w in (400, 500, 600, 700) for s in ('latin', 'latin-ext'))
fonts += ff('Literata', 'literata-latin-400-italic.woff2', 400, 'italic')
fonts += ''.join(ff('Figtree', f'figtree-{s}-{w}-normal.woff2', w) for w in (400, 500, 600, 700) for s in ('latin', 'latin-ext'))

D = json.load(open(B('kids2.json'))); FL = json.load(open(B('flags.json'))); MP = json.load(open(B('kidmap.json')))
data = ch('d', D) + ch('f', FL) + ch('m', MP)
t = open(B('template.html'), encoding='utf-8').read().replace('/*__FONTS__*/', fonts)
used = sorted({i['img'] for a in D['ARTS'] for i in a['items'] if i.get('img')} |
              {i['img'] for o in D['C'] for i in (o.get('foco') or []) if isinstance(i, dict) and i.get('img')})
recs = sorted(D['REC'])
HM = sorted(o['k'] for o in D['C'] if o.get('hm'))
falta = [n for n in used if not os.path.exists(M('fotos', n + '.webp'))] + \
        [k for k in HM if not os.path.exists(M('mapas', k + '.webp'))] + \
        [k for k in recs if not os.path.exists(M('hinos', k + '.mp3'))]
if falta: raise SystemExit('Mídia faltando: ' + ', '.join(falta[:20]))

# limpa só o que é gerado
manter = {'privacidade.html', 'priv.html'}
os.makedirs(WEB, exist_ok=True)
for x in os.listdir(WEB):
    if x in manter: continue
    p = os.path.join(WEB, x)
    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
for d in ('f', 'a', 'h'): os.makedirs(os.path.join(WEB, d))

PWA = ('<link rel="manifest" href="manifest.webmanifest">\n<link rel="icon" href="icon-192.png">\n'
       '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<meta name="mobile-web-app-capable" content="yes">')
open(os.path.join(WEB, 'index.html'), 'w', encoding='utf-8').write(
    t.replace('/*__EMBED__*/true', 'false').replace('<!--__DATA__-->', data).replace('<!--__PWA__-->', PWA))
for n in ('icon-192.png', 'icon-512.png', 'maskable-192.png', 'maskable-512.png', 'apple-touch-icon.png'):
    shutil.copy(os.path.join(FON, 'icones', n), os.path.join(WEB, n))
json.dump({'name': 'Atlas do Mundo', 'short_name': 'Atlas do Mundo',
           'description': 'Enciclopédia ilustrada dos países do mundo, para crianças e famílias, vista a partir do Sul.',
           'lang': 'pt-BR', 'start_url': './', 'scope': './', 'display': 'standalone', 'orientation': 'any',
           'background_color': '#f4ecd8', 'theme_color': '#fbfaf6', 'categories': ['education', 'books', 'kids'],
           'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
                     {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
                     {'src': 'maskable-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'maskable'},
                     {'src': 'maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]},
          open(os.path.join(WEB, 'manifest.webmanifest'), 'w'), ensure_ascii=False, indent=1)

# fotos em pacotes: f/{prefixo}.json  (prefixo = nome sem o último "_xxx")
FBK = {}
for n in used:
    FBK.setdefault(re.sub(r'_[^_]*$', '', n), {})[n] = base64.b64encode(open(M('fotos', n + '.webp'), 'rb').read()).decode()
for bk, v in FBK.items(): json.dump(v, open(os.path.join(WEB, 'f', bk + '.json'), 'w'))
TL = {}
for a in D['ARTS']:
    im = next((i for i in a['items'] if i.get('img')), None)
    if im:
        x = Image.open(M('fotos', im['img'] + '.webp')); x.thumbnail((420, 420)); bf = io.BytesIO()
        x.save(bf, 'WEBP', quality=62); TL[im['img']] = base64.b64encode(bf.getvalue()).decode()
json.dump(TL, open(os.path.join(WEB, 'f', '_tiles.json'), 'w'))
HB = {}
for k in HM: HB.setdefault(k[0], {})[k] = base64.b64encode(open(M('mapas', k + '.webp'), 'rb').read()).decode()
for L, v in HB.items(): json.dump(v, open(os.path.join(WEB, 'h', L + '.json'), 'w'))
for k in recs: shutil.copy(M('hinos', k + '.mp3'), os.path.join(WEB, 'a', k + '.mp3'))

ver = hashlib.md5(open(os.path.join(WEB, 'index.html'), 'rb').read()).hexdigest()[:10]
core = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'f/_tiles.json'] + \
       ['h/' + x for x in sorted(os.listdir(os.path.join(WEB, 'h')))] + ['a/' + x for x in sorted(os.listdir(os.path.join(WEB, 'a')))]
open(os.path.join(WEB, 'sw.js'), 'w').write(f'''const V='atlas-{ver}', CORE={json.dumps(core)};
self.addEventListener('install',e=>{{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
self.addEventListener('fetch',e=>{{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request,{{ignoreSearch:true}}).then(r=>r||fetch(e.request).then(res=>{{if(res.ok&&new URL(e.request.url).origin===location.origin){{const cp=res.clone();caches.open(V).then(c=>c.put(e.request,cp));}}return res;}}).catch(()=>caches.match('index.html'))))}});
''')
print(round(os.path.getsize(os.path.join(WEB, 'index.html')) / 1e6, 2), 'MB index;', len(used), 'fotos;', len(HM), 'mapas;', len(recs), 'hinos')
