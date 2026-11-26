import json,os,glob,re
K=json.load(open('kids.json'))
C={c['cca2']:c for c in json.load(open('/tmp/npmt/node_modules/world-countries/countries.json'))}
ST=json.load(open('stats/stats.json'))
OFF=json.load(open('stats/official.json'))['v']
OIL=json.load(open('stats/oil.json'))['v']
FBM=json.load(open('fb/map.json'))
FB={}
for f in sorted(glob.glob('fb/out/*.json')): FB.update(json.load(open(f)))
LEFT=set('GB IE IN PK BD LK NP BT JP TH MY SG ID BN TL AU NZ PG FJ SB TO WS TV KI NR ZA NA BW ZW ZM MW MZ TZ KE UG LS SZ MU SC JM BB TT BS AG DM GD KN LC VC GY SR MV CY MT HK MO VG VI AI KY MS TC BM FK IM JE GG SH CK NU NF TK CX CC PN'.split())
for o in K['C']:
    c=C[o['k']]; sub=c.get('subregion','')
    if c['region']=='Americas': o['ct']='as' if sub=='South America' else ('ac' if sub in ('Central America','Caribbean') else 'an')
    o['cur']=list(c.get('currencies',{}).keys())
    idd=c.get('idd',{}); suf=idd.get('suffixes') or []
    o['idd']=(idd.get('root','')+(suf[0] if len(suf)==1 else '')) if idd.get('root') else None
    o['tld']=(c.get('tld') or [None])[0]
    o['drive']='l' if o['k'] in LEFT else ('r' if o['k']!='AQ' else None)
    o['units']={'US':'sistema americano (milhas, libras, °F)','LR':'sistema americano (milhas, libras, °F)','MM':'métrico e medidas tradicionais birmanesas','GB':'métrico, com milhas nas estradas'}.get(o['k'],'métrico (metro, quilo, litro, °C)')
    o['s']=ST.get(o['k'],o.get('s',{}))
    _of=OFF.get(o['k'],{})
    o['s']={kk:v for kk,v in o['s'].items() if kk not in ('pop','popY','gdp','gdpY','gpc','life','age','hdi')}
    o['s'].update(_of)
    o['s'].update(OIL.get(o['k'],{}))
    if o['s'].get('pop') and o.get('a'): o['s']['den']=round(o['s']['pop']/o['a'],1)
    f=FB.get(o['k'])
    if f: o['f']={k:v for k,v in f.items() if v not in (None,[],'',{})}
    import html as H
    fbf=json.load(open(FBM[o['k']])) if o['k'] in FBM else {}
    an=fbf.get('Government',{}).get('National anthem(s)',{}) if isinstance(fbf.get('Government',{}).get('National anthem(s)'),dict) else {}
    nm=H.unescape((an.get('title',{}) or {}).get('text','')) if isinstance(an.get('title'),dict) else ''
    lm=H.unescape((an.get('lyrics/music',{}) or {}).get('text','')) if isinstance(an.get('lyrics/music'),dict) else ''
    if nm:
        mm=re.match(r'^\s*"([^"]+)"',nm)
        o.setdefault('f',{})['hino']={'n':mm.group(1) if mm else nm.split('(')[0].strip(),'m':(lm.split('/')[-1].strip().title() if lm else None)}
    for k in ('nome_pt',): o.get('f',{}).pop(k,None)
print({k:C[k]['subregion'] for k in ['MX','GT','CU','US','PA']})
# artigos
A=json.load(open('photos/articles.json'))
from kiddata import SPREADS
from spreads_pt import S as SPT
def grp(p):
    p=int(p)
    if p<12: return 'tema'
    if p<=28: return 'an'
    if p<=32: return 'ac'
    if p<=42: return 'as'
    if p<=54: return 'af'
    if p<=82: return 'eu'
    if p<=108: return 'ai'
    return 'oc'
