#!/usr/bin/env python3
"""Gera assets/relevo.svg — curvas de nível de um CAMPO DE MURUNDUS.

O murundu é o montículo de terra do Cerrado (README, "A marca"); um campo de
murundus, visto de cima com curvas de nível, é a textura cartográfica da marca.
Aqui ela é desenhada a partir de uma superfície matemática (soma de montículos
gaussianos de posição e tamanho sorteados com semente fixa) e as curvas saem de
marching squares, como em uma carta topográfica: a cada 5ª curva, uma "curva
mestra" mais grossa. Determinístico: a mesma semente dá o mesmo arquivo.

    pip install numpy scikit-image
    python assets/gerar_relevo.py

O SVG só tem traços (sem cor): o site o usa como MÁSCARA (`mask-image`) e pinta
com a cor do tema, então o mesmo arquivo serve ao tema claro, ao escuro e às
faixas escuras.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from skimage import measure

DESTINO = Path(__file__).resolve().parent / "relevo.svg"

LARGURA, ALTURA = 1600, 900  # viewBox
GRADE = 5  # px do viewBox por célula da grade
SEMENTE = 20261008
N_MONTICULOS = 46
N_NIVEIS = 26
CURVA_MESTRA_A_CADA = 5


def superficie() -> np.ndarray:
    rng = np.random.default_rng(SEMENTE)
    nx, ny = LARGURA // GRADE, ALTURA // GRADE
    y, x = np.mgrid[0:ny, 0:nx].astype(float)
    z = np.zeros((ny, nx))
    for _ in range(N_MONTICULOS):
        cx, cy = rng.uniform(-0.05, 1.05) * nx, rng.uniform(-0.05, 1.05) * ny
        raio = rng.uniform(5, 17)
        altura = rng.uniform(0.35, 1.0)
        # Montículo levemente achatado, como os murundus vistos de cima.
        achatamento = rng.uniform(0.8, 1.25)
        z += altura * np.exp(-(((x - cx) / raio) ** 2 + ((y - cy) / (raio * achatamento)) ** 2))
    # Declive suave para a esquerda: o relevo "sobe" para o canto direito.
    z += 0.35 * (x / nx)
    return z


def caminho(contorno: np.ndarray) -> str:
    # Simplifica sem mudar a forma visível e escreve em coordenadas do viewBox.
    pts = measure.approximate_polygon(contorno, tolerance=0.25)
    xs = pts[:, 1] * GRADE
    ys = pts[:, 0] * GRADE
    partes = [f"M{xs[0]:.0f} {ys[0]:.0f}"]
    partes += [f"L{x:.0f} {y:.0f}" for x, y in zip(xs[1:], ys[1:])]
    return "".join(partes)


def main() -> None:
    z = superficie()
    niveis = np.linspace(z.min() + 0.08, z.max() - 0.12, N_NIVEIS)
    finos: list[str] = []
    mestras: list[str] = []
    for i, nivel in enumerate(niveis):
        destino = mestras if i % CURVA_MESTRA_A_CADA == 0 else finos
        for contorno in measure.find_contours(z, nivel):
            if len(contorno) >= 12:
                destino.append(caminho(contorno))
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGURA} {ALTURA}" '
        'preserveAspectRatio="xMidYMid slice" fill="none" stroke="#000" '
        'stroke-linecap="round" stroke-linejoin="round">\n'
        f'<path stroke-width="1" d="{"".join(finos)}"/>\n'
        f'<path stroke-width="2.2" d="{"".join(mestras)}"/>\n'
        "</svg>\n"
    )
    DESTINO.write_text(svg, encoding="utf-8")
    print(f"GERADO: {DESTINO.name} — {DESTINO.stat().st_size / 1024:.0f} KB, "
          f"{len(finos)} curvas finas + {len(mestras)} mestras")


if __name__ == "__main__":
    main()
