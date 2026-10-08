#!/usr/bin/env python3
"""Troca o descritor do logotipo: "ANÁLISES AMBIENTAIS" -> "CONSULTORIA AMBIENTAL".

O logotipo da marca é vetor traçado da arte: a palavra "Murundu" e as letras
do descritor são caminhos, não texto. Para mudar o descritor sem pedir arte
nova, as letras antigas são descartadas e as novas são DESENHADAS COMO
CONTORNOS a partir da fonte Inter SemiBold (assets/fonts/og/). Contorno, e não
<text>, de propósito: <text> faria o logotipo mudar de letra conforme a máquina
(o problema já registrado no README da marca).

Fica intacto, copiado byte a byte do original: a palavra "Murundu", os dois
traços laterais e as cores. A nova linha ocupa o mesmo vão (x 125..806) e a
mesma linha de base (y 236,5) do descritor antigo, com a mesma altura de caixa
alta (26,5); o espaçamento entre letras é calculado para fechar o vão.

    python assets/gerar_logotipo.py     # requer: pip install fonttools

Entrada:  assets/marca/fonte/murundu_logotipo{,_claro}.svg  (originais da marca)
Saída:    assets/marca/murundu_logotipo{,_claro}.svg
"""

from __future__ import annotations

import re
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

RAIZ = Path(__file__).resolve().parent
FONTE_SVG = RAIZ / "marca" / "fonte"
SAIDA = RAIZ / "marca"
FONTE_TIPO = RAIZ / "fonts" / "og" / "inter-latin-600-normal.woff"

TEXTO = "CONSULTORIA AMBIENTAL"
ARIA_ANTIGO = "Murundu — Análises Ambientais"
ARIA_NOVO = "Murundu — Consultoria Ambiental"

# Medido no vetor original (descritor "ANÁLISES AMBIENTAIS").
X0, X1 = 125.1, 805.8  # primeira e última letra
BASE_Y = 236.5  # linha de base
ALTURA_CAIXA_ALTA = 26.5  # y 210 .. 236,5


def contornos(texto: str) -> str:
    fonte = TTFont(str(FONTE_TIPO))
    cmap = fonte.getBestCmap()
    glifos = fonte.getGlyphSet()
    cap = fonte["OS/2"].sCapHeight
    escala = ALTURA_CAIXA_ALTA / cap

    nomes = [cmap[ord(c)] for c in texto]
    avancos = [glifos[n].width * escala for n in nomes]
    # Espaçamento entre letras que fecha exatamente o vão X0..X1. A última
    # letra não leva espaçamento depois dela.
    sobra = (X1 - X0) - sum(avancos)
    track = sobra / (len(nomes) - 1)

    x = X0
    partes: list[str] = []
    for nome, avanco in zip(nomes, avancos):
        pen = SVGPathPen(glifos, ntos=lambda v: f"{v:.2f}")
        # fonte: y para cima; SVG: y para baixo -> inverte e posiciona.
        glifos[nome].draw(TransformPen(pen, (escala, 0, 0, -escala, x, BASE_Y)))
        d = pen.getCommands()
        if d:
            partes.append(d)
        x += avanco + track
    return " ".join(partes)


def converter(origem: Path, destino: Path) -> None:
    svg = origem.read_text(encoding="utf-8")
    caminhos = list(re.finditer(r'(<path fill="(#[0-9A-Fa-f]{6})" fill-rule="evenodd" d=")([^"]+)("/>)', svg))
    if len(caminhos) != 2:
        raise SystemExit(f"{origem.name}: esperados 2 caminhos, achei {len(caminhos)}")
    descritor = caminhos[1]
    subs = [s.strip() for s in re.split(r"(?=M )", descritor.group(3).strip()) if s.strip()]

    def largura(s: str) -> float:
        n = [float(v) for v in re.findall(r"-?\d+\.?\d*", s)]
        return max(n[0::2]) - min(n[0::2])

    tracos = [s for s in subs if largura(s) > 60]
    if len(tracos) != 2:
        raise SystemExit(f"{origem.name}: esperados 2 traços laterais, achei {len(tracos)}")

    novo_d = " ".join(tracos) + " " + contornos(TEXTO)
    svg = svg[: descritor.start(3)] + novo_d + svg[descritor.end(3) :]
    if ARIA_ANTIGO not in svg:
        raise SystemExit(f"{origem.name}: aria-label esperado não encontrado")
    svg = svg.replace(ARIA_ANTIGO, ARIA_NOVO)
    destino.write_text(svg, encoding="utf-8")
    print(f"GERADO: {destino.name} — {destino.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    for nome in ("murundu_logotipo.svg", "murundu_logotipo_claro.svg"):
        converter(FONTE_SVG / nome, SAIDA / nome)