order={'tema':0,'as':1,'ac':2,'an':3,'af':4,'eu':5,'ai':6,'oc':7}
ARTS=[]
for p,a in A.items():
    if not a['items'] and not a['intro']: continue
    t=SPT.get(p,(a.get('t') or p,))[0]
    cc=SPREADS.get(p,'').split()
    for it in a['items']:
        if it.get('t') and '200 mil' in it['t'] and p=='038': it['ed']='Nota da edição: o livro usa um número antigo. No Censo de 2022, do IBGE, cerca de 1,7 milhão de pessoas se declararam indígenas no Brasil.'
    ed='Nota da edição: o texto original exagera ao dizer que “a maioria” vive na pobreza. Segundo o IBGE, em 2023 cerca de 27% da população brasileira estava abaixo da linha de pobreza: muita gente, mas não a maioria.' if p=='038' else None
    ARTS.append({'ed':ed,'p':p,'t':t,'g':grp(p),'intro':a['intro'],'items':a['items'],'c':cc})
ARTS.sort(key=lambda a:(order[a['g']],a['p']))
for o in K['C']: o.pop('p',None)
for a in ARTS:
    for k in a['c']:
        o=next((x for x in K['C'] if x['k']==k),None)
        if o is not None: o.setdefault('p',[]).append(a['p'])
# revisões (viés colonial)
RV={}
for f in sorted(glob.glob('rev/out/f*.json')): RV.update(json.load(open(f)))
for o in K['C']:
    if o['k'] in RV:
        r={k:v for k,v in RV[o['k']].items() if k not in ('nome','regiao') and v not in (None,'',[],{})}
        keep={k:o.get('f',{}).get(k) for k in ('hino',) if o.get('f',{}).get(k) and not r.get(k)}
        o['f']={**r,**keep}
RA={}
for f in sorted(glob.glob('rev/out/a*.json')):
    for a in json.load(open(f)): RA[a['p']]=a
for a in ARTS:
    r=RA.get(a['p'])
    if not r: continue
    if r.get('t'): a['t']=r['t']
    if r.get('intro'): a['intro']=r['intro']
    if r.get('ed'): a['ed']=r['ed']
    byi={x['i']:x for x in r.get('items',[])}
    j=0
    for idx,it in enumerate(a['items']):
        x=byi.get(idx)
        if x:
            if x.get('h') is not None: it['h']=x['h']
            if x.get('t') is not None: it['t']=x['t']
            if x.get('ed'): it['ed']=x['ed']
if os.path.exists('rev/out/linguas.json'):
    LG=json.load(open('rev/out/linguas.json'))
    for o in K['C']:
        if LG.get(o['k']): o['lg']=LG[o['k']]
def _cr(s):
    if not isinstance(s,str): return s
    for a,b in (('Unknown','Desconhecido'),('Traditional','Tradicional'),(' And ',' e '),('Arranged By','arranjo de'),('Adapted By','adaptação de')): s=s.replace(a,b)
    return s
for o in K['C']:
    h=(o.get('f') or {}).get('hino')
    if isinstance(h,dict):
        for k in h: h[k]=_cr(h[k])
def _np(x):
    if isinstance(x,str): return re.sub(r'\s*\((veja|ver)\s+pp?\.\s*[\d–-]+\)','',x)
    if isinstance(x,list): return [_np(y) for y in x]
    if isinstance(x,dict): return {k:_np(v) for k,v in x.items()}
    return x
ARTS[:]=_np(ARTS)
TZ=json.load(open('stats/tz.json')); TZ.get('CN',[0,0])[1:2]=[1]
for o in K['C']:
    if o['k'] in TZ and o['k']!='AQ': o['tz']=TZ[o['k']]
# ícones
from icons import PROD,DISH,pick
OM=set()
for o in K['C']:
    f=o.get('f') or {}
    for k in ('exporta','agricultura'):
        if f.get(k): f[k]=[[x,pick(x,PROD,'1F4E6')] for x in f[k]]
        for x in f.get(k,[]) or []: OM.add(x[1])
    for p in f.get('pratos',[]) or []:
        p['i']=pick(p.get('nome'),DISH,None) or pick(p.get('desc'),DISH,'1F37D'); OM.add(p['i'])
