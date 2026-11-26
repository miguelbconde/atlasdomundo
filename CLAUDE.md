# Atlas do Mundo — guia de continuidade para o Claude

Leia este arquivo inteiro antes de qualquer trabalho. Ele descreve o estado do projeto em 26/11/2026 e como continuar sem perder nada.

## 1. O projeto

- **O quê:** enciclopédia ilustrada dos países para crianças de 6 a 9 anos e suas famílias, em português do Brasil. Tom de enciclopédia, não de jogo.
- **Meta:** vender como app pago na Google Play e na App Store, para celular e tablet.
- **Dono:** Miguel Conde, professor de Literatura Comparada na UFRJ. Ele não programa.
- **Como falar com ele:** em português, com clareza e sem jargão (sermo humilis). Explique o que fez em poucas linhas e mostre o texto final quando o assunto for conteúdo. Peça a ele só o que exige a conta ou a mão dele (lojas, segredos, pagamentos).
- **Segurança:** todo o trabalho roda na nuvem, nesta sessão e no GitHub. Ele desinstalou o Claude do computador em nov/2026. Não proponha passos que exijam instalar algo na máquina dele.
- **Autoria:** obra autônoma. Nenhum texto, mapa ou imagem do atlas da DK que serviu de ponto de partida. Fotos só com licença livre (Wikimedia Commons), sempre com crédito.

## 2. Começar uma sessão

```bash
# 1) adicionar o repositório à sessão (ferramenta add_repo: owner miguelbconde, repo atlasdomundo, access push) e clonar
git clone https://github.com/miguelbconde/atlasdomundo.git /home/claude/atlasdomundo
cd /home/claude/atlasdomundo
pip install pillow --break-system-packages -q
# 2) compilar e servir para teste
python3 fonte/build.py
(setsid python3 -m http.server 8765 --directory web >/dev/null 2>&1 &)
# 3) capturas de tela (se faltar: pip install playwright --break-system-packages && playwright install chromium)
python3 fonte/ferramentas/shot.py "p/BR" teste 420 900   # gera /tmp/teste.png; "ERR []" quer dizer sem erros de JavaScript
```

- O build.py **apaga e recria** web/, preservando só priv.html e privacidade.html. Depois de cada build, reinicie o servidor.
- **Rotas do app:**
  - `#p/BR` — país
  - `#r/gente-do-planeta` — artigo ou região
  - `#paises`, `#regioes`, `#numeros/<indicador>`, `#jogos`, `#jogo/<nome>`, `#creditos`
  - sem nada — mapa-múndi

## 3. Estrutura do repositório

| Caminho | O que é |
|---|---|
| `fonte/base/kids2.json` | **Base de dados canônica**: todo o texto e os números do app. Edite aqui. |
| `fonte/base/template.html` | O app inteiro (HTML, CSS e JS num arquivo só, cerca de 750 linhas). |
| `fonte/base/flags.json`, `kidmap.json` | Bandeiras (SVG) e o mapa-múndi (geometria). |
| `fonte/midia/fotos/*.webp` | Fotos usadas (1.053). O nome é a chave `img` nos dados. |
| `fonte/midia/mapas/{ISO2}.webp` | Mapas físicos desenhados de cada país (250). |
| `fonte/midia/hinos/{ISO2}.mp3` | Gravações de hinos em domínio público (36). Os demais tocam a melodia sintetizada a partir de `AN`. |
| `fonte/fontes/`, `fonte/icones/` | Fontes Literata e Figtree (woff2) e ícones do PWA. |
| `fonte/build.py` | Gera web/ a partir do que está acima. Só precisa de Python e Pillow. |
| `fonte/ferramentas/shot.py` | Captura de tela com Playwright. |
| `fonte/historico/` | Scripts e guias das fases anteriores. São referência, **não rodam mais**: dependiam de arquivos de trabalho que não estão no repositório. O resultado deles já está em kids2.json. |
| `web/` | Saída do build, que vai dentro do app. Também tem a política de privacidade (`priv.html`). |
| `android/`, `ios/`, `capacitor.config.json`, `package.json` | Capacitor 8. appId `br.com.miguelbconde.atlasdomundo`. |
| `.github/workflows/android.yml`, `ios.yml` | Compilação na nuvem: o primeiro gera o .aab; o segundo envia ao TestFlight. Disparam manualmente ou com uma tag `v*`. |
| `loja/textos/`, `loja/capturas/` | Fichas das lojas, respostas dos formulários e capturas. |
| `assets/` | Ícone e splash em alta resolução, que geram os ícones nativos. |

