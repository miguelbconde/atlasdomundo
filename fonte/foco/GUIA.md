# Seção "Em foco" — além dos clichês (Atlas do Mundo, crianças de 6 a 9 anos e famílias, pt-BR)

Entrada: `{ISO2: {nome, onu, capital, populacao, ja_na_ficha:{patrimonio, pratos, exporta}, em_foco_atual:[ids], candidatos:[{id, titulo, texto, foto}]}}`.
`candidatos` são textos já existentes nos artigos regionais (com foto quando `foto: true`); `em_foco_atual` são os ids escolhidos antes.

Monte, para CADA país/território, a seção "Em foco" final:

**Quantidade:** 3 a 5 textos (2 a 3 para territórios minúsculos, desabitados ou com pouca informação). Todo país precisa ter seção.

**Mistura obrigatória:**
- 1 ou 2 textos **fundamentais** (o que todo mundo deveria saber), mas sempre com dado concreto e verificável, nunca generalização.
- Quando houver 4 ou 5 textos, **pelo menos 2 menos óbvios**: um fato histórico pouco conhecido, uma invenção ou descoberta, um ecossistema ou animal singular, uma prática cotidiana, uma forma de arte ou ofício específico, uma obra de engenharia, uma pessoa importante pouco lembrada, uma língua, um fenômeno geográfico surpreendente.

**Proibido (clichês):** "o povo é alegre/hospitaleiro", "todo mundo joga futebol", "terra de contrastes", "paraíso tropical", exotismo, listas genéricas de atrações turísticas. Se o tema for futebol, carnaval, praia etc., só entra com dados precisos (datas, números, nomes) e um ângulo que ensine algo.

**Outras regras:**
- Sobre o PRÓPRIO país, nada de ligações tangenciais com outros lugares.
- Evite repetir o que já está na ficha (`ja_na_ficha`); complemente.
- Perspectiva do Sul Global: povos como sujeitos da própria história, colonização com nome e custo, sem exotismo. Ligue ao Brasil só quando for fato relevante, não forçado.
- **Verifique os fatos com WebSearch** (fontes institucionais, enciclopédias, imprensa séria) para tudo o que for novo; números com ano; nada inventado; na dúvida, sem número.
- Linguagem: português do Brasil claro, frases curtas, sem infantilizar.

**Formato de cada item:**
- Para reaproveitar um candidato: `{"usar": "<id>", "h": "título (opcional, se quiser mudar)", "t": "texto (opcional, se quiser revisar)"}` — mantém a foto.
- Para criar novo: `{"h": "título curto (até 5 palavras)", "t": "2 a 4 frases, 40–75 palavras", "q": "busca em inglês para achar uma foto livre no Wikimedia Commons: lugar, objeto, animal ou paisagem concreta; sem pessoas em close"}`.
Ordene do mais fundamental para o menos óbvio.

**Saída:** `{ISO2: [itens]}` com todas as chaves da entrada. Grave com script Python (json.dump, ensure_ascii=False), valide (todas as chaves, 2–5 itens, ids existentes) e responda em 3 linhas.