import re as _re
K['OM']={h:_re.sub(r'<\?xml[^>]*>|<!--.*?-->','',open(f'/tmp/om/package/color/svg/{h}.svg').read(),flags=_re.S).strip() for h in OM}
R=json.load(open('stats/brl.json'))
# --- redação própria (rw/out) e fotos livres (photos2) ---
RW={}
for f in sorted(glob.glob('rw/out/r*.json')):
    for x in json.load(open(f)): RW[x['p']]=x
PM=json.load(open('photos2/meta.json')) if os.path.exists('photos2/meta.json') else {}
LICN={4:'CC BY 2.0',5:'CC BY-SA 2.0',7:'sem restrições conhecidas',8:'governo dos EUA, domínio público',9:'CC0',10:'domínio público'}
for a in ARTS:
    r=RW.get(a['p'])
    if not r: continue
    a['t']=r.get('t') or a['t']; a['intro']=r.get('intro',''); a['ed']=r.get('ed')
    its=[]
    for i,x in enumerate(r['items']):
        it={'h':x.get('h'),'t':x.get('t'),'c':x.get('c') or []}
        if x.get('ed'): it['ed']=x['ed']
        m=PM.get(f"{a['p']}_{i}")
        if m:
            lic=m['lic']; lic={'Public domain':'domínio público','No restrictions':'sem restrições'}.get(lic,lic)
            it.update(img=m['img'],iw=m['iw'],ih=m['ih'],cr=f"Foto: {m['user'] or 'autor desconhecido'} · {lic} · Wikimedia Commons",src=m.get('page'))
        its.append(it)
    a['items']=its
    a['c']=sorted({c for it in its for c in it['c']} | set(a.get('c') or []))
for o in K['C']: o.pop('p',None)
for a in ARTS:
    for k in a['c']:
        o=next((x for x in K['C'] if x['k']==k),None)
        if o is not None: o.setdefault('p',[]).append(a['p'])
# --- reescrita independente (rw2) ---
for f in sorted(glob.glob('rw2/out/j*.json')):
    for j in json.load(open(f)):
        a=next((x for x in ARTS if x['p']==j['p']),None)
        if not a: continue
        if j['i']==-1: a['intro']=j['texto']
        elif j['i']<len(a['items']):
            a['items'][j['i']]['t']=j['texto']
            if j.get('h'): a['items'][j['i']]['h']=j['h']
# --- destaques revisados ---
HL={}
for f in sorted(glob.glob('hl/out/h*.json')): HL.update(json.load(open(f)))
for o in K['C']:
    h=HL.get(o['k'])
    if h and o.get('f'):
        for kk in ('patrimonio','simbolos','recursos'):
            if kk in h: o['f'][kk]=h[kk]
# --- checagem de fatos (fc) ---
FC={}
for f in sorted(glob.glob('fc/out/c*.json')): FC.update(json.load(open(f)))
for o in K['C']:
    c=FC.get(o['k'])
    if not c: continue
    for kk,v in c.items():
        if kk.startswith('_') or kk=='nome': continue
        if kk=='capital': o['cap']=v if isinstance(v,list) else [v]
        elif o.get('f') is not None: o['f'][kk]=v