## 4. Como mudar o conteúdo (fluxo padrão)

1. Escreva um script curto em `fonte/edicoes/AAAA-MM-DD-assunto.py`. Ele lê `fonte/base/kids2.json`, aplica a mudança e grava de volta com `json.dump(D, open(..., 'w'), ensure_ascii=False)`. Assim fica registrado o que mudou.
2. Rode `python3 fonte/build.py`, reinicie o servidor e confira com shot.py. Leia a imagem.
3. Publique o artefato de pré-visualização (seção 7).
4. Faça commit e `git -c push.negotiate=true push origin main`.
5. Para gerar novas versões das lojas: suba `version` em package.json e `versionName` em `android/app/build.gradle`, rode `npx cap sync` se mexeu em configuração nativa e dispare os workflows ou crie a tag `vX.Y.Z`.

Mudanças de interface ou de lógica vão em `fonte/base/template.html`.

### Esquema de kids2.json

- **Chaves do topo:**
  - `C`: os 250 países e territórios
  - `ARTS`: 57 artigos (2 temáticos: `planeta-vivo` e `gente-do-planeta`; os outros são regiões e oceanos)
  - `G`: saudações por língua `[locale, Oi, pron, Tchau, pron, Obrigado, pron]`
  - `LN`: nomes de línguas em português
  - `AN`: melodias dos hinos
  - `REC`: metadados das gravações dos hinos
  - `OM`: ícones OpenMoji em SVG
  - `ECO`: biomas `[código, nome, cor]`
  - `RATES`: câmbio em BRL, com data
- **Cada país em `C`:**
  - Identificação e geografia:
    - `k`: ISO2
    - `n`: nome
    - `cap`: capitais
    - `ct`: continente
    - `a`: área em km²
    - `b`: fronteiras
    - `p`: artigos em que aparece
  - Língua:
    - `lg`: línguas
    - `g`: chave de `G`
    - `gv`: locale da voz
    - `ex`: Jeito de falar, itens `{t, o, r?, v?, l?, s}` = tipo, original, romanização, locale da voz, tradução literal, sentido
  - Números:
    - `s`: estatísticas (pop, ppp, pov, co2, ren, oilp, oilr…, com o ano em `xY`)
    - `pt`: Brasil e posições
  - Ficha:
    - `cur`: moedas
    - `idd`: código telefônico
    - `tld`: domínio da internet
    - `drive`: mão do trânsito
    - `units`: sistema de medidas
  - Hora:
    - `tz`: `[zona IANA da capital, …]`
    - `tzs`: vários fusos, lista `[[zona, cidade], …]`
  - Textos e mapa:
    - `f`: ficha de textos (nome_origem etc.)
    - `foco`: Em foco, itens `{h, t, img?, iw, ih, cr, src}`
    - `hm`: dados do mapa desenhado
  - Status: `un` (membro da ONU), `ind` (independente), `an` (soberania)
- **Item de artigo:** `{h, t, c:[ISO2 que o texto marca no mapa], img?, iw, ih, cr: crédito, src: página no Commons}`. O artigo tem `intro`.
- **Indicadores de "Comparar países":** ficam no array `IND` em template.html. Cada um tem `k`, `t`, `u`, `short`, `d` e `src`, e lê `o.s[k]`. Para criar um indicador novo, adicione o valor em `s` de cada país e um item em `IND`.
- **Foto nova:**
  - Baixe de upload.wikimedia.org, que costuma passar pela lista de sites liberados da sessão. Se não passar, peça o arquivo ao Miguel.
  - Converta para webp com largura de cerca de 900px e grave em `fonte/midia/fotos/<nome>.webp`.
  - Preencha `img`, `iw`, `ih`, `cr` ("Foto: autor · licença · Wikimedia Commons") e `src`.
  - O nome precisa terminar em `_algo`, porque o build agrupa as fotos em pacotes pelo prefixo: `foco_BR_3` vai para o pacote `foco_BR`, `008_4` para o pacote `008`.
  - O método antigo de busca está em `fonte/historico/foco_fotos.py` e `flickr.py`.

