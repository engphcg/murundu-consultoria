#!/usr/bin/env python3
"""Gera assets/og.png — a miniatura que WhatsApp, LinkedIn e Google mostram.

Roda à mão quando o texto da capa ou a marca mudar; o PNG é versionado no
repositório para o site continuar sem passo de build (ver README).

    python assets/gerar_og.py

Usa só arquivos do próprio repositório: o símbolo e o logotipo de
assets/marca/ e as fontes de assets/fonts/og/ (as mesmas famílias do site,
em WOFF estático porque o Pillow não lê WOFF2 variável). Funciona igual em
Windows, macOS e Linux.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent
MARCA = RAIZ / "marca"
FONTES = RAIZ / "fonts" / "og"
DESTINO = RAIZ / "og.png"

# Paleta MEDIDA na arte da marca (README, "A paleta").
CREME = (249, 229, 200)  # #F9E5C8
TINTA = (35, 20, 6)  # #231406
LARANJA = (174, 90, 4)  # #AE5A04
# Para texto pequeno sobre o creme, o laranja da marca dá só ~4:1; esta
# variante mais funda dá ~6:1 e é a mesma usada no CSS (--accent-text).
LARANJA_TEXTO = (143, 74, 3)  # #8F4A03
TINTA_SUAVE = (95, 72, 50)  # #5F4832

# 1200x630 é a proporção que o Open Graph pede; abaixo de 600x315 o
# WhatsApp degrada para miniatura quadrada minúscula.
LARGURA, ALTURA = 1200, 630


def _fonte(arquivo: str, tamanho: int) -> ImageFont.FreeTypeFont:
    caminho = FONTES / arquivo
    if not caminho.is_file():
        raise SystemExit(f"fonte ausente: {caminho}")
    return ImageFont.truetype(str(caminho), tamanho)


def _sobre(base: Image.Image, imagem: Image.Image, posicao: tuple[int, int]) -> None:
    base.paste(imagem, posicao, imagem)


def desenhar() -> Image.Image:
    img = Image.new("RGB", (LARGURA, ALTURA), CREME)
    d = ImageDraw.Draw(img)

    # Filete de topo, na cor do corpo do "M".
    d.rectangle([(0, 0), (LARGURA, 12)], fill=LARANJA)

    # O símbolo no tamanho nativo (350x409): ampliar fabricaria detalhe.
    simbolo = Image.open(MARCA / "murundu_marca.png").convert("RGBA")
    _sobre(img, simbolo, (92, (ALTURA - simbolo.height) // 2 + 6))

    # Coluna de texto.
    x = 540
    logotipo = Image.open(MARCA / "murundu_logotipo.png").convert("RGBA")
    largura_logo = 560
    logotipo = logotipo.resize(
        (largura_logo, round(logotipo.height * largura_logo / logotipo.width)),
        Image.LANCZOS,
    )
    _sobre(img, logotipo, (x, 48))

    d.text(
        (x, 228),
        "Licenciamento\nambiental",
        font=_fonte("source-serif-4-latin-600-normal.woff", 74),
        fill=TINTA,
        spacing=4,
    )
    d.text(
        (x, 432),
        "Pedro Henrique Carvalho Gonçalves",
        font=_fonte("inter-latin-700-normal.woff", 26),
        fill=TINTA,
    )
    d.text(
        (x, 470),
        "Engenheiro Ambiental  ·  CREA-MS 63.313",
        font=_fonte("inter-latin-500-normal.woff", 25),
        fill=TINTA_SUAVE,
    )
    d.text(
        (x, 504),
        "Campo Grande, MS  ·  atendimento em todo o Brasil",
        font=_fonte("inter-latin-500-normal.woff", 25),
        fill=TINTA_SUAVE,
    )
    d.text(
        (x, 562),
        "murundu.eng.br",
        font=_fonte("inter-latin-700-normal.woff", 30),
        fill=LARANJA_TEXTO,
    )
    return img


if __name__ == "__main__":
    imagem = desenhar()
    imagem.save(DESTINO, "PNG", optimize=True)
    kb = DESTINO.stat().st_size / 1024
    print(f"GERADO: {DESTINO.name} — {imagem.width}x{imagem.height}, {kb:.0f} KB")
    if kb > 300:
        print("AVISO: acima de 300 KB; o WhatsApp pode recusar a miniatura")
        sys.exit(1)