# --- decisões editoriais (nov/2026) ---
_C={o['k']:o for o in K['C']}
_C['AF']['f']['hino']={'n':'Dā də bātorāno kor ("Esta é a casa dos bravos")','m':'canto sem instrumentos (nasheed), de autoria desconhecida'}
_C['AF']['f']['hino_nota']='Usado pelo governo talibã desde que voltou ao poder, em 2021. Esse governo não ocupa a vaga do Afeganistão na ONU. O hino anterior, "Milli Surood", valeu de 2006 a 2021.'
_C['AF'].pop('an',None)
_C['IL']['capn']='Israel declara Jerusalém sua capital, mas a ONU não reconhece: para a ONU, o status da cidade deve ser decidido em negociação entre israelenses e palestinos (Resolução 478 do Conselho de Segurança, 1980). Por isso, quase todas as embaixadas ficam em Tel Aviv.'
_C['PS']['capn']='A Palestina declara Jerusalém Oriental sua capital; a ONU considera Jerusalém Oriental território ocupado por Israel desde 1967. O governo palestino funciona em Ramallah.'
_C['IE']['f']['independencia']='21 de janeiro de 1919, quando o parlamento irlandês (Dáil Éireann) aprovou a Declaração de Independência. O Estado Livre Irlandês, separado do Reino Unido, nasceu em 6 de dezembro de 1922, e o país virou república em 1949.'
# --- seção Em foco (curadoria) ---
FO={}
for f in sorted(glob.glob('foco/out*.json')): FO.update(json.load(open(f)))
FOCO_PEND=FO
# --- mapas desenhados ---
HM=json.load(open('hand/legend.json')) if os.path.exists('hand/legend.json') else {}
K['ECO']=HM.get('_eco',[])
for o in K['C']:
    if o['k'] in HM and os.path.exists(f"hand/{o['k']}.webp"): o['hm']=HM[o['k']]
# ids próprios (sem números de página de livro) e limpeza de menções a livro
import unicodedata as _ud
def _slug(t): return re.sub(r'[^a-z0-9]+','-',_ud.normalize('NFKD',t.lower()).encode('ascii','ignore').decode()).strip('-')
SL={}
for a in ARTS:
    s=_slug(a['t']); b=s; n=2
    while s in SL.values(): s=f'{b}-{n}'; n+=1
    SL[a['p']]=s
for a in ARTS:
    a['p']=SL[a['p']]
    for it in a['items']:
        if it.get('ed') and re.search(r'\blivro\b|texto original|original', it['ed'], re.I): it.pop('ed')
    if a.get('ed') and re.search(r'\blivro\b|texto original|original', a['ed'], re.I): a['ed']=None
for o in K['C']:
    if o.get('p'): o['p']=[SL.get(x,x) for x in o['p']]
# Em foco (versão 2: itens próprios por país)
F2={}
for f in sorted(glob.glob('foco2/out/b*.json')):
    c=f.replace('/out/','/chk/')
    F2.update(json.load(open(c if os.path.exists(c) else f)))
_PM=json.load(open('photos2/meta.json')) if os.path.exists('photos2/meta.json') else {}
for _f in glob.glob('photos2/meta_foco_*.json'): _PM.update(json.load(open(_f)))
_PM={kk:vv for kk,vv in _PM.items() if isinstance(vv,dict)}
_AP={a['p']:a for a in ARTS}
def _credit(m):
    lic=m['lic']; lic={'Public domain':'domínio público','No restrictions':'sem restrições'}.get(lic,lic)
    return f"Foto: {m['user'] or 'autor desconhecido'} · {lic} · Wikimedia Commons"
for o in K['C']:
    L=[]
    for n,it in enumerate(F2.get(o['k'],[])):
        if it.get('usar'):
            p,i=it['usar'].split(':'); a=_AP.get(p)
            if not a or int(i)>=len(a['items']): continue
            base=dict(a['items'][int(i)]); base.pop('c',None)
            if it.get('h'): base['h']=it['h']
            if it.get('t'): base['t']=it['t']
            L.append(base)
        else:
            x={'h':it.get('h'),'t':it.get('t')}
            m=_PM.get(f"foco_{o['k']}_{n}")
            if m and m.get('lic')!='GFDL': x.update(img=m['img'],iw=m['iw'],ih=m['ih'],cr=_credit(m),src=m.get('page'))
            L.append(x)
    if L: o['foco']=L[:5]
    else: o.pop('foco',None)