## 5. Regras editoriais (valem para todo texto novo ou revisto)

- **Público e linguagem:** crianças de 6 a 9 anos e as famílias. Português do Brasil claro, frases curtas, sem infantilizar. Dado concreto e verificável, com ano. Na dúvida, sem número.
- **Checagem:** confira na web todo fato novo, em fontes institucionais, enciclopédias e imprensa séria. A Wikipédia não passa pela lista de sites liberados; use wikiwand.com.
- **Atlas geográfico, para público amplo:**
  - Ele deve poder ser adotado por escolas e famílias de qualquer orientação.
  - Geopolítica, só quando inevitável, em tom descritivo e equilibrado: apresentar os lados de cada questão disputada, sem ser crítico com uns e apologético com outros.
  - Em maio-nov/2026 foram revistos, por exemplo, EUA, Cuba, Venezuela, Nicarágua, Israel e Palestina, Saara Ocidental, Armênia e Turquia (1915), Chipre e Ucrânia. As correções estão em `fonte/historico/foco_fix.json`.
- **Expressões e enfoque:**
  - Não usar "Sul Global"; falar em "hemisfério sul" quando for o caso.
  - Não culpar a colonização diretamente pelas desigualdades. Explicar padrões e assimetrias com causas múltiplas: geografia, clima, história, escolhas de governo. A China é o contraexemplo citado.
  - Mencionar a colonização como fato histórico descritivo, por exemplo para explicar a difusão de uma língua, é aceitável.
  - Sem exotismo, sem clichês ("povo alegre", "terra de contrastes", "paraíso tropical").
- **Em foco:**
  - 3 a 5 itens por país (2 a 3 para territórios minúsculos). Com 4 ou 5 itens, pelo menos 2 devem ser menos óbvios.
  - Tratar só do próprio país, sem ligações tangenciais.
  - Não repetir o que já está na ficha.
  - Título de até 5 palavras; texto de 40 a 75 palavras.
  - O guia completo está em `fonte/historico/foco/GUIA.md`. Uma parte dele ficou superada: onde diz "colonização com nome e custo", vale a regra acima.
