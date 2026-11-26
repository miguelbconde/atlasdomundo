"""Revisão dos números com fontes oficiais:
ONU (World Population Prospects 2024: população 2025, expectativa de vida 2023, idade mediana, crianças 0-14, mortalidade até 5 anos),
PNUD (Relatório de Desenvolvimento Humano 2025: IDH 2023, anos esperados de escola), Banco Mundial (PIB 2023)."""
import json, csv, math, re
import numpy as np, pyreadr, openpyxl, pycountry
W = '/tmp/geo/data/wpp2024/data/'
K = json.load(open('kids2.json'))
WC = {c['cca2']: c for c in json.load(open('/tmp/npmt/node_modules/world-countries/countries.json'))}
num2k = {}
for k, c in WC.items():
    if c.get('ccn3'): num2k[int(c['ccn3'])] = k
rd = lambda f: list(pyreadr.read_r(W + f + '.rda').values())[0]
# população 2025 (projeção média)
pp = rd('popproj1dt'); pp = pp[pp.year == 2025]
POP = {num2k[int(r.country_code)]: (r.popM + r.popF) * 1000 for r in pp.itertuples() if int(r.country_code) in num2k}
# idades 2023 (última estimativa)
pa = rd('popAge1dt'); pa = pa[pa.year == 2023]
AGE, KIDS = {}, {}
for cc, g in pa.groupby('country_code'):
    k = num2k.get(int(cc))
    if not k: continue
    g = g.sort_values('age'); tot = g['pop'].sum()
    if tot <= 0: continue
    cum = g['pop'].cumsum().values; ages = g['age'].values
    i = int(np.searchsorted(cum, tot / 2)); prev = cum[i - 1] if i else 0
    AGE[k] = round(float(ages[i] + (tot / 2 - prev) / g['pop'].values[i]), 1)
    KIDS[k] = round(float(g[g.age <= 14]['pop'].sum() / tot * 100), 1)
e0 = rd('e01dt'); e0 = e0[e0.year == 2023]
LIFE = {num2k[int(r.country_code)]: round(float(r.e0B), 1) for r in e0.itertuples() if int(r.country_code) in num2k}
# mortalidade até 5 anos (por mil nascidos), a partir das taxas de mortalidade por idade
mx = rd('mx1dt'); mx = mx[(mx.year == 2023) & (mx.age <= 4)]
U5 = {}
for cc, g in mx.groupby('country_code'):
    k = num2k.get(int(cc))
    if not k: continue
    s = 1.0
    for r in g.sort_values('age').itertuples():
        m = r.mxB; a = .15 if r.age == 0 else .5
        s *= 1 - m / (1 + (1 - a) * m)
    U5[k] = round((1 - s) * 1000, 1)
# IDH (PNUD 2025)
wb = openpyxl.load_workbook('/tmp/geo/data/hdr/HDR25_Statistical_Annex_Tables_1-7.xlsx', read_only=True, data_only=True)
ALIAS = {'Bolivia (Plurinational State of)': 'BO', 'Iran (Islamic Republic of)': 'IR', 'Korea (Republic of)': 'KR', "Korea (Democratic People's Rep. of)": 'KP', 'Venezuela (Bolivarian Republic of)': 'VE', 'Tanzania (United Republic of)': 'TZ', 'Moldova (Republic of)': 'MD', 'Congo (Democratic Republic of the)': 'CD', 'Congo': 'CG', "Lao People's Democratic Republic": 'LA', 'Micronesia (Federated States of)': 'FM', 'Palestine, State of': 'PS', 'Hong Kong, China (SAR)': 'HK', 'Türkiye': 'TR', 'Eswatini (Kingdom of)': 'SZ', "Côte d'Ivoire": 'CI', 'Viet Nam': 'VN', 'Russian Federation': 'RU', 'Syrian Arab Republic': 'SY', 'Cabo Verde': 'CV', 'Czechia': 'CZ', 'Brunei Darussalam': 'BN', 'Saint Kitts and Nevis': 'KN', 'Saint Lucia': 'LC', 'Saint Vincent and the Grenadines': 'VC', 'Sao Tome and Principe': 'ST', 'Timor-Leste': 'TL', 'North Macedonia': 'MK', 'Kyrgyzstan': 'KG', 'Gambia': 'GM', 'Bahamas': 'BS', 'Netherlands': 'NL', 'United States': 'US', 'United Kingdom': 'GB'}
def iso(n):
    n = n.strip()
    if n in ALIAS: return ALIAS[n]
    try: return pycountry.countries.lookup(n).alpha_2
    except LookupError:
        try: return pycountry.countries.search_fuzzy(n)[0].alpha_2
        except LookupError: return None
HDI, EYS, miss = {}, {}, []
for row in wb['Table 1. HDI'].iter_rows(min_row=8, values_only=True):
    v = [c for c in row if c is not None]
    if len(v) >= 5 and isinstance(v[0], int) and isinstance(v[1], str) and isinstance(v[2], float):
        k = iso(v[1])
        if not k: miss.append(v[1]); continue
        HDI[k] = round(v[2], 3)
        nums = [x for x in v[3:] if isinstance(x, (int, float))]
        if len(nums) >= 2: EYS[k] = round(nums[1], 1)
# PIB (Banco Mundial)
G = {}
a3 = {c['cca3']: k for k, c in WC.items()}
for r in csv.DictReader(open('/tmp/geo/data/wb_gdp.csv')):
    k = a3.get(r['Country Code'])
    if k and r['Year'] == '2023': G[k] = float(r['Value'])
P23 = {num2k[int(cc)]: g['pop'].sum() * 1000 for cc, g in pa.groupby('country_code') if int(cc) in num2k}
out = {}
for o in K['C']:
    k = o['k']; d = {}
    if k in POP: d['pop'] = int(round(POP[k])); d['popY'] = 2025
    if k in LIFE: d['life'] = LIFE[k]
    if k in AGE: d['age'] = AGE[k]
    if k in KIDS: d['kids'] = KIDS[k]
    if k in U5: d['u5'] = U5[k]
    if k in HDI: d['hdi'] = HDI[k]
    if k in EYS: d['esc'] = EYS[k]
    if k in G: d['gdp'] = G[k]; d['gdpY'] = 2023
    if k in G and k in P23: d['gpc'] = int(round(G[k] / P23[k]))
    out[k] = d
json.dump({'v': out, 'miss_hdi': miss}, open('stats/official.json', 'w'), ensure_ascii=False)
print('HDI', len(HDI), 'sem iso:', miss)
print('pop', len(POP), 'life', len(LIFE), 'u5', len(U5), 'gdp', len(G))
print(out['BR'])
