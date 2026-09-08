"""Testes comportamentais do verificador de pré-publicação."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "verificar.py"


class VerificadorTests(unittest.TestCase):
    def executar(self, arquivos: dict[str, str]) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            for nome, conteudo in arquivos.items():
                destino = raiz / nome
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(conteudo, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(raiz)],
                text=True,
                capture_output=True,
                encoding="utf-8",
                check=False,
            )

    @staticmethod
    def base() -> dict[str, str]:
        return {
            "index.html": """<!doctype html><html><head>
<link rel="canonical" href="https://murundu.eng.br/">
<meta property="og:url" content="https://murundu.eng.br/">
<link rel="stylesheet" href="assets/styles.css">
<script type="application/ld+json">{"@type":"ProfessionalService"}</script>
</head><body><h1>Murundu</h1><img src="assets/teste.svg" alt=""></body></html>""",
            "404.html": "<!doctype html><html><body><h1>Página não encontrada</h1></body></html>",
            "assets/styles.css": ":root { color: #000; }\n",
            "CNAME": "murundu.eng.br\n",
        }

    def test_aprova_site_valido_e_informa_escopo(self) -> None:
        resultado = self.executar(self.base())
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertIn(
            "VERIFICADO: 6 checagens, 0 falhas (index.html, 404.html, assets/styles.css, CNAME)",
            resultado.stdout,
        )

    def test_reprova_marcador_com_arquivo_e_linha(self) -> None:
        arquivos = self.base()
        arquivos["index.html"] = arquivos["index.html"].replace(
            "<h1>Murundu</h1>", "<h1>Murundu</h1>\n<p>⟨PREENCHER: dado⟩</p>"
        )
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("index.html:7", resultado.stdout)
        self.assertIn("marcador de conteúdo pendente", resultado.stdout)

    def test_reprova_marcador_no_json_ld_separadamente(self) -> None:
        arquivos = self.base()
        arquivos["index.html"] = arquivos["index.html"].replace(
            '"ProfessionalService"', '"ProfessionalService", "name":"⟨PREENCHER: nome⟩"'
        )
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("marcador dentro do JSON-LD", resultado.stdout)

    def test_reprova_url_externa_nao_autorizada(self) -> None:
        arquivos = self.base()
        arquivos["index.html"] = arquivos["index.html"].replace(
            "</body>", '<a href="https://example.com">fora</a></body>'
        )
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("URL externa não autorizada", resultado.stdout)

    def test_reprova_importacao_externa_na_folha(self) -> None:
        arquivos = self.base()
        arquivos["assets/styles.css"] = '@import "https://example.com/style.css";\n'
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("assets/styles.css:1: URL externa não autorizada em @import", resultado.stdout)

    def test_aceita_link_autorizado_do_software(self) -> None:
        arquivos = self.base()
        arquivos["index.html"] = arquivos["index.html"].replace(
            "</body>", '<a href="https://murundu.app.br">Software</a></body>'
        )
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 0, resultado.stdout)

    def test_reprova_imagem_sem_alt(self) -> None:
        arquivos = self.base()
        arquivos["index.html"] = arquivos["index.html"].replace(' alt=""', "")
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("elemento <img> sem atributo alt", resultado.stdout)

    def test_reprova_quantidade_de_h1_diferente_de_um(self) -> None:
        arquivos = self.base()
        arquivos["index.html"] = arquivos["index.html"].replace("</body>", "<h1>Outro</h1></body>")
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("esperado exatamente um <h1>; encontrados 2", resultado.stdout)

    def test_reprova_cname_incorreto(self) -> None:
        arquivos = self.base()
        arquivos["CNAME"] = "outro.example\nlinha-extra\n"
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("CNAME deve conter exatamente uma linha", resultado.stdout)

    def test_reprova_arquivo_ausente(self) -> None:
        arquivos = self.base()
        del arquivos["404.html"]
        resultado = self.executar(arquivos)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("404.html:1: arquivo obrigatório ausente", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
