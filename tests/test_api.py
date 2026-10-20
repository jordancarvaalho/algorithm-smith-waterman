"""Teste de integração HTTP real contra a aplicação FastAPI.

Usa fastapi.testclient.TestClient (ASGI real, sem mocks de rede) para
exercitar os quatro endpoints do contrato e a entrega dos estáticos.
Cobre também os critérios de aceite que são, na prática, testes de
integração: comparação, erro de quantidade de arquivo, exportação completa.
"""

import csv
import io
import re
import unittest
import zipfile

from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)

CORPO_CANONICO = {
    "seq1": "ACGTAC",
    "seq2": "ACGTTC",
    "modo": "GLOBAL",
    "match": 2,
    "mismatch": -1,
    "gap": -2,
}


class TesteEndpointAlinhar(unittest.TestCase):
    def test_caso_canonico_devolve_200_e_resultado_do_contrato(self):
        resposta = cliente.post("/api/alinhar", json=CORPO_CANONICO)
        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.json()
        self.assertEqual(corpo["score"], 9)
        self.assertEqual(corpo["tamanho"], 6)
        self.assertEqual(corpo["alinhamento"]["marcacao"], "||||.|")
        self.assertEqual(corpo["inicio"], [6, 6])
        self.assertEqual(corpo["avisos"], [])

    def test_base_invalida_devolve_422_sem_processar(self):
        corpo = dict(CORPO_CANONICO, seq1="ACGTAXTG")
        resposta = cliente.post("/api/alinhar", json=corpo)
        self.assertEqual(resposta.status_code, 422)
        erros = resposta.json()["erros"]
        self.assertEqual(len(erros), 1)
        self.assertEqual(erros[0]["codigo"], "base_invalida")
        self.assertIn('"X"', erros[0]["mensagem"])
        self.assertIn("posição 6", erros[0]["mensagem"])

    def test_seq2_vazia_e_gap_nao_numerico_juntos(self):
        corpo = dict(CORPO_CANONICO, seq2="", gap="abc")
        resposta = cliente.post("/api/alinhar", json=corpo)
        self.assertEqual(resposta.status_code, 422)
        codigos = {erro["codigo"] for erro in resposta.json()["erros"]}
        self.assertIn("seq_vazia", codigos)
        self.assertIn("parametro_nao_numerico", codigos)

    def test_match_negativo_gera_aviso_e_processa(self):
        corpo = dict(CORPO_CANONICO, match=-1)
        resposta = cliente.post("/api/alinhar", json=corpo)
        self.assertEqual(resposta.status_code, 200)
        corpo_resposta = resposta.json()
        codigos_aviso = {a["codigo"] for a in corpo_resposta["avisos"]}
        self.assertIn("match_nao_positivo", codigos_aviso)
        self.assertIsNotNone(corpo_resposta["score"])

    def test_normalizacao_de_minusculas_e_comprimentos_diferentes(self):
        corpo = dict(CORPO_CANONICO, seq1="acgta", seq2="TGCATG")
        resposta = cliente.post("/api/alinhar", json=corpo)
        self.assertEqual(resposta.status_code, 200)
        corpo_resposta = resposta.json()
        self.assertEqual(corpo_resposta["seq1"], "ACGTA")
        self.assertEqual(corpo_resposta["seq2"], "TGCATG")


class TesteEndpointComparar(unittest.TestCase):
    """Critério: /api/comparar devolve global e local sobre a mesma entrada."""

    def test_comparar_devolve_global_e_local(self):
        corpo = {k: v for k, v in CORPO_CANONICO.items() if k != "modo"}
        resposta = cliente.post("/api/comparar", json=corpo)
        self.assertEqual(resposta.status_code, 200)
        corpo_resposta = resposta.json()
        self.assertIn("global", corpo_resposta)
        self.assertIn("local", corpo_resposta)
        self.assertEqual(corpo_resposta["global"]["modo"], "GLOBAL")
        self.assertEqual(corpo_resposta["local"]["modo"], "LOCAL")
        self.assertEqual(corpo_resposta["global"]["score"], 9)


class TesteEndpointArquivo(unittest.TestCase):
    def test_duas_sequencias_preenche_campos(self):
        conteudo = b">seq1\nACGTAC\n>seq2\nACGTTC\n"
        resposta = cliente.post(
            "/api/arquivo", files={"arquivo": ("duas.fasta", conteudo, "text/plain")}
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"seq1": "ACGTAC", "seq2": "ACGTTC"})

    def test_tres_sequencias_devolve_erro_seq_quantidade(self):
        conteudo = b">seq1\nACGT\n>seq2\nACGG\n>seq3\nACGA\n"
        resposta = cliente.post(
            "/api/arquivo", files={"arquivo": ("tres.fasta", conteudo, "text/plain")}
        )
        self.assertEqual(resposta.status_code, 422)
        erros = resposta.json()["erros"]
        self.assertEqual(erros[0]["codigo"], "seq_quantidade")


