# Murundu Consultoria Ambiental

Landing page estática da consultoria ambiental Murundu, com atuação em Mato Grosso do Sul e base em Campo Grande. O site usa somente HTML e CSS, não requer etapa de build e está preparado para hospedagem futura no GitHub Pages.

## Direção editorial e visual

A página segue a ideia de um **dossiê territorial** e usa a identidade visual da marca Murundu: o símbolo (um "M" de camadas de solo, com curva de nível, folha e o ponto do levantamento), o logotipo e a paleta medida na arte. Hierarquia tipográfica, linhas de processo e grade documental completam o conjunto. A estrutura sugerida no brief foi mantida, com uma nota técnica curta sobre o programa Murundu inserida depois dos trabalhos.

## A marca

Arquivos em `assets/marca/`. A paleta foi **medida na arte**, não estimada:

| cor | hex | papel no site |
|---|---|---|
| laranja queimada | `#AE5A04` | botões, fundo do contato, filetes, linhas |
| âmbar | `#E59801` | destaques sobre fundo escuro; botão no tema escuro |
| creme | `#F9E5C8` | painel do símbolo (sempre, nos dois temas) |
| tinta | `#231406` | títulos, faixas escuras, rodapé |

Duas regras que vêm de medição:

- **Texto de destaque sobre fundo claro usa `#8F4A03`** (`--accent-text`, ~6:1), não o laranja puro, que fica em 4,50:1 no fundo claro e ~4,0:1 sobre o creme da marca. Sobre a tinta escura o destaque é o âmbar.
- **O painel do símbolo é sempre creme.** O símbolo tem camadas em tinta `#231406` que sumiriam sobre um painel escuro.

O logotipo troca sozinho para a versão clara no tema escuro (`<picture>` com `prefers-color-scheme`).

### Descritor: "Consultoria Ambiental"

A arte original traz o descritor **"ANÁLISES AMBIENTAIS"** (os originais seguem intactos em `assets/marca/fonte/`). O site usa **"CONSULTORIA AMBIENTAL"**, que descreve a consultoria. Os SVGs de `assets/marca/` são gerados por `assets/gerar_logotipo.py`: a palavra "Murundu", os traços laterais e as cores são copiados do original; só as letras do descritor são redesenhadas, como **contornos vetoriais** de Inter SemiBold, no mesmo vão e na mesma linha de base. Contorno e não `<text>`, de propósito: `<text>` mudaria de letra conforme a máquina. Se a arte for revisada, substitua os arquivos de `fonte/` e rode o script (`pip install fonttools`).

`murundu_logotipo.png` existe só para a imagem de compartilhamento (`gerar_og.py`) e é a renderização do SVG a 2x (qualquer navegador gera: abrir o SVG a 1888 px e salvar com fundo transparente).

### Derivados

`python assets/gerar_icones.py` gera os ícones de aba (`favicon-escuro.png` na aba clara, `favicon-claro.png` na aba escura), o `apple-touch-icon.png` e `marca/murundu_marca_web.png`. Este último é o símbolo com a paleta reduzida a 256 cores (o original tem ~23 mil por ruído de geração e pesa 155 KB; a versão web pesa ~10 KB e foi comparada com o original, sem diferença visível). O PNG do símbolo tem 350×409 px nativos. Para tamanho grande, o site usa o **símbolo em vetor** (`marca/murundu_marca.svg`), traçado da própria arte por `python assets/vetorizar_marca.py` (`pip install potracer scipy numpy pillow`): cada pixel vai para a cor mais próxima da paleta medida, cada cor vira uma camada traçada com potrace, e as camadas são empilhadas com folga de ~0,5 px para não abrir fio de fundo. A conferência é numérica: renderizado e comparado com a arte, a diferença média é 4,5/255 sobre creme (2,9 sobre tinta), restrita a fios de borda. Ele herda as pequenas irregularidades de borda da arte, que é raster; se vier uma arte vetorial do autor, ela substitui este arquivo.

