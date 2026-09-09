#!/usr/bin/env python3
"""Gera assets/og.png — a miniatura que WhatsApp, LinkedIn e Google mostram.

Roda à mão quando o texto da capa mudar; o PNG é versionado no repositório
para o site continuar sem passo de build (ver README).

    python assets/gerar_og.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# A mesma paleta do site (assets/styles.css, bloco :root).
AREIA = (243, 240, 230)
VERDE = (23, 55, 47)
VERDE_SECO = (82, 107, 89)
TERRA = (155, 84, 47)
# Duas cores que existem só nesta capa, e cada uma por um motivo medido:
# a textura passa POR TRÁS do texto, então precisa ficar perto do fundo para
# não virar tarja de "texto riscado" (foi o que aconteceu com VERDE_SECO);
# e a linha secundária precisa de contraste real sobre o verde escuro, que
# VERDE_SECO também não dava.
TEXTURA = (34, 68, 58)
AREIA_FRACA = (170, 186, 172)

# 1200x630 é a proporção que o Open Graph pede; abaixo de 600x315 o
# WhatsApp degrada para miniatura quadrada minúscula.
LARGURA, ALTURA = 1200, 630

FONTES = Path("C:/Windows/Fonts")
DESTINO = Path(__file__).resolve().parent / "og.png"


def _fonte(arquivo: str, tamanho: int) -> ImageFont.FreeTypeFont:
    caminho = FONTES / arquivo
    if not caminho.is_file():
        raise SystemExit(f"fonte ausente: {caminho}")
    return ImageFont.truetype(str(caminho), tamanho)


def desenhar() -> Image.Image:
    img = Image.new("RGB", (LARGURA, ALTURA), VERDE)
    d = ImageDraw.Draw(img)

    # Curvas de nível — o mesmo motivo do cabeçalho do site, aqui como textura
    # de fundo cobrindo a capa inteira. Ela CRUZA o texto de propósito: tentar
    # desviar dele deixaria faixas vazias óbvias. O que a torna aceitável é o
    # contraste baixo de TEXTURA contra o fundo; com VERDE_SECO as linhas
    # riscavam as duas últimas linhas de texto.
    for i in range(16):
        base = 30 + i * 42
        pontos = [
            (x, base + math.sin((x / 210) + i * 0.55) * 26)
            for x in range(-20, LARGURA + 20, 12)
        ]
        d.line(pontos, fill=TEXTURA, width=2, joint="curve")

    # Filete de destaque, como a linha do polígono no site.
    d.rectangle([(0, 0), (LARGURA, 10)], fill=TERRA)

    d.text((80, 92), "MURUNDU", font=_fonte("seguibl.ttf", 40), fill=TERRA)
    d.text(
        (80, 152),
        "Licenciamento\nAmbiental",
        font=_fonte("seguibl.ttf", 92),
        fill=AREIA,
        spacing=6,
    )
    d.text(
        (80, 386),
        "Pedro Henrique Carvalho Gonçalves  ·  Engenheiro Ambiental  ·  CREA-MS 63.313",
        font=_fonte("segoeui.ttf", 27),
        fill=AREIA,
    )
    d.text(
        (80, 430),
        "Campo Grande, MS  ·  atendimento remoto em todo o Brasil",
        font=_fonte("segoeui.ttf", 27),
        fill=AREIA_FRACA,
    )
    d.text((80, 520), "murundu.eng.br", font=_fonte("segoeuib.ttf", 32), fill=TERRA)
    return img


if __name__ == "__main__":
    imagem = desenhar()
    imagem.save(DESTINO, "PNG", optimize=True)
    kb = DESTINO.stat().st_size / 1024
    print(f"GERADO: {DESTINO.name} — {imagem.width}x{imagem.height}, {kb:.0f} KB")
    if kb > 300:
        print("AVISO: acima de 300 KB; o WhatsApp pode recusar a miniatura")
        sys.exit(1)
