#!/usr/bin/env python3
"""Deriva os ícones de aba (favicon) dos ícones da marca em assets/marca/.

Os ícones originais têm margem transparente irregular e não são quadrados
(318x305 e 315x305). Aqui cada um é recortado pela caixa do que é opaco,
centrado numa tela quadrada e reduzido — nunca ampliado, para não fabricar
detalhe que a arte não tem (ver README, "A marca").

    python assets/gerar_icones.py

Saídas, todas em assets/:
    favicon-escuro.png   ícone escuro  — aba CLARA (64 px)
    favicon-claro.png    ícone creme   — aba ESCURA (64 px)
    apple-touch-icon.png ícone escuro, 180 px, sobre o creme da marca
    marca/murundu_marca_web.png  o símbolo, em versão leve para as páginas

Por que "web": o símbolo original tem ~23 mil cores (ruído da geração) e pesa
155 KB; a arte real tem 4 cores mais a suavização das bordas. Quantizado a 256
cores, sem dithering e SEM mudar o tamanho, pesa uma fração disso — o original
fica intacto ao lado, como fonte.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent
MARCA = RAIZ / "marca"
CREME = (249, 229, 200, 255)  # #F9E5C8, medido na arte


def leve(img: Image.Image) -> Image.Image:
    """Reduz a paleta (com alfa) sem alterar o tamanho."""
    return img.quantize(colors=256, method=Image.FASTOCTREE, dither=Image.NONE)


def quadrado(origem: Path, lado: int, fundo=None) -> Image.Image:
    img = Image.open(origem).convert("RGBA")
    img = img.crop(img.getchannel("A").getbbox())
    maior = max(img.size)
    escala = min(1.0, lado / maior)  # nunca amplia
    if escala < 1.0:
        img = img.resize(
            (round(img.width * escala), round(img.height * escala)), Image.LANCZOS
        )
    tela = Image.new("RGBA", (lado, lado), fundo or (0, 0, 0, 0))
    tela.alpha_composite(img, ((lado - img.width) // 2, (lado - img.height) // 2))
    return tela


if __name__ == "__main__":
    leve(quadrado(MARCA / "murundu_icone_escuro.png", 64)).save(RAIZ / "favicon-escuro.png", optimize=True)
    leve(quadrado(MARCA / "murundu_icone_claro.png", 64)).save(RAIZ / "favicon-claro.png", optimize=True)
    leve(Image.open(MARCA / "murundu_marca.png").convert("RGBA")).save(
        MARCA / "murundu_marca_web.png", optimize=True
    )
    # No iOS a transparência vira preto: o ícone vai sobre o creme da marca,
    # com folga de 12 % para o arredondamento do sistema não cortar a arte.
    miolo = quadrado(MARCA / "murundu_icone_escuro.png", 158)
    fundo = Image.new("RGBA", (180, 180), CREME)
    fundo.alpha_composite(miolo, (11, 11))
    fundo.convert("RGB").save(RAIZ / "apple-touch-icon.png", optimize=True)
    for nome in ("favicon-escuro.png", "favicon-claro.png", "apple-touch-icon.png", "marca/murundu_marca_web.png"):
        print(f"GERADO: {nome} — {(RAIZ / nome).stat().st_size / 1024:.1f} KB")
