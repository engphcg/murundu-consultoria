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

O verificador bloqueia a publicação enquanto houver marcadores de conteúdo, URLs externas não autorizadas, imagens sem texto alternativo, quantidade incorreta de títulos principais ou `CNAME` inválido. Nesta etapa, a reprovação por conteúdo pendente é intencional.

Os testes comportamentais do verificador podem ser executados com:

```powershell
python -m unittest -v test_verificar.py
```

## Publicação futura

Depois de substituir todos os marcadores listados em `PENDENCIAS-DE-CONTEUDO.md` e obter uma verificação sem falhas, os arquivos podem ser publicados diretamente pelo GitHub Pages. O domínio, sitemap e processamento sem Jekyll já estão configurados nos arquivos estáticos. Nenhuma publicação ou configuração remota foi realizada neste repositório.
