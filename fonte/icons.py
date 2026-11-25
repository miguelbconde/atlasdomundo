import re
# regras em ordem: (expressão, hexcode OpenMoji)
PROD = [
 (r'petr[oó]leo|hidrocarboneto|coque|óleo combust|gasolina|diesel|querosene', '1F6E2'),
 (r'gás', '1F525'), (r'eletricidade|energia elétrica', '26A1'),
 (r'ouro|metais preciosos|prata|platina', '1FA99'),
 (r'diamante|pedras preciosas|gemas', '1F48E'), (r'joia', '1F48D'),
 (r'minério|minérios|bauxita|fosfat|carvão|dolomita|cascalho|pedra|areia|sal\b|potássio|calcário|urânio|cobalto|níquel|estanho|zinco|manganês|carbonato', '1FAA8'),
 (r'ferro|aço|cobre|alumínio|ligas|metal|sucata|barras|blocos de|fios de alumínio', '1F529'),
 (r'cimento|tijolo|casas pré', '1F9F1'),
 (r'vacina', '1F489'), (r'medicament|remédio|hormôni|farmac|sangue|instrumentos médicos|ortopéd', '1F48A'),
 (r'químic|ácido|álcoois|nitrogênio|amina|plástic|polímer|borracha sintética|aromátic|fertiliz|óleos essenciais|sabão|cosmét|perfume', '1F9EA'),
 (r'caminh[õo]', '1F69A'), (r'carro|veículo|automó|tratores', '1F697'), (r'navio|barco|embarca', '1F6A2'), (r'avi[ãõa]o|aeronave|aviões|helicópter', '2708'),
 (r'computador|chips|semicondut|circuito|eletrônic', '1F4BB'), (r'telefone|celular', '1F4F1'), (r'transmissão|telecomunica|rádio|tv\b', '1F4E1'),
 (r'fios|cabos|isolad', '1F50C'), (r'bateria', '1F50B'), (r'turbina|máquina|equipamento|motor|peças|aparelho|bomba|válvula|escavação|contêiner|reator', '2699'),
 (r'calçado|sapato', '1F45F'), (r'roupa|vestuário|camisa|malhas|confecç', '1F455'), (r'tecido|têxte|fio de|juta|roupa de cama|tapete', '1F9F5'), (r'lã|algodão', '1F9F6'),
 (r'relógio', '231A'), (r'móve|assento', '1FA91'), (r'papel|celulose|selos|documentos|livros', '1F4C4'), (r'pintura|obras de arte|antiguidad', '1F5BC'), (r'mala|estojo', '1F9F3'),
 (r'cerveja', '1F37A'), (r'vinho', '1F377'), (r'rum|bebidas|destilad|uísque|vodca|licor|álcool', '1F943'), (r'água', '1F4A7'),
 (r'flor', '1F338'), (r'especiaria|cravo|baunilha|canela|noz-moscada|açafrão|cardamomo|pimenta-do-reino|gomas|resinas|babosa|aloe|ervas', '1F33F'), (r'gengibre', '1FADA'),
 (r'mel\b', '1F36F'), (r'margarina|manteiga', '1F9C8'), (r'queijo|laticínio', '1F9C0'), (r'leite|iogurte', '1F95B'),
 (r'gado|bovin|búfal|boi', '1F404'), (r'porco|suín', '1F416'), (r'ovelha|carneiro|cordeiro|peles', '1F411'), (r'cabra|caprin', '1F410'), (r'camel', '1F42A'),
 (r'frango|aves|galinha|peru\b', '1F414'), (r'ovo', '1F95A'), (r'camarão|crustác|lagosta|caranguejo', '1F990'), (r'marisco|frutos do mar|molusc|ostra|polvo|lula', '1F9AA'),
 (r'peix|pescad|atum|sardinha|salmão|bacalhau|farinha de peixe', '1F41F'), (r'carne|farinha de origem animal', '1F969'),
 (r'café', '2615'), (r'cacau|chocolate', '1F36B'), (r'chá', '1F375'), (r'tabaco|fumo', '1F342'),
 (r'cana', '1F38B'), (r'açúcar|melaço', '1F36C'), (r'beterraba', '1FADC'),
 (r'arroz', '1F35A'), (r'milho|sorgo|milhete|milheto', '1F33D'), (r'trigo|cevada|aveia|centeio|triticale|cereais|farinha|forragem|grãos', '1F33E'),
 (r'soja|feijão|leguminosa|lentilha|grão-de-bico|ervilha|fava', '1FAD8'), (r'amendoim', '1F95C'), (r'castanha|caju|noz|nozes|amêndoa|pistache|avelã', '1F330'),
 (r'coco|copra', '1F965'), (r'dendê|palma|tâmara|dendezeiro', '1F334'), (r'azeit|oliva', '1FAD2'), (r'girassol|canola|colza|gergelim|oleaginos|óleos? de sementes|óleos? vege', '1F33B'),
 (r'banana|plátano', '1F34C'), (r'mandioca|inhame|taro|batata-doce|raízes|tubérc|fruta-pão', '1F360'), (r'batata', '1F954'),
 (r'tomate', '1F345'), (r'cenoura', '1F955'), (r'repolho|alface|espinafre|hortaliça|verdura|legumes', '1F96C'), (r'pepino', '1F952'), (r'cebola|alho', '1F9C5'),
 (r'pimentão', '1FAD1'), (r'pimenta|chile', '1F336'), (r'abóbora', '1F383'), (r'melancia', '1F349'), (r'melão|melões', '1F348'),
 (r'laranja|tangerina|cítric|toranja|mexerica', '1F34A'), (r'limão|limões|lima', '1F34B'), (r'maçã', '1F34E'), (r'uva', '1F347'), (r'abacaxi', '1F34D'), (r'manga|goiaba|mamão|papaia', '1F96D'), (r'abacate', '1F951'), (r'ameixa|pêssego|caroço|damasco|cereja', '1F351'),
 (r'fruta|frutos', '1F34E'), (r'madeira|tora|lenha', '1FAB5'), (r'borracha|látex', '1F333'), (r'sal\b', '1F9C2'),
]
DISH = [
 (r'mantu|pastizzi|pastéis', '1F95F'), (r'tourti', '1F967'), (r'strudel|gaufre|waffle|potica|wonders', '1F370'), (r'kimchi|sukuma', '1F96C'), (r'mian\b|\bmin\b|naengmyeon|tsuivan|udon|soba|lo mein', '1F35C'), (r'pršut|presunto|speķ', '1F969'),
 (r'sushi|sashimi', '1F363'), (r'paella|tajine|tagine|panela', '1F958'), (r'curry|caril|dal\b|dhal', '1F35B'), (r'lámen|ramen|lamen|noodle|macarrão de arroz|pho|pad thai|lagman|laghman', '1F35C'),
 (r'pizza', '1F355'), (r'tempur', '1F364'), (r'macarrão|espaguete|lasanha|ravióli|nhoque|talharim|massa (italiana|fresca|recheada)', '1F35D'), (r'taco|tortilha', '1F32E'), (r'tamal|tamale|humita|pamonha', '1FAD4'),
 (r'bolinho|dumpling|pastel|empanada|samosa|pierogi|manti|momo|khinkali|pelmeni|guioza|gyoza|buuz|bolinha', '1F95F'), (r'falafel|kibe|quibe|croquete', '1F9C6'),
 (r'espet|kebab|churrasco|grelhad|satay|shashlik|brochete|anticucho|suya', '1F362'), (r'fondue', '1FAD5'), (r'sanduíche|sanduiche|hambúrguer|burger|wrap|shawarma|döner|doner|kebab no pão|pita', '1F959'),
 (r'salsicha|linguiça|chouriço|salame', '1F32D'), (r'panqueca|crepe|blini|injera|dosa|arepa|pupusa|tapioca', '1F95E'), (r'torta|quiche|pie\b|empadão', '1F967'),
 (r'pão|pães|naan|chapati|roti|baguete|broa|bagel|focaccia', '1F35E'), 
 (r'sopa|caldo|borscht|borsch|gazpacho|ensopado|guisado|cozido|ragu|goulash|gulache|feijoada|moqueca|sancocho|ajiaco|cassoulet|chili|stew|picadinho', '1F372'),
 (r'arroz|pilaf|plov|risoto|biryani|jollof|nasi|bibimbap|onigiri', '1F35A'), (r'feijão|feijões|lentilha|grão-de-bico|homus|hummus|ful\b|foul|frijol', '1FAD8'),
 (r'mingau|papa|fufu|ugali|nshima|sadza|pirão|polenta|angu|cuscuz|couscous|porridge|aveia|pap\b|banku|kenkey|cachupa', '1F963'),
 (r'\bbolo|(?<!-)\bdoces?\b|sobremesa|pudim|baklava|alfajor|biscoito|brigadeiro', '1F370'),
 (r'salada|ceviche|tabule|tabbouleh', '1F957'), (r'camarão|lagosta|caranguejo', '1F364'), (r'peixe|bacalhau|arenque|salmão|atum|sardinha|truta|tilápia', '1F41F'),
 (r'frango|galinha|pato|peru\b|ave\b', '1F357'), (r'cordeiro|carneiro|cabra|cabrito|ovelha', '1F356'), (r'carne|bife|porco|leitão|vaca|boi', '1F969'),
 (r'ovo|omelete|tortilla espanhola|shakshuka', '1F373'), (r'queijo', '1F9C0'), (r'banana|plátano|matoke', '1F34C'), (r'mandioca|inhame|batata-doce|taro|poi\b', '1F360'),
 (r'batata', '1F954'), (r'milho', '1F33D'), (r'coco', '1F965'), (r'iogurte|leite', '1F95B'), (r'chá', '1F375'), (r'café', '2615'),
]
def pick(s, rules, default):
    s = (s or '').lower()
    for rx, h in rules:
        if re.search(rx, s): return h
    return default
