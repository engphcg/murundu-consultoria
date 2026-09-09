#!/usr/bin/env python3
"""Verifica os bloqueios objetivos antes da publicação do site."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


# Exceções externas autorizadas pelo dono e pelo contrato público da página.
# Tudo na PRÓPRIA origem é permitido: canonical, og:url, og:image e qualquer
# asset futuro. Não é exceção, é o site apontando para si mesmo.
ORIGEM_PROPRIA = "https://murundu.eng.br"
ALLOWED_EXTERNAL_URLS = {
    "https://murundu.app.br",  # Software citado com autorização expressa do dono.
}
ALLOWED_CONTACT_PREFIXES = (
    "https://wa.me/",  # Canal de WhatsApp declarado na página.
    "mailto:",  # Canal de e-mail declarado na página.
)
MARKER = "⟨PREENCHER"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1_lines: list[int] = []
        self.images_without_alt: list[int] = []
        self.external_urls: list[tuple[int, str, str]] = []
        self.json_ld_ranges: list[tuple[int, int]] = []
        self._json_ld_start: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        line = self.getpos()[0]
        if tag == "h1":
            self.h1_lines.append(line)
        if tag == "img" and "alt" not in attributes:
            self.images_without_alt.append(line)
        if tag == "script" and attributes.get("type", "").lower() == "application/ld+json":
            self._json_ld_start = line

        for attribute in ("src", "href"):
            value = attributes.get(attribute)
            if value and value.lower().startswith(("http://", "https://")):
                self.external_urls.append((line, attribute, value))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_ld_start is not None:
            self.json_ld_ranges.append((self._json_ld_start, self.getpos()[0]))
            self._json_ld_start = None


def is_allowed_external(url: str) -> bool:
    if url == ORIGEM_PROPRIA or url.startswith(ORIGEM_PROPRIA + "/"):
        return True
    if url in ALLOWED_EXTERNAL_URLS or url.startswith(ALLOWED_CONTACT_PREFIXES):
        return True
    parsed = urlparse(url)
    return parsed.scheme == "mailto"


def check_html(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"{path.name}:1: arquivo obrigatório ausente")
        return

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    parser = PageParser()
    parser.feed(text)

    for number, line in enumerate(lines, start=1):
        if MARKER in line:
            failures.append(f"{path.name}:{number}: marcador de conteúdo pendente")

    for start, end in parser.json_ld_ranges:
        for number in range(start, end + 1):
            if number <= len(lines) and MARKER in lines[number - 1]:
                failures.append(f"{path.name}:{number}: marcador dentro do JSON-LD")

    for line, attribute, url in parser.external_urls:
        if not is_allowed_external(url):
            failures.append(
                f"{path.name}:{line}: URL externa não autorizada em {attribute}: {url}"
            )

    for line in parser.images_without_alt:
        failures.append(f"{path.name}:{line}: elemento <img> sem atributo alt")

    if len(parser.h1_lines) != 1:
        line = parser.h1_lines[0] if parser.h1_lines else 1
        failures.append(
            f"{path.name}:{line}: esperado exatamente um <h1>; encontrados {len(parser.h1_lines)}"
        )

    for number, line in enumerate(lines, start=1):
        match = re.search(r"@import\s+(?:url\()?['\"]?(https?://[^\s)'\"]+)", line, re.I)
        if match and not is_allowed_external(match.group(1)):
            failures.append(
                f"{path.name}:{number}: URL externa não autorizada em @import: {match.group(1)}"
            )


def check_cname(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append("CNAME:1: arquivo obrigatório ausente")
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines != ["murundu.eng.br"]:
        failures.append(
            "CNAME:1: CNAME deve conter exatamente uma linha: murundu.eng.br"
        )


def check_stylesheet(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        failures.append("assets/styles.css:1: arquivo obrigatório ausente")
        return
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = re.search(r"@import\s+(?:url\()?['\"]?(https?://[^\s)'\"]+)", line, re.I)
        if match and not is_allowed_external(match.group(1)):
            failures.append(
                f"assets/styles.css:{number}: URL externa não autorizada em @import: {match.group(1)}"
            )


def main(root: Path | None = None) -> int:
    # No Windows o stdout herda a página de código do console (cp1252 nesta
    # máquina): as mensagens acentuadas saem truncadas para quem lê e quebram
    # com UnicodeDecodeError quem lê pelo cano — foi assim que os testes deste
    # arquivo erravam. O relatório é sempre UTF-8, seja qual for o console.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    base = root or Path(__file__).resolve().parent
    failures: list[str] = []
    check_html(base / "index.html", failures)
    check_html(base / "404.html", failures)
    check_stylesheet(base / "assets" / "styles.css", failures)
    check_cname(base / "CNAME", failures)

    for failure in failures:
        print(f"FALHA: {failure}")
    print(
        f"VERIFICADO: 6 checagens, {len(failures)} falhas "
        "(index.html, 404.html, assets/styles.css, CNAME)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    selected_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    raise SystemExit(main(selected_root))
