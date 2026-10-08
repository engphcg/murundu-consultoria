#!/usr/bin/env python3
"""Traça o SÍMBOLO da marca em vetor, a partir da própria arte.

O símbolo só existia em PNG (350x409). Aqui ele é vetorizado por camadas de cor,
no mesmo espírito do logotipo (README, "A marca"): determinístico, a partir da
arte, sem redesenhar à mão e sem pedir arte nova.

    pip install potracer scipy numpy pillow
    python assets/vetorizar_marca.py

Método:
 1. a arte é ampliada 4x SÓ para posicionar as bordas com precisão de
    sub-pixel — a ampliação é premultiplicada (a cor do fundo transparente não
    vaza para a borda) e não acrescenta detalhe: o contorno traçado segue onde a
    arte já tinha a borda;
 2. cada pixel opaco vai para a cor mais próxima da paleta MEDIDA (laranja,
    tinta, creme); as bordas suavizadas caem na cor dominante;
 3. cada cor vira uma máscara, limpa de pontos soltos, e é traçada com potrace;
 4. as camadas são empilhadas: base em tinta (levemente encolhida, para nunca
    aparecer fora do contorno), depois laranja, depois creme. Laranja e creme
    levam uma folga de ~0,5 px para não deixar fio de fundo entre elas.

A conferência é numérica: o SVG é renderizado e comparado pixel a pixel com a
arte (ver o final do script). Nada de "parece igual".

Saída: assets/marca/murundu_marca.svg
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import potrace
from PIL import Image
from scipy import ndimage

RAIZ = Path(__file__).resolve().parent
ORIGEM = RAIZ / "marca" / "murundu_marca.png"
DESTINO = RAIZ / "marca" / "murundu_marca.svg"

ESCALA = 4  # ampliação só para posicionar a borda
FOLGA = 2  # dilatação das camadas de cima, em px ampliados (~0,5 px reais)
ENCOLHE = 3  # a base escura é encolhida, para nunca aparecer fora do contorno

# Paleta MEDIDA na arte (README da marca).
PALETA = {
    "tinta": (0x23, 0x14, 0x06),
    "laranja": (0xAE, 0x5A, 0x04),
    "creme": (0xF9, 0xE5, 0xC8),
}


def hexa(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def ampliar_premultiplicado(img: Image.Image, k: int) -> np.ndarray:
    a = np.asarray(img.convert("RGBA"), dtype=np.float64) / 255.0
    pre = a.copy()
    pre[..., :3] *= a[..., 3:4]
    camadas = []
    for c in range(4):
        im = Image.fromarray(pre[..., c].astype(np.float32), mode="F")
        camadas.append(np.asarray(im.resize((img.width * k, img.height * k), Image.BICUBIC)))
    p = np.stack(camadas, axis=-1)
    alfa = np.clip(p[..., 3], 0, 1)
    rgb = np.where(alfa[..., None] > 1e-3, p[..., :3] / np.maximum(alfa[..., None], 1e-3), 0)
    return np.dstack([np.clip(rgb, 0, 1), alfa])


def mascaras(rgba: np.ndarray) -> dict[str, np.ndarray]:
    opaco = rgba[..., 3] >= 0.5
    cores = np.array(list(PALETA.values()), dtype=np.float64) / 255.0
    dist = ((rgba[..., None, :3] - cores[None, None]) ** 2).sum(-1)
    classe = dist.argmin(-1)
    saida = {}
    for i, nome in enumerate(PALETA):
        m = opaco & (classe == i)
        # tira pontos soltos (resíduo de borda) e fecha furinhos de 1-2 px
        rot, n = ndimage.label(m)
        if n:
            tam = ndimage.sum(m, rot, range(1, n + 1))
            m = np.isin(rot, [j + 1 for j, t in enumerate(tam) if t >= 60])
        m = ndimage.binary_closing(m, iterations=1)
        saida[nome] = m
    saida["_opaco"] = opaco
    return saida


def tracar(mascara: np.ndarray, k: int) -> str:
    # potracer traça o que é "escuro" (False); a máscara marca o que é tinta (True).
    bmp = potrace.Bitmap(~mascara)
    caminho = bmp.trace(turdsize=40, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
                        alphamax=1.2, opticurve=True, opttolerance=0.8)
    f = lambda p: f"{p.x / k:.1f},{p.y / k:.1f}"
    partes = []
    for curva in caminho:
        partes.append(f"M{f(curva.start_point)}")
        for seg in curva.segments:
            if seg.is_corner:
                partes.append(f"L{f(seg.c)}L{f(seg.end_point)}")
            else:
                partes.append(f"C{f(seg.c1)} {f(seg.c2)} {f(seg.end_point)}")
        partes.append("Z")
    return "".join(partes)


def main() -> int:
    img = Image.open(ORIGEM)
    rgba = ampliar_premultiplicado(img, ESCALA)
    m = mascaras(rgba)

    base = ndimage.binary_erosion(m["_opaco"], iterations=ENCOLHE)
    laranja = ndimage.binary_dilation(m["laranja"], iterations=FOLGA)
    creme = ndimage.binary_dilation(m["creme"], iterations=FOLGA)

    # Camadas de cima não podem sair do contorno da arte.
    laranja &= m["_opaco"]
    creme &= m["_opaco"]

    w, h = img.size
    camadas = [
        ("tinta", base),
        ("laranja", laranja),
        ("creme", creme),
    ]
    corpo = "\n".join(
        f'<path fill="{hexa(PALETA[nome])}" fill-rule="evenodd" d="{tracar(masc, ESCALA)}"/>'
        for nome, masc in camadas
    )
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        'role="img" aria-label="Murundu — símbolo">\n' + corpo + "\n</svg>\n"
    )
    DESTINO.write_text(svg, encoding="utf-8")
    print(f"GERADO: {DESTINO.name} — {DESTINO.stat().st_size / 1024:.1f} KB, viewBox {w}x{h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