class TesteEndpointExportar(unittest.TestCase):
    """Critério: exportação devolve os 4 arquivos com os nomes exatos e conteúdo correspondente."""

    def test_exportar_txt(self):
        resposta = cliente.post("/api/exportar/txt", json=CORPO_CANONICO)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            'filename="alinhamento_ACGTAC_ACGTTC.txt"',
            resposta.headers["content-disposition"],
        )
        self.assertIn("Score final: 9", resposta.content.decode("utf-8-sig"))

    def test_exportar_csv_pontuacao_bate_com_resultado_da_tela(self):
        resposta_tela = cliente.post("/api/alinhar", json=CORPO_CANONICO)
        matriz_tela = resposta_tela.json()["matriz"]

        resposta_export = cliente.post("/api/exportar/csv_pontuacao", json=CORPO_CANONICO)
        self.assertEqual(resposta_export.status_code, 200)
        texto = resposta_export.content.decode("utf-8-sig")
        linhas = list(csv.reader(io.StringIO(texto)))
        matriz_do_csv = [[int(v) for v in linha[1:]] for linha in linhas[1:]]
        self.assertEqual(matriz_do_csv, matriz_tela)

    def test_exportar_zip_contem_quatro_arquivos(self):
        resposta = cliente.post("/api/exportar/zip", json=CORPO_CANONICO)
        self.assertEqual(resposta.status_code, 200)
        with zipfile.ZipFile(io.BytesIO(resposta.content)) as zf:
            self.assertEqual(
                set(zf.namelist()),
                {
                    "alinhamento_ACGTAC_ACGTTC.txt",
                    "matriz_pontuacao_ACGTAC_ACGTTC.csv",
                    "matriz_traceback_ACGTAC_ACGTTC.csv",
                    "alinhamento_ACGTAC_ACGTTC.csv",
                },
            )

    def test_exportar_comparacao_zip(self):
        corpo = {k: v for k, v in CORPO_CANONICO.items() if k != "modo"}
        resposta = cliente.post("/api/exportar/comparacao_zip", json=corpo)
        self.assertEqual(resposta.status_code, 200)
        with zipfile.ZipFile(io.BytesIO(resposta.content)) as zf:
            nomes = set(zf.namelist())
            self.assertIn("matriz_pontuacao_global_ACGTAC_ACGTTC.csv", nomes)
            self.assertIn("matriz_pontuacao_local_ACGTAC_ACGTTC.csv", nomes)

    def test_exportar_com_entrada_invalida_devolve_422(self):
        corpo = dict(CORPO_CANONICO, seq1="ACGTAXTG")
        resposta = cliente.post("/api/exportar/csv_pontuacao", json=corpo)
        self.assertEqual(resposta.status_code, 422)


class TesteEstaticos(unittest.TestCase):
    """Critério: GET / serve web/index.html; o restante de web/ é servido na raiz."""

    def test_raiz_serve_index_html(self):
        resposta = cliente.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("text/html", resposta.headers["content-type"])
        self.assertIn("Alinhamento de Duas Sequências", resposta.text)

    # Content-types aceitos por extensão. O bundle Vite muda os nomes dos
    # arquivos (hash) a cada build, então o teste não pode depender de um
    # nome fixo; ele extrai os assets referenciados pelo próprio HTML servido.
    _CONTENT_TYPES_ACEITOS = {
        ".js": ("text/javascript", "application/javascript"),
        ".css": ("text/css",),
        ".svg": ("image/svg+xml",),
        ".woff2": ("font/woff2",),
        ".woff": ("font/woff",),
        ".png": ("image/png",),
        ".json": ("application/json",),
    }

    def test_assets_referenciados_pelo_html_sao_servidos(self):
        """Critério: todo asset local referenciado pelo index.html (src/href)
        responde 200 com um content-type condizente com sua extensão. Como os
        caminhos vêm do próprio HTML servido, o teste continua válido mesmo
        depois de um rebuild que troque os nomes com hash."""
        resposta = cliente.get("/")
        self.assertEqual(resposta.status_code, 200)

        caminhos = set(
            re.findall(r'(?:src|href)="(/[^"]+)"', resposta.text)
        )
        self.assertTrue(
            caminhos, "nenhum asset local (src/href) encontrado no HTML servido"
        )

        for caminho in caminhos:
            with self.subTest(caminho=caminho):
                resposta_asset = cliente.get(caminho)
                self.assertEqual(resposta_asset.status_code, 200)

                extensao = "." + caminho.rsplit(".", 1)[-1].lower()
                tipos_aceitos = self._CONTENT_TYPES_ACEITOS.get(extensao)
                if tipos_aceitos:
                    content_type = resposta_asset.headers["content-type"]
                    self.assertTrue(
                        any(content_type.startswith(t) for t in tipos_aceitos),
                        f"content-type inesperado para {caminho}: {content_type}",
                    )


if __name__ == "__main__":
    unittest.main()
