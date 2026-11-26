# Checagem de fatos — seção "Em foco"

Arquivo de entrada: `{ISO2: [itens]}`. Itens com `"usar"` e sem `"t"` são textos antigos já revisados: ignore. Confira os itens com `"t"` (novos ou revisados).

Para cada item, verifique com **WebSearch** (e WebFetch se preciso) todo fato checável, priorizando: números, datas, superlativos ("o maior", "o primeiro", "o único"), nomes próprios e afirmações históricas.
- Se o fato estiver certo: mantenha.
- Se estiver errado: corrija no texto, mantendo o tamanho (40–75 palavras) e o tom.
- Se não conseguir confirmar: reescreva sem aquele dado (tire o número ou a afirmação), sem inventar substituto.
- Não mude `"q"`, `"usar"` nem a ordem dos itens. Pode ajustar `"h"` se o título ficar impreciso.

Saída: o MESMO formato da entrada, com os textos corrigidos, gravado por script Python (json.dump, ensure_ascii=False) em `foco2/chk/<nome do arquivo>`. Além disso, grave `foco2/chk/<nome>.log.json` com a lista `[{pais, h, mudanca, fonte}]` das correções feitas. Responda em 3 linhas: quantos itens checados, quantos corrigidos, quantos tiveram dado retirado.
