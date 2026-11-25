import json,gzip,base64,os,glob,shutil
F='/tmp/npmt/node_modules/@fontsource/'
def ch(k,o): return f'<script type="application/octet-stream" id="c-{k}">'+base64.b64encode(gzip.compress(json.dumps(o,ensure_ascii=False,separators=(",",":")).encode(),9)).decode()+'</script>\n'
def ff(fam,f,w,style='normal'):
    p=F+f
    if not os.path.exists(p): return ''
    return "@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')%s}"%(fam,style,w,base64.b64encode(open(p,'rb').read()).decode(),";unicode-range:U+0100-024F,U+1E00-1EFF" if 'ext' in f else ';unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2190-21FF')
fonts=''.join(ff('Literata',f'literata/files/literata-{s}-{w}-normal.woff2',w) for w in (400,500,600,700) for s in ('latin','latin-ext'))+ff('Literata','literata/files/literata-latin-400-italic.woff2',400,'italic')
fonts+=''.join(ff('Figtree',f'figtree/files/figtree-{s}-{w}-normal.woff2',w) for w in (400,500,600,700) for s in ('latin','latin-ext'))
D=json.load(open('kids2.json')); FL=json.load(open('flags.json')); MP=json.load(open('kidmap.json'))
data=ch('d',D)+ch('f',FL)+ch('m',MP)
t=open('template2.html',encoding='utf-8').read().replace('/*__FONTS__*/',fonts)
used=sorted({i['img'] for a in D['ARTS'] for i in a['items'] if i.get('img')})
recs=sorted(D['REC'])
b64=lambda kid,p: f'<script type="application/octet-stream" id="{kid}">'+base64.b64encode(open(p,'rb').read()).decode()+'</script>\n'
HM=sorted(o['k'] for o in D['C'] if o.get('hm'))
from PIL import Image
os.makedirs('photos2/small',exist_ok=True)
for n in used:
    sp=f'photos2/small/{n}.webp'
    if not os.path.exists(sp) or os.path.getmtime(sp)<os.path.getmtime(f'photos2/img/{n}.webp'):
        im=Image.open(f'photos2/img/{n}.webp'); im.thumbnail((640,640)); im.save(sp,'WEBP',quality=60)
os.makedirs('hand/small',exist_ok=True)
def hsmall(k):
    sp=f'hand/small/{k}.webp'
    if not os.path.exists(sp) or os.path.getmtime(sp)<os.path.getmtime(f'hand/{k}.webp'):
        im=Image.open(f'hand/{k}.webp'); im.save(sp,'WEBP',quality=55)
    return sp
emb=''.join(b64('i-'+n,f'photos2/small/{n}.webp') for n in used)+''.join(b64('h-'+k,hsmall(k)) for k in HM)+''.join(b64('a-'+k,f'anth/mp3o/{k}.mp3') for k in recs)
p='/home/claude/out/Atlas do Mundo (2026) - enciclopédia ilustrada.html'
open(p,'w',encoding='utf-8').write(t.replace('/*__EMBED__*/true','true').replace('<!--__DATA__-->',data+emb))
shutil.rmtree('art2',ignore_errors=True); os.makedirs('art2/f'); os.makedirs('art2/a'); os.makedirs('art2/h')
PWA='<link rel="manifest" href="manifest.webmanifest">\n<link rel="icon" href="icon-192.png">\n<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<meta name="mobile-web-app-capable" content="yes">'
open('art2/index.html','w',encoding='utf-8').write(t.replace('/*__EMBED__*/true','false').replace('<!--__DATA__-->',data).replace('<!--__PWA__-->',PWA))
for n in ('icon-192.png','icon-512.png','maskable-192.png','maskable-512.png','apple-touch-icon.png'): shutil.copy('app_src/'+n,'art2/'+n)
json.dump({'name':'Atlas do Mundo','short_name':'Atlas do Mundo','description':'Enciclopédia ilustrada dos países do mundo, para crianças e famílias, vista a partir do Sul.','lang':'pt-BR','start_url':'./','scope':'./','display':'standalone','orientation':'any','background_color':'#f4ecd8','theme_color':'#fbfaf6','categories':['education','books','kids'],
 'icons':[{'src':'icon-192.png','sizes':'192x192','type':'image/png','purpose':'any'},{'src':'icon-512.png','sizes':'512x512','type':'image/png','purpose':'any'},{'src':'maskable-192.png','sizes':'192x192','type':'image/png','purpose':'maskable'},{'src':'maskable-512.png','sizes':'512x512','type':'image/png','purpose':'maskable'}]},open('art2/manifest.webmanifest','w'),ensure_ascii=False,indent=1)

for n in used: shutil.copy(f'photos2/img/{n}.webp',f'art2/f/{n}.webp')
HB={}
for k in HM: HB.setdefault(k[0],{})[k]=base64.b64encode(open(f'hand/{k}.webp','rb').read()).decode()
for L,v in HB.items(): json.dump(v,open(f'art2/h/{L}.json','w'))
for k in recs: shutil.copy(f'anth/mp3/{k}.mp3',f'art2/a/{k}.mp3')
import hashlib
ver=hashlib.md5(open('art2/index.html','rb').read()).hexdigest()[:10]
core=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png']+['h/'+x for x in sorted(os.listdir('art2/h'))]+['a/'+x for x in sorted(os.listdir('art2/a'))]
open('art2/sw.js','w').write(f'''const V='atlas-{ver}', CORE={json.dumps(core)};
self.addEventListener('install',e=>{{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
self.addEventListener('fetch',e=>{{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request,{{ignoreSearch:true}}).then(r=>r||fetch(e.request).then(res=>{{if(res.ok&&new URL(e.request.url).origin===location.origin){{const cp=res.clone();caches.open(V).then(c=>c.put(e.request,cp));}}return res;}}).catch(()=>caches.match('index.html'))))}});
''')
print(round(os.path.getsize(p)/1e6,1),'MB offline;',round(os.path.getsize('art2/index.html')/1e6,2),'MB index;',len(used),'fotos',len(recs),'hinos')
