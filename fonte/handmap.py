"""Mapas 'desenhados à mão' de cada país: relevo, águas, ecossistemas (zonas climáticas), cidades.
Fontes: Natural Earth (domínio público), relevo sombreado Natural Earth (via basemap-data), grade Köppen-Geiger 0,5° (koppen-climate-lookup).
Saída: hand/{ISO}.webp e hand/legend.json
"""
import json, math, random, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import shape, box, Polygon, MultiPolygon, LineString, MultiLineString, Point
from shapely.ops import unary_union
from shapely import affinity
from shapely.prepared import prep
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
NE = '/tmp/geo/ne/'
OUT = '/home/claude/dkat/hand'
os.makedirs(OUT, exist_ok=True)
FONT = '/tmp/geo/pkgs/ph/package/files/patrick-hand-latin-400-normal.ttf'
S = 2  # supersampling

def feats(f): return json.load(open(NE + f + '.geojson'))['features']

# ---------- dados globais ----------
K = json.load(open('/home/claude/dkat/kids2.json'))
NAMES = {o['k']: o['n'] for o in K['C']}
CAPS = {o['k']: (o['cap'] or [None])[0] for o in K['C']}
WC = {c['cca2']: c for c in json.load(open('/tmp/npmt/node_modules/world-countries/countries.json'))}

ADM = feats('ne_10m_admin_0_countries')
ADMG = []
for f in ADM:
    p = f['properties']
    iso = p['ISO_A2'] if p['ISO_A2'] not in ('-99', None) else p['ISO_A2_EH']
    ADMG.append((iso, shape(f['geometry']).buffer(0), p.get('NAME_PT') or p['NAME']))
LAND = [shape(f['geometry']) for f in feats('ne_10m_land')]
LAKES = [(shape(f['geometry']), f['properties']) for f in feats('ne_10m_lakes')]
RIVERS = [(shape(f['geometry']), f['properties']) for f in feats('ne_10m_rivers_lake_centerlines')]
REG = [(shape(f['geometry']).buffer(0), f['properties']) for f in feats('ne_10m_geography_regions_polys')]
MAR = [(shape(f['geometry']).buffer(0), f['properties']) for f in feats('ne_10m_geography_marine_polys')]
ELEV = [(shape(f['geometry']), f['properties']) for f in feats('ne_10m_geography_regions_elevation_points')]
PLACES = [(shape(f['geometry']), f['properties']) for f in feats('ne_10m_populated_places_simple')]
GLAC = [shape(f['geometry']).buffer(0) for f in feats('ne_10m_glaciated_areas')]
RTR = json.load(open('/home/claude/dkat/hand_names.json')) if os.path.exists('/home/claude/dkat/hand_names.json') else {}

sr = np.asarray(Image.open('/tmp/geo/pkgs/mpl_toolkits/basemap_data/shadedrelief.jpg').convert('L'), dtype=np.float32)
HS = (sr - ndimage.gaussian_filter(sr, 8)).astype(np.float32)  # detalhe do relevo
del sr
KOP = np.load('/tmp/geo/kop.npy'); KCLS = json.load(open('/tmp/geo/kopcls.json'))

ECO = [  # (id, nome, cor, classes)
 ('fu', 'floresta tropical úmida', (86, 145, 84), ['Af', 'Am']),
 ('sv', 'savana e cerrado', (184, 192, 104), ['Aw', 'As']),
 ('sa', 'semiárido e estepe', (214, 190, 128), ['BSh', 'BSk']),
 ('de', 'deserto', (236, 214, 158), ['BWh', 'BWk']),
 ('me', 'matas e campos mediterrâneos', (165, 172, 104), ['Csa', 'Csb', 'Csc']),
 ('st', 'florestas e campos subtropicais', (132, 178, 104), ['Cfa', 'Cwa']),
 ('ft', 'floresta temperada e de altitude', (118, 165, 118), ['Cfb', 'Cfc', 'Cwb', 'Cwc']),
 ('fm', 'floresta mista de clima frio', (104, 150, 126), ['Dfa', 'Dfb', 'Dsa', 'Dsb', 'Dwa', 'Dwb']),
 ('ta', 'taiga (floresta boreal)', (84, 124, 108), ['Dfc', 'Dfd', 'Dsc', 'Dsd', 'Dwc', 'Dwd']),
 ('tu', 'tundra e alta montanha', (186, 180, 166), ['ET']),
 ('ge', 'gelo permanente', (246, 247, 248), ['EF']),
]
K2E = np.zeros(len(KCLS) + 1, dtype=np.uint8)
for i, e in enumerate(ECO):
    for c in e[3]:
        if c in KCLS: K2E[KCLS.index(c) + 1] = i + 1