- **Jeito de falar:** 1 ou 2 itens por país (palavra, gíria ou expressão curiosa), sem palavrão. Original, romanização, tradução literal e sentido.
- **Mapas:** todos os nomes em português. Nada de fontes com cara de Comic Sans.
- **Visual:** modo claro por padrão, com botão de tema. Paleta clara e quente (#fbfaf6, #f4ecd8). Fontes Literata nos títulos e Figtree no texto.
- **Arquivos para o Miguel:** nomes no formato "SOBRENOME (ano) - Título", quando se aplicar.

## 6. Estado atual (26/11/2026)

**Feito no app:**
- Mapa-múndi com regiões e oceanos. Os rótulos dos oceanos são menores, e "OCEANO ATLÂNTICO" no hemisfério sul aparece em duas linhas, a oeste de Greenwich. Opção norte em cima ou sul em cima.
- Página de cada país:
  - mapa desenhado e bandeira;
  - hino, com gravação ou melodia;
  - números com ranking;
  - hora ao vivo; países com vários fusos (19, entre eles BR, US, RU, AU e MX) listam a hora de uma cidade em cada fuso;
  - moeda com conversão;
  - pratos e exportações;
  - saudações com voz;
  - Jeito de falar, Em foco e Símbolos.
- Artigos regionais e temáticos com fotos. "Gente do planeta" tem abertura nova (padrões demográficos e assimetrias) e dois textos novos: "Mais de 7 mil línguas" e "Iguais e diferentes" (globalização e diversidade, em diálogo implícito com Lévi-Strauss e Stuart Hall).
- "Comparar países" (`#numeros`) tem, entre outros indicadores, produção de petróleo (% do mundo, Energy Institute 2025, via OWID) e reservas provadas (EIA).
- Jogos: bandeiras, capitais, "oi" e "onde fica".
- PWA com cache offline (sw.js); as fotos carregam sob demanda, em pacotes.

**Feito para as lojas:**
- Projetos Capacitor para Android e iOS.
- Workflows do GitHub Actions.
- Fichas, formulários e capturas.
- Política de privacidade em `web/priv.html`.
- A chave de envio do Android (upload.jks) e as senhas foram geradas e entregues ao Miguel, fora do repositório. **Nunca** commitar *.jks, *.p8 ou senhas: o `.gitignore` já cobre isso.

**Pendências do Miguel (dependem dele):**
1. Criar a conta da Google Play Console (US$ 25) e a do Apple Developer (US$ 99 por ano).
2. Cadastrar os segredos do repositório, listados no README, seção 3.
3. Publicar a política de privacidade num endereço público (Cloudflare Pages ou GitHub Pages) e trocar o e-mail de contato.
4. Na Play Store, conta pessoal nova exige teste fechado com 12 testadores durante 14 dias.

**Pendências e ofertas em aberto (minhas):**
- Rever os textos das lojas em `loja/textos/`. Eles ainda dizem "vista do Sul" e "a colonização é contada com nome e consequência", o que não combina mais com as regras da seção 5. Propor nova redação ao Miguel.
- Refazer as capturas de `loja/capturas/` depois das mudanças recentes (Em foco v2, Jeito de falar, fusos, petróleo).
- Cerca de 200 expressões do Jeito de falar em línguas grandes não foram checadas uma a uma na web. As 50 mais frágeis foram. Existe a oferta de uma segunda rodada.
- Reservas de petróleo: a fonte (EIA via Wikipédia) não declara o ano. Existe a oferta de trocar pelo OPEC Annual Statistical Bulletin 2026.
- Se o primeiro run dos workflows falhar, ler o log e corrigir.
- Testar o layout em tablet (por exemplo 1024×1366 e 1366×1024) e em celular pequeno (360×740) antes de enviar às lojas.

## 7. Artefato de pré-visualização (claude.ai)

- O Miguel acompanha o app pelo artefato "Atlas do Mundo · enciclopédia ilustrada":
  - slug `8d2f5462-fca7-47fc-975f-e67055372dbd`
  - https://claude.ai/artifact/JSBMH3X4KoQS4VTGf5hTEc
  - o artefato é privado dele; read: owner
- **Atualização de rotina:** pegue a versão atual com `get_artifact`. Depois chame `publish_files` com essa versão em `base_version`, publicando só `index.html` e `sw.js` (de web/) em modo patch.
- **Se mudaram fotos, mapas ou hinos:** publique também os arquivos de `f/`, `h/` ou `a/` alterados.
- **Limites:**
  - 256 arquivos e 64 MB por chamada; divida em lotes de menos de 55 MB;
  - 512 arquivos no total;
  - o modo `replace` apaga o que não for listado.

## 8. Armadilhas conhecidas

- **Rede:** o shell só alcança registros de pacotes, GitHub e alguns hosts. raw.githubusercontent.com (OWID e outros dados) funciona; Wikipédia e muitos sites, não. Para ler páginas, use WebFetch.
- **template.html:**
  - Usa `EMBED` (falso no app). As imagens têm `data-img` ou `data-tile` e são hidratadas por um MutationObserver.
  - Não redeclare variáveis já existentes (FB, FBU, FU…).
  - Não ponha `const` dentro de um `if` sem chaves: isso já quebrou o app uma vez.
- **Fusos horários:** os dados de `tzs` foram gerados a partir de `/usr/share/zoneinfo/zone.tab`, agrupando as zonas pelo deslocamento padrão. O script está em `fonte/historico/tzgroups.py`.
- **Commits:** termine a mensagem com as linhas de atribuição que o sistema indicar na sessão.
