# Atlas do Mundo

Enciclopédia ilustrada dos países, para crianças de 6 a 9 anos e suas famílias, vista a partir do Sul.
Este repositório contém o app completo para **Google Play** e **App Store**, compilado na nuvem (GitHub Actions), sem precisar de Mac nem de programas instalados no computador.

## O que tem aqui

| Pasta | Conteúdo |
|---|---|
| `web/` | O app em si (HTML, fotos, mapas desenhados, hinos). É o que vai dentro do aplicativo. |
| `android/`, `ios/` | Projetos nativos gerados pelo Capacitor 8 (não editar à mão). |
| `assets/` | Ícone e tela de abertura em alta resolução (fonte dos ícones nativos). |
| `loja/textos/` | Textos das fichas das lojas e respostas dos formulários. |
| `loja/capturas/` | Capturas de tela (celular Android, iPhone 6,9", iPad 13"), ícone 512 e gráfico 1024×500. |
| `fonte/` | Scripts que geram o app a partir dos dados (para futuras atualizações). |
| `.github/workflows/` | Compilação automática: `android.yml` (gera o .aab) e `ios.yml` (envia ao TestFlight). |

## Passo a passo para publicar

### 1. Contas (uma vez)
- **Google Play Console**: conta de desenvolvedor (taxa única de US$ 25). Conta pessoal nova exige teste fechado com 12 testadores por 14 dias antes de publicar.
- **Apple Developer Program**: US$ 99 por ano.

### 2. Domínio para a política de privacidade
As duas lojas pedem um endereço público para `web/privacidade.html`. O jeito mais simples: publicar a pasta `web/` no Cloudflare Pages (gratuito) ou ativar o GitHub Pages. Antes, troque o e-mail de contato no fim do arquivo.

### 3. Segredos do repositório (Settings → Secrets and variables → Actions)
**Android**
- `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD` — chave de envio (fornecida à parte; nunca colocar no repositório).
- `PLAY_SERVICE_ACCOUNT_JSON` (opcional) — para enviar automaticamente ao teste interno depois do primeiro envio manual.

**iOS** (App Store Connect → Usuários e acesso → Integrações → Chaves da API, papel "App Manager")
- `APPLE_TEAM_ID` — código da equipe (10 caracteres, em developer.apple.com → Membership).
- `ASC_KEY_ID`, `ASC_ISSUER_ID` — dados da chave da API.
- `ASC_KEY_P8_BASE64` — o arquivo .p8 da chave, convertido em base64.

### 4. Compilar
- Aba **Actions** → "Android — gerar AAB" → **Run workflow**. Ao fim, baixe o `.aab` em *Artifacts*.
- Aba **Actions** → "iOS — compilar e enviar ao TestFlight" → **Run workflow**. O app aparece no TestFlight em alguns minutos.
- Criar uma tag `v1.0.1` (Releases → Draft a new release) dispara os dois de uma vez.

### 5. Play Console
1. Criar o app (nome, idioma pt-BR, app, pago).
2. Preencher: política de privacidade, acesso ao app (sem login), anúncios (não), classificação de conteúdo, público-alvo (Famílias), segurança dos dados ("não coleta") — respostas em `loja/textos/formularios.md`.
3. Ficha da loja: textos de `loja/textos/google-play.md` e imagens de `loja/capturas/`.
4. Testes → Teste fechado: enviar o `.aab`, convidar 12+ testadores, esperar 14 dias; então pedir acesso à produção.
5. Preço: definir em Monetização (exige perfil de pagamentos).

### 6. App Store Connect
1. Meus apps → + → Novo app (bundle `br.com.miguelbconde.atlasdomundo`, nome "Atlas do Mundo: países").
2. Ficha: textos de `loja/textos/app-store.md`, capturas `iphone-6.9-*` e `ipad-13-*`.
3. Privacidade do app: "Dados não coletados". Categoria Kids: 6–8 anos.
4. Preço e disponibilidade; contrato de "Apps pagos" e dados bancários/fiscais.
5. Escolher o build enviado pelo TestFlight e enviar para revisão.

## Atualizar o conteúdo
Os dados e o texto são gerados por `fonte/data2.py` e `fonte/build2.py` (precisam dos dados de origem, não incluídos). Depois de gerar, copiar o resultado para `web/`, subir a versão em `package.json` e rodar os workflows.

## Licenças
Textos, fichas, mapas desenhados e programação: © Miguel Conde, todos os direitos reservados.
Componentes de terceiros e suas licenças: ver `THIRD_PARTY.md` (as mesmas informações estão na página Créditos do app).
