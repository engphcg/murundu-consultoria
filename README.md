# Murundu Consultoria Ambiental

Landing page estática da consultoria ambiental Murundu, com atuação em Mato Grosso do Sul e base em Campo Grande. O site usa somente HTML e CSS, não requer etapa de build e está preparado para hospedagem futura no GitHub Pages.

## Direção editorial e visual

A página segue a ideia de um **dossiê territorial**: hierarquia tipográfica, linhas de processo, grade documental e um desenho próprio de curvas de nível. A estrutura sugerida no brief foi mantida, com uma nota técnica curta sobre o programa Murundu inserida depois dos trabalhos. Assim, a tecnologia aparece como competência complementar sem competir com os serviços de consultoria.

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

## O que o verificador NÃO alcança: as 5 larguras

`verificar.py` lê os arquivos; ele não calcula layout, então **não** enxerga
texto quebrado no meio da palavra nem estouro horizontal. Isso se confere com o
navegador aberto, em 360 · 390 · 768 · 1280 · 1920 px, medindo no DOM (não só
olhando a captura):

- `document.documentElement.scrollWidth > innerWidth` tem de ser `false`;
- para cada título, a palavra mais longa tem de caber na largura útil do
  elemento — foi assim que se achou o `max-width: 16ch` do `<h1>` (a palavra
  "empreendimento" mede 14,12ch: qualquer valor menor a parte no meio, em
  QUALQUER tamanho de fonte) e os tetos dos `clamp` de `h1` e `h2`.

Repita essa medição sempre que mudar o texto de um título ou a largura de uma
coluna. Palavra longa nova é o gatilho.

## Publicação futura

Depois de obter uma verificação sem falhas, os arquivos podem ser publicados diretamente pelo GitHub Pages. O domínio, sitemap e processamento sem Jekyll já estão configurados nos arquivos estáticos. A fotografia profissional permanece opcional e está documentada em `PENDENCIAS-DE-CONTEUDO.md`. Nenhuma publicação ou configuração remota foi realizada neste repositório.
O passo a passo completo — DNS no Registro.br, GitHub Pages e a ordem em que
cada etapa tem de acontecer — está em `DNS-E-PUBLICACAO.md`.