EG = K2E[KOP]  # 0 = mar
ECOL = np.array([(200, 200, 200)] + [e[2] for e in ECO], dtype=np.float32)

# ---------- utilidades ----------
def norm_lon(g, shift):
    return affinity.translate(g, 360, 0) if shift and g.bounds[2] < 0 else g

def polys(g):
    return list(g.geoms) if hasattr(g, 'geoms') else [g]

def wobble(pts, amp, seed):
    """desloca levemente os pontos de uma linha (traço à mão)"""
    if len(pts) < 3: return pts
    rnd = random.Random(seed); ph = [rnd.random() * 6.28 for _ in range(4)]
    out = []; acc = 0
    for i, (x, y) in enumerate(pts):
        if i: acc += math.hypot(x - pts[i - 1][0], y - pts[i - 1][1])
        dx = amp * (math.sin(acc / 37 + ph[0]) * .6 + math.sin(acc / 13 + ph[1]) * .4)
        dy = amp * (math.sin(acc / 41 + ph[2]) * .6 + math.sin(acc / 11 + ph[3]) * .4)
        out.append((x + dx, y + dy))
    return out

def densify(pts, step):
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for j in range(n): out.append((x0 + (x1 - x0) * j / n, y0 + (y1 - y0) * j / n))
    out.append(pts[-1]); return out