`python assets/gerar_og.py` regenera a imagem de compartilhamento com a marca.

## Ver localmente

Na raiz deste repositório, execute:

```powershell
python -m http.server 8000
```

Depois acesse `http://localhost:8000/` no navegador.

Também é possível abrir `index.html` diretamente, mas o servidor local reproduz melhor a navegação entre páginas.

## Verificar antes de publicar

```powershell
python verificar.py
```

O verificador bloqueia a publicação se houver marcadores de conteúdo, URLs externas não autorizadas, imagens sem texto alternativo, quantidade incorreta de títulos principais ou `CNAME` inválido. Com os dados reais preenchidos, a execução deve terminar com zero falhas.

Os testes comportamentais do verificador podem ser executados com:

```powershell
python -m unittest -v test_verificar.py
```

## O que o verificador NÃO alcança: títulos e larguras

`verificar.py` lê os arquivos; ele não calcula layout, então **não** enxerga
palavra de título partida entre linhas nem estouro horizontal. Isso se mede
no navegador, com o script do repositório:

```
npm install playwright
node scripts/medir_titulos.js        # exit 1 se achar qualquer defeito
```

Ele percorre 10 larguras (320 a 1920 px) nos temas claro e escuro e reprova:
palavra de título **partida entre linhas**, título com **`hyphens: auto`**,
título mais largo que a própria caixa e rolagem horizontal da página.

**Regra: título nunca é hifenizado** (`hyphens: manual`). A hifenização
automática não age só quando a palavra é mais larga que a coluna: o navegador
hifeniza sempre que ela não cabe no *fim da linha corrente*, mesmo cabendo
inteira na linha de baixo — foi assim que "empreendimento" virou
"empreendi-/mento" e "consultoria" virou "con-/sultoria" no celular. (Este
README e o CSS já afirmaram que a hifenização *protegia* o título; estava
errado.) ⚠️ O defeito só aparece com o dicionário pt-BR instalado, que o
Chromium de teste não tem — por isso o script confere também a **causa**
(`hyphens`), e não só o sintoma.

Palavra composta com hífen real ("lava-jato") leva `<span class="nao-quebra">`
para não partir no hífen. O título principal tem **dois níveis**
(`.h1-main` forte e `.h1-sub` mais leve, na cor de destaque): a hierarquia
dispensa quebra forçada, e cada nível só quebra entre palavras.

Rode o script sempre que mudar o texto de um título ou a largura de uma coluna.
Palavra longa nova é o gatilho.

## Fontes

Source Serif 4 (títulos) e Inter (texto) ficam em `assets/fonts/`, em WOFF2 variável, subconjunto latino, com as licenças SIL OFL ao lado. Nada é pedido a servidores de terceiros. Trocar a fonte de um título muda a largura das palavras: refaça a medição das 5 larguras descrita acima.

## Depoimentos

O site é estático e não recebe dados de visitantes. O botão "Enviar meu depoimento" abre o e-mail do visitante com um modelo e a pergunta de autorização. Ao receber um depoimento **com autorização expressa**, copie o `<figure class="depoimento">` que está comentado em `#depoimentos` no `index.html` e preencha. Não invente nem edite o sentido de depoimentos, e não adicione `Review`/`AggregateRating` ao JSON-LD sem avaliações reais e verificáveis.

## Publicação futura

Depois de obter uma verificação sem falhas, os arquivos podem ser publicados diretamente pelo GitHub Pages. O domínio, sitemap e processamento sem Jekyll já estão configurados nos arquivos estáticos. A fotografia profissional permanece opcional e está documentada em `PENDENCIAS-DE-CONTEUDO.md`. Nenhuma publicação ou configuração remota foi realizada neste repositório.
O passo a passo completo — DNS no Registro.br, GitHub Pages e a ordem em que
cada etapa tem de acontecer — está em `DNS-E-PUBLICACAO.md`.