_FX=json.load(open('foco_fix.json'))
for o in K['C']:
    if not o.get('foco'): continue
    nl=[]
    for it in o['foco']:
        key=o['k']+'|'+it.get('h','')
        if key in _FX:
            v=_FX.pop(key)
            if v is None: continue
            it=dict(it); it.update(v)
        nl.append(it)
    o['foco']=nl
if _FX: print('FIX NAO APLICADOS:',list(_FX))
K['ARTS']=ARTS; K['RATES']={'date':R['date'],'brl':R['brl']}
REC=json.load(open('anth/rec.json')) if os.path.exists('anth/rec.json') else {}
REC.pop('NG',None)  # gravação é do hino antigo (1978–2024)
_EX={}
for _f in 'abc': _EX.update(json.load(open(f'expr/{_f}.json')))
for o in K['C']:
    if o['k'] in _EX: o['ex']=_EX[o['k']]
from tzgroups import groups as _tzg
for o in K['C']:
    g=_tzg(o['k'], (o.get('tz') or [None])[0])
    if g: o['tzs']=g
for _a in K['ARTS']:
    if _a.get('p')=='gente-do-planeta':
        _i=next(i for i,x in enumerate(_a['items']) if x['h']=='Línguas de muita gente')
        _a['items'][_i+1:_i+1]=[
         {'h':'Mais de 7 mil línguas','t':'Hoje se falam no mundo pouco mais de 7 mil línguas, mas a maioria tem poucos falantes: só 23 idiomas, somados, são a língua de mais da metade da humanidade. O campeão de variedade é a Papua-Nova Guiné, onde menos de 10 milhões de pessoas falam cerca de 840 línguas. Já houve mais. Quando os portugueses chegaram, calcula-se que se falassem no Brasil mais de mil línguas indígenas; o Censo de 2022 contou 295. No mundo, cerca de 4 em cada 10 línguas correm risco de desaparecer, porque as crianças já não as aprendem em casa.','c':['PG','BR']},
         {'h':'Iguais e diferentes','t':'Quando povos se encontram, trocam palavras, músicas, comidas e invenções, e todos saem mais ricos dessa troca. Mas, se o mundo inteiro passasse a falar, comer e viver do mesmo jeito, ele ficaria mais pobre, porque cada língua guarda uma maneira própria de ver as coisas. Hoje, com viagens, televisão e internet, as mesmas línguas e os mesmos produtos chegam a toda parte, e aprender uma língua falada por muita gente abre portas. Isso não apaga tudo: muitas famílias falam uma língua em casa e outra na escola; das misturas nascem jeitos novos de falar, como os crioulos de Cabo Verde e do Haiti; e povos que quase perderam a sua língua voltam a ensiná-la às crianças, como os maoris na Nova Zelândia e os galeses no País de Gales.','c':['CV','HT','NZ','GB']}]
    if _a.get('p')=='gente-do-planeta': _a['intro']='Há pouco mais de um século, a humanidade era quatro vezes menor do que hoje. Esse crescimento não foi igual em toda parte. Na Europa, no Japão e, mais recentemente, na China, nascem poucas crianças e a população envelhece; em boa parte da África, as famílias são maiores e a maioria das pessoas é jovem: a idade mediana fica perto de 20 anos, contra mais de 40 na Europa. A riqueza também se distribui de modo desigual, e quem vive num país rico usa, em média, muito mais energia e recursos do que quem vive num país pobre. As razões são muitas, da geografia e do clima à história e às escolhas de cada governo, e o quadro muda: em poucas décadas, a China tirou centenas de milhões de pessoas da pobreza extrema.'
K['REC']=REC
K.pop('SP',None)
json.dump(K,open('kids2.json','w'),ensure_ascii=False)
print(len(K['C']),'arts',len(ARTS),'with f',sum(1 for o in K['C'] if o.get('f')),len(json.dumps(K))//1000,'KB')