def noise(h, w, seed, scales=((8, .5), (32, .3), (128, .2))):
    rnd = np.random.default_rng(seed); n = np.zeros((h, w), np.float32)
    for sc, wt in scales:
        a = rnd.random((max(2, h // sc + 2), max(2, w // sc + 2))).astype(np.float32)
        n += wt * np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
    return n

def nice(x):
    e = 10 ** math.floor(math.log10(x)); f = x / e
    return (1 if f < 1.5 else 2 if f < 3.5 else 5 if f < 7.5 else 10) * e

# ---------- um país ----------
def country_geom(k):
    gs = [g for iso, g, _ in ADMG if iso == k]
    if gs: return unary_union(gs)
    c = WC.get(k)
    if not c or not c.get('latlng'): return None
    la, lo = c['latlng']; b = box(lo - 2.5, la - 2.5, lo + 2.5, la + 2.5)
    parts = [p for iso, g, _ in ADMG for p in polys(g) if p.intersects(b)]
    parts = [p for p in parts if p.centroid.distance(Point(lo, la)) < 3]
    return unary_union(parts) if parts else None

def render(k):
    g = country_geom(k)
    if g is None or g.is_empty: return None
    ps = polys(g)
    shift = (g.bounds[2] - g.bounds[0]) > 180
    ps = [norm_lon(p, shift) for p in ps]
    tot = sum(p.area for p in ps); big = max(ps, key=lambda p: p.area)
    keep = [p for p in ps if p.distance(big) < 8 or p.area >= .25 * big.area]
    if k == 'US': keep = [p for p in ps if p.area >= .01 * tot]
    cg = unary_union(keep)
    x0, y0, x1, y1 = cg.bounds
    w, h = x1 - x0, y1 - y0
    mid = (y0 + y1) / 2; cosm = max(.25, math.cos(math.radians(mid)))
    mn = 1.2
    if w * cosm < mn: x0 -= (mn / cosm - w) / 2; x1 += (mn / cosm - w) / 2
    if h < mn: y0 -= (mn - h) / 2; y1 += (mn - h) / 2
    w, h = x1 - x0, y1 - y0
    pad = .12; x0 -= w * pad; x1 += w * pad; y0 -= h * pad; y1 += h * pad
    w, h = x1 - x0, y1 - y0
    ar = w * cosm / h
    if ar > 1.7: d = (w * cosm / 1.7 - h); y0 -= d / 2; y1 += d / 2
    elif ar < .75: d = (h * .75 / cosm - w); x0 -= d / 2; x1 += d / 2
    y0, y1 = max(y0, -85), min(y1, 85)
    w, h = x1 - x0, y1 - y0
    ar = w * cosm / h
    WF = 900 if ar >= 1 else int(round(720 * ar)); HF = int(round(WF / ar))
    if HF > 720: HF = 720; WF = int(round(HF * ar))
    W, H = WF * S, HF * S
    sx = W / w

    def P(lon, lat): return ((lon - x0) * sx, (y1 - lat) * sx / cosm)
    def ring(c): return [P(x, y) for x, y in c]
    view = box(x0, y0, x1, y1)
    vb = view.buffer(max(w, h) * .05)

    # grade lon/lat de cada pixel
    lon = x0 + (np.arange(W) + .5) / sx; lat = y1 - (np.arange(H) + .5) / (sx / cosm)
    LO, LA = np.meshgrid(((lon + 180) % 360) - 180, lat)

    # máscaras
    def mask(geoms, buf=0):
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        for gg in geoms:
            for p in polys(gg):
                if p.is_empty or not hasattr(p, 'exterior'): continue
                d.polygon(ring(p.exterior.coords), fill=255)
                for r in p.interiors: d.polygon(ring(r.coords), fill=0)
        return np.asarray(im, np.float32) / 255
    near = lambda gs: [norm_lon(p, shift).intersection(vb) for gg in gs for p in polys(gg) if norm_lon(p, shift).intersects(vb)]
    NEARLAND = near(LAND)
    land = mask(NEARLAND)
    cm = mask([cg])
    others = [(iso, norm_lon(gg, shift) if not shift else unary_union([norm_lon(p, shift) for p in polys(gg)]), nm) for iso, gg, nm in ADMG]
    others = [(iso, gg, nm) for iso, gg, nm in others if gg.intersects(vb) and iso != k]
    lakes = [(norm_lon(gg, shift).intersection(vb), p) for gg, p in LAKES if norm_lon(gg, shift).intersects(vb)]
    lm = mask([l for l, _ in lakes])
    glac = mask(near(GLAC))
    land = np.clip(land - lm, 0, 1); cm = np.clip(cm - lm, 0, 1)

    # relevo
    rx = ((LO + 180) / 360 * 10800 - .5); ry = ((90 - LA) / 180 * 5400 - .5)
    hs = ndimage.map_coordinates(HS, [ry, rx], order=1, mode='wrap')
    zoom = 10800 / 360 / (sx / S)  # px fonte por px final
    hs = ndimage.gaussian_filter(hs, max(0, S * .6 / max(zoom, .05) * .15))
    fz = float(np.clip(zoom / .6, .12, 1))
    shade = np.clip(1 + hs / 70 * fz, .72, 1.22)

    # ecossistemas
    gy = np.clip(((90 - LA) / .5).astype(int), 0, 359); gx = np.clip(((LO + 180) / .5).astype(int), 0, 719)
    eg = EG.copy()
    sub = eg[max(0, gy.min() - 3):gy.max() + 4, :]
    # preenche mar com a classe terrestre mais próxima (evita cor de mar nas bordas)
    full = EG.copy(); m0 = full == 0
    idx = ndimage.distance_transform_edt(m0, return_distances=False, return_indices=True)
    full = full[idx[0], idx[1]]
    # cor contínua: interpola cores da grade
    fy = (90 - LA) / .5 - .5; fx = (LO + 180) / .5 - .5
    jit = (noise(H, W, hash(k) % 999, ((6, .6), (24, .4))) - .5) * 1.6
    cols = np.zeros((H, W, 3), np.float32)
    cg_ = ECOL[full]
    for c in range(3): cols[..., c] = ndimage.map_coordinates(cg_[..., c], [fy + jit, fx + jit * .8], order=1, mode='wrap')
    eco_id = full[np.clip(np.round(fy).astype(int), 0, 359), np.clip(np.round(fx).astype(int), 0, 719) % 720]

    # papel
    pn = noise(H, W, 7)
    paper = np.stack([np.full((H, W), c, np.float32) for c in (244, 236, 216)], -1) * (0.94 + .1 * pn[..., None])
    img = paper.copy()
    # mar
    lab_, nlab = ndimage.label(land + lm > .5)
    sizes = ndimage.sum(np.ones_like(lab_), lab_, range(1, nlab + 1)) if nlab else []
    bigland = np.isin(lab_, [i + 1 for i, sz in enumerate(sizes) if sz > 900 * S * S]) if nlab else (land > .5)
    dist = ndimage.distance_transform_edt(~bigland)
    sea = np.array([170, 205, 222], np.float32)
    seaf = np.clip(dist / (60 * S), 0, 1)[..., None]
    seac = sea * (1 - .12 * (1 - seaf)) * (0.95 + .08 * pn[..., None])
    img = img * .25 + seac * .75
    for d0, a in ((5 * S, .45), (11 * S, .3), (19 * S, .18)):
        rip = np.clip(1 - np.abs(dist - d0) / (.9 * S), 0, 1) * a
        img = img * (1 - rip[..., None]) + np.array([96, 140, 165], np.float32) * rip[..., None]
    # terras vizinhas
    oth = np.array([228, 222, 206], np.float32) * (.96 + .06 * pn[..., None])
    oth = oth * (1 + (shade[..., None] - 1) * .7)
    img = img * (1 - land[..., None]) + oth * land[..., None]
    # país: aquarela
    tex = noise(H, W, 11, ((3, .4), (12, .35), (48, .25)))
    eco = cols * (0.9 + .18 * tex[..., None]) * shade[..., None]
    er = ndimage.binary_erosion(cm > .5, iterations=3 * S)
    edge = np.clip((cm > .5).astype(np.float32) - ndimage.gaussian_filter(er.astype(np.float32), 2 * S), 0, 1)
    eco = eco * (1 - .22 * edge[..., None])
    img = img * (1 - cm[..., None]) + eco * cm[..., None]
    # pontilhado nos desertos
    dz = np.isin(eco_id, [i + 1 for i, e in enumerate(ECO) if e[0] in ('de',)]) & (cm > .5)
    dots = (np.random.default_rng(3).random((H, W)) < .012) & dz
    img[dots] = img[dots] * .78
    # gelo
    gl = glac * land
    img = img * (1 - gl[..., None] * .8) + np.array([248, 250, 252], np.float32) * shade[..., None] * gl[..., None] * .8
    # lagos
    lakec = np.array([150, 192, 214], np.float32) * (.96 + .06 * pn[..., None])
    img = img * (1 - lm[..., None]) + lakec * lm[..., None]

    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, 'RGBA')
    seed = sum(map(ord, k))
    span = max(w * cosm, h)
    def line(coords, col, wd, amp=1.0, sd=0):
        pts = densify(coords, 6 * S)
        pts = wobble(pts, amp * S, seed + sd)
        d.line(pts, fill=col, width=max(1, int(wd)), joint='curve')

    # rios
    rlim = 12 if span < 4 else 10 if span < 10 else 8 if span < 25 else 6 if span < 50 else 4
    rivlabels = []
    for gg, p in RIVERS:
        if p.get('scalerank', 99) > rlim: continue
        gg = norm_lon(gg, shift)
        if not gg.intersects(vb): continue
        cl = gg.intersection(vb)
        wd = S * (2.6 if p['scalerank'] <= 2 else 2 if p['scalerank'] <= 5 else 1.4)
        for ln in polys(cl):
            if ln.geom_type != 'LineString' or len(ln.coords) < 2: continue
            line(ring(ln.coords), (70, 125, 170, 235), wd, .6, int(ln.length * 100))
        if p.get('name') and cg.intersects(gg): rivlabels.append((gg.intersection(cg), p))
    # contornos de lagos e costas
    for l, p in lakes:
        for pp in polys(l):
            if hasattr(pp, 'exterior'): line(ring(pp.exterior.coords), (70, 125, 170, 200), S * 1.1, .4)
    for p in NEARLAND:
        for pp in polys(p):
            if hasattr(pp, 'exterior') and pp.exterior.length > 0: line(ring(pp.exterior.coords), (95, 80, 60, 210), S * 1.2, .5)
    # fronteiras vizinhas
    for iso, gg, nm in others:
        for pp in polys(gg.intersection(vb)):
            if hasattr(pp, 'exterior'):
                pts = wobble(densify(ring(pp.exterior.coords), 6 * S), .5 * S, seed)
                for i in range(0, len(pts) - 2, 3): d.line(pts[i:i + 3], fill=(120, 100, 80, 150), width=S)

    # montanhas
    rng = random.Random(seed)
    def mountain(x, y, s, al=1):
        hgt = s * (0.8 + .4 * rng.random()); wdt = s * (1.1 + .3 * rng.random())
        a, b, c = (x - wdt / 2, y), (x + rng.uniform(-.1, .1) * wdt, y - hgt), (x + wdt / 2, y)
        d.polygon([b, c, (x + wdt * .05, y)], fill=(110, 85, 60, int(70 * al)))
        d.line([a, b, c], fill=(90, 66, 45, int(230 * al)), width=max(1, int(S * 1.2)), joint='curve')
        d.line([b, (b[0] - wdt * .12, b[1] + hgt * .35)], fill=(255, 255, 255, int(160 * al)), width=S)
    LAB = []  # (prioridade, texto, x, y, tamanho, cor, estilo)
    msz = 13 * S
    REGL = []
    for gg, p in REG:
        fc = p['FEATURECLA']
        gg2 = norm_lon(gg, shift)
        if not gg2.intersects(view): continue
        inter = gg2.intersection(view)
        apx = inter.area * sx * sx / cosm
        if fc == 'Range/mtn' and apx > (msz * 2.2) ** 2 and span > 4:
            step = msz * (2.1 if span > 12 else 2.8)
            bx0, by0, bx1, by1 = inter.bounds
            yy = by1
            while yy > by0:
                xx = bx0 + rng.random() * step / sx
                while xx < bx1:
                    q = Point(xx + rng.uniform(-.3, .3) * step / sx, yy)
                    if inter.contains(q):
                        X, Y = P(q.x, q.y)
                        if 0 < X < W and 0 < Y < H and land[int(min(Y, H - 1)), int(min(X, W - 1))] > .5:
                            inc = cm[int(min(Y, H - 1)), int(min(X, W - 1))] > .5
                            if inc or rng.random() < .45: mountain(X, Y, msz if inc else msz * .8, 1 if inc else .35)
                    xx += step / sx
                yy -= step / sx * cosm * .85
        nm = RTR.get(p['NAME'], p.get('NAME_PT') or p['NAME'])
        if fc in ('Range/mtn', 'Desert', 'Plateau', 'Plain', 'Basin', 'Lowland', 'Wetlands', 'Delta', 'Tundra', 'Valley', 'Depression') and apx > (60 * S) ** 2 and inter.intersects(cg):
            rp = inter.representative_point(); X, Y = P(rp.x, rp.y)
            REGL.append((3 + p.get('SCALERANK', 5) * .1 - min(apx / (W * H), .5), nm.upper() if fc != 'Range/mtn' else nm, X, Y, 15 * S, (110, 80, 50), 'sp'))
    LAB += sorted(REGL)[:4]
    # picos
    pc2 = prep(cg.buffer(.05))
    peaks = [(gg, p) for gg, p in ELEV if p['featurecla'] == 'mountain' and p.get('elevation') and pc2.contains(norm_lon(gg, shift))]
    peaks.sort(key=lambda t: -t[1]['elevation'])
    for gg, p in peaks[:2]:
        gg = norm_lon(gg, shift); X, Y = P(gg.x, gg.y)
        d.polygon([(X, Y - 7 * S), (X - 6 * S, Y + 4 * S), (X + 6 * S, Y + 4 * S)], fill=(150, 70, 50, 255))
        nm = RTR.get(p['name'], p.get('name_pt') or p['name'])
        LAB.append((1.5, nm, X + 9 * S, Y, 14 * S, (130, 60, 40), 'l'))
    # rios: rótulos (os maiores)
    rivlabels.sort(key=lambda t: t[1]['scalerank'])
    seen = set()
    for gg, p in rivlabels[:4]:
        nm = p['name']
        if nm in seen or gg.is_empty: continue
        seen.add(nm)
        ls = max(polys(gg), key=lambda x: x.length) if hasattr(gg, 'geoms') else gg
        if ls.length * sx < 120 * S: continue
        q = ls.interpolate(.5, normalized=True); X, Y = P(q.x, q.y)
        LAB.append((2.5, 'rio ' + RTR.get(nm, nm), X, Y - 8 * S, 14 * S, (50, 100, 150), 'c'))
    # mares
    for gg, p in MAR:
        gg2 = norm_lon(gg, shift)
        if not gg2.intersects(view) or p['featurecla'] in ('river', 'lagoon', 'reef'): continue
        inter = gg2.intersection(view)
        if inter.area * sx * sx / cosm < (90 * S) ** 2: continue
        rp = inter.representative_point(); X, Y = P(rp.x, rp.y)
        if land[int(min(Y, H - 1)), int(min(X, W - 1))] > .5: continue
        nm = RTR.get(p['name'], p.get('name_pt') or p['name'])
        LAB.append((4 + p.get('scalerank', 5) * .05, nm, X, Y, 16 * S, (60, 110, 145), 'c'))
    # países vizinhos
    for iso, gg, nm in others:
        inter = gg.intersection(view)
        if inter.area * sx * sx / cosm < (70 * S) ** 2: continue
        rp = max(polys(inter), key=lambda x: x.area).representative_point(); X, Y = P(rp.x, rp.y)
        LAB.append((5, NAMES.get(iso, nm).upper(), X, Y, 14 * S, (140, 125, 100), 'sp'))
    # cidades
    cgb = cg.buffer(.15); bb = cgb.bounds

    pcg = prep(cgb)
    cities = [(gg, p) for gg, p in PLACES if p['featurecla'] not in ('Historic place', 'Meteorological Station', 'Scientific station') and (q := norm_lon(gg, shift)) and bb[0] <= q.x <= bb[2] and bb[1] <= q.y <= bb[3] and pcg.contains(q) and (p.get('iso_a2') in (k, None, '-99') or cg.buffer(.01).contains(q))]
    MARK = []
    cap = [c for c in cities if p_is_cap(c[1], k)]
    rest = sorted([c for c in cities if c not in cap], key=lambda t: -(t[1].get('pop_max') or 0))
    ncity = 2 if span < 3 else 4 if span < 10 else 6
    if k in ('IL', 'PS'): rest = cap + rest; cap = []
    for gg, p in cap[:1]:
        gg = norm_lon(gg, shift); X, Y = P(gg.x, gg.y)
        MARK.append(('s', X, Y))
        LAB.append((0, CAPS.get(k) or p['name'], X + 12 * S, Y, 19 * S, (60, 40, 30), 'lb'))
    for gg, p in rest[:ncity]:
        gg = norm_lon(gg, shift); X, Y = P(gg.x, gg.y)
        if any(math.hypot(X - c[2], Y - c[3]) < 30 * S for c in LAB if c[0] < 1): continue
        MARK.append(('c', X, Y))
        LAB.append((.5, RTR.get(p['name'], p['name']), X + 8 * S, Y, 16 * S, (60, 40, 30), 'l'))

    # contorno do país (traço duplo)
    for p in polys(cg):
        if not hasattr(p, 'exterior'): continue
        r = ring(p.exterior.coords)
        if len(r) < 3: continue
        per = sum(math.hypot(r[i+1][0]-r[i][0], r[i+1][1]-r[i][1]) for i in range(len(r)-1))
        if per > 260 * S: line(r, (150, 60, 45, 85), S * 4.5, 1.2, 1)
        line(r, (110, 40, 30, 255), S * (2 if per > 120 * S else 1.2), .7 if per > 120 * S else .3, 2)

    for t_, X, Y in MARK:
        if t_ == 's': star(d, X, Y, 9 * S)
        else: d.ellipse([X - 4 * S, Y - 4 * S, X + 4 * S, Y + 4 * S], fill=(250, 245, 235, 255), outline=(60, 40, 30, 255), width=S)
    # rótulos (com prevenção de sobreposição)
    boxes = [(X - 6 * S, Y - 6 * S, X + 6 * S, Y + 6 * S) for _, X, Y in MARK]
    fonts = {}
    def F(sz):
        if sz not in fonts: fonts[sz] = ImageFont.truetype(FONT, int(sz))
        return fonts[sz]
    used = set()
    for pr, txt, X, Y, sz, col, st in sorted(LAB, key=lambda t: t[0]):
        txt = (txt or '').strip()
        if not txt or txt.replace(' ', '').lower() in used: continue
        f = F(sz)
        if st == 'sp': txt = ' '.join(txt)
        tw = d.textlength(txt, font=f); th = sz
        if st.startswith('l'): cands = [(X, Y - th * .6, X + tw, Y + th * .5), (X - tw - 24 * S, Y - th * .6, X - 24 * S, Y + th * .5), (X - 12 * S - tw / 2, Y - th * 1.7, X - 12 * S + tw / 2, Y - th * .6), (X - 12 * S - tw / 2, Y + th * .4, X - 12 * S + tw / 2, Y + th * 1.5)]
        else: cands = [(X - tw / 2, Y - th * .6, X + tw / 2, Y + th * .5)]
        bx = None
        for c_ in cands:
            if c_[0] < 6 * S or c_[2] > W - 6 * S or c_[1] < 6 * S or c_[3] > H - 30 * S: continue
            if any(not (c_[2] < b[0] or c_[0] > b[2] or c_[3] < b[1] or c_[1] > b[3]) for b in boxes): continue
            bx = c_; break
        if bx is None: continue
        boxes.append((bx[0] - 4 * S, bx[1] - 2 * S, bx[2] + 4 * S, bx[3] + 2 * S)); used.add(txt.replace(' ', '').lower())
        xy = (bx[0], bx[1] - th * .05)
        d.text(xy, txt, font=f, fill=col + (255,), stroke_width=int(S * 2.5), stroke_fill=(250, 244, 228, 200))

    # escala e rosa dos ventos
    kmpx = 111.32 * cosm / sx
    km = nice(W * .18 * kmpx); L = km / kmpx
    bx, by = 20 * S, H - 18 * S
    d.line([(bx, by), (bx + L, by)], fill=(70, 50, 35, 255), width=2 * S)
    for t in (0, .5, 1): d.line([(bx + L * t, by - 5 * S), (bx + L * t, by + 1 * S)], fill=(70, 50, 35, 255), width=S * 2)
    d.text((bx + L + 8 * S, by - 12 * S), f"{int(km):,} km".replace(',', '.'), font=F(15 * S), fill=(70, 50, 35, 255))
    cx, cy = W - 30 * S, 34 * S
    d.polygon([(cx, cy - 20 * S), (cx - 7 * S, cy + 6 * S), (cx, cy + 1 * S)], fill=(110, 40, 30, 255))
    d.polygon([(cx, cy - 20 * S), (cx + 7 * S, cy + 6 * S), (cx, cy + 1 * S)], fill=(250, 244, 228, 255), outline=(110, 40, 30, 255))
    d.text((cx - 5 * S, cy + 7 * S), 'N', font=F(16 * S), fill=(110, 40, 30, 255))
    # moldura
    for o_, a in ((5 * S, 255), (9 * S, 140)):
        pts = wobble(densify([(o_, o_), (W - o_, o_), (W - o_, H - o_), (o_, H - o_), (o_, o_)], 8 * S), .6 * S, seed + o_)
        d.line(pts, fill=(110, 85, 60, a), width=S * (2 if o_ < 6 * S else 1))

    im = im.resize((WF, HF), Image.LANCZOS)
    im.save(f'{OUT}/{k}.webp', 'WEBP', quality=70, method=6)
    # legenda: ecossistemas presentes no país
    ids = eco_id[cm > .5]
    leg = []
    if ids.size:
        cnt = np.bincount(ids, minlength=len(ECO) + 1)
        for i, e in enumerate(ECO, 1):
            if cnt[i] / ids.size >= .03: leg.append([e[0], round(cnt[i] / ids.size * 100)])
    feats_ = {'mont': any(fc for fc in []), }
    return {'w': WF, 'h': HF, 'eco': sorted(leg, key=lambda t: -t[1]), 'gelo': bool((gl * cm).sum() > 50), 'km': int(km)}

def p_is_cap(p, k):
    return p.get('adm0cap') == 1 and (p.get('iso_a2') == k)

def star(d, x, y, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * .45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=(170, 45, 35, 255), outline=(80, 30, 20, 255))

if __name__ == '__main__':
    ks = sys.argv[1:] or [o['k'] for o in K['C']]
    res = {}
    if os.path.exists(f'{OUT}/legend.json'): res = json.load(open(f'{OUT}/legend.json'))
    from multiprocessing import Pool
    def run(k):
        try: return k, render(k)
        except Exception as ex:
            import traceback; traceback.print_exc(); return k, None
    with Pool(int(os.environ.get('NP', '4'))) as pool:
        for k, r in pool.imap_unordered(run, ks):
            if r: res[k] = r
            print(k, 'ok' if r else 'FALHOU', flush=True)
    res['_eco'] = [[e[0], e[1], '#%02x%02x%02x' % e[2]] for e in ECO]
    json.dump(res, open(f'{OUT}/legend.json', 'w'), ensure_ascii=False)
