import zoneinfo, datetime as dt
SKIP = {'AQ', 'UA', 'CN', 'UM'}  # Antártida (estações), Ucrânia e China (fuso oficial único), ilhas sem moradores
NOME = {
 'Australia/Sydney':'Sydney','Australia/Brisbane':'Brisbane','Australia/Adelaide':'Adelaide','Australia/Darwin':'Darwin','Australia/Perth':'Perth','Australia/Eucla':'Eucla','Australia/Lord_Howe':'Ilha Lord Howe','Antarctica/Macquarie':'Ilha Macquarie',
 'America/Sao_Paulo':'Brasília','America/Manaus':'Manaus','America/Rio_Branco':'Rio Branco','America/Noronha':'Fernando de Noronha',
 'America/Toronto':'Ottawa e Toronto','America/Vancouver':'Vancouver','America/Edmonton':'Edmonton','America/Winnipeg':'Winnipeg','America/Halifax':'Halifax','America/St_Johns':'St. John’s','America/Regina':'Regina','America/Atikokan':'Atikokan','America/Blanc-Sablon':'Blanc-Sablon','America/Whitehorse':'Whitehorse',
 'Africa/Kinshasa':'Kinshasa','Africa/Lubumbashi':'Lubumbashi',
 'America/Santiago':'Santiago','America/Punta_Arenas':'Punta Arenas','Pacific/Easter':'Ilha de Páscoa',
 'America/Guayaquil':'Quito e Guayaquil','Pacific/Galapagos':'Galápagos',
 'Europe/Madrid':'Madri','Atlantic/Canary':'Ilhas Canárias',
 'Pacific/Chuuk':'Chuuk','Pacific/Pohnpei':'Palikir (Pohnpei)',
 'America/Nuuk':'Nuuk','America/Danmarkshavn':'Danmarkshavn','America/Thule':'Pituffik','America/Scoresbysund':'Ittoqqortoormiit',
 'Asia/Jakarta':'Jacarta','Asia/Makassar':'Macassar e Bali','Asia/Jayapura':'Jayapura',
 'Pacific/Tarawa':'Tarawa','Pacific/Kanton':'Ilha Kanton','Pacific/Kiritimati':'Kiritimati',
 'Asia/Ulaanbaatar':'Ulan Bator','Asia/Hovd':'Hovd',
 'America/Mexico_City':'Cidade do México','America/Cancun':'Cancún','America/Tijuana':'Tijuana','America/Mazatlan':'Mazatlán','America/Ciudad_Juarez':'Ciudad Juárez','America/Matamoros':'Matamoros','America/Hermosillo':'Hermosillo',
 'Pacific/Auckland':'Wellington e Auckland','Pacific/Chatham':'Ilhas Chatham',
 'Pacific/Tahiti':'Papeete (Taiti)','Pacific/Marquesas':'Ilhas Marquesas','Pacific/Gambier':'Ilhas Gambier',
 'Pacific/Port_Moresby':'Port Moresby','Pacific/Bougainville':'Bougainville',
 'Europe/Lisbon':'Lisboa','Atlantic/Azores':'Açores','Atlantic/Madeira':'Madeira',
 'Europe/Kaliningrad':'Kaliningrado','Europe/Moscow':'Moscou','Europe/Samara':'Samara','Asia/Yekaterinburg':'Iecaterimburgo','Asia/Omsk':'Omsk','Asia/Novosibirsk':'Novosibirsk','Asia/Irkutsk':'Irkutsk','Asia/Yakutsk':'Iakutsk','Asia/Vladivostok':'Vladivostok','Asia/Magadan':'Magadan','Asia/Kamchatka':'Petropavlovsk-Kamtchatski',
 'America/New_York':'Washington e Nova York','America/Chicago':'Chicago','America/Denver':'Denver','America/Phoenix':'Phoenix','America/Los_Angeles':'Los Angeles','America/Anchorage':'Anchorage (Alasca)','Pacific/Honolulu':'Honolulu (Havaí)',
}
TAB = {}
for line in open('/usr/share/zoneinfo/zone.tab'):
    if line.startswith('#'): continue
    c, _, z = line.split('\t')[:3]; TAB.setdefault(c, []).append(z.strip())
def off(z, m): return zoneinfo.ZoneInfo(z).utcoffset(dt.datetime(2026, m, 15)).total_seconds()
def groups(k, cap):
    if k in SKIP: return None
    g = {}
    for z in TAB.get(k, []): g.setdefault(min(off(z, 1), off(z, 7)), []).append(z)
    if len(g) < 2: return None
    out = []
    for key, zs in sorted(g.items()):
        rep = cap if cap in zs else next((z for z in zs if z in NOME), zs[0])
        out.append([rep, NOME.get(rep, rep.split('/')[-1].replace('_', ' '))])
    return out
