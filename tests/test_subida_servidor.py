"""Teste de subida real do servidor (processo uvicorn separado, porta TCP real).

Critério de aceite: "o avaliador executa o script de inicialização, a
aplicação sobe e fica acessível no navegador sem passos manuais adicionais".

Este teste não invoca run.bat/run.sh diretamente (eles criam um venv e
reinstalam dependências, o que seria lento e invasivo dentro da suíte);
em vez disso, sobe `uvicorn app.main:app` exatamente como os scripts fazem
na última linha, num processo real, e faz requisições HTTP reais via
`urllib` contra `http://127.0.0.1:<porta>`. run.bat/run.sh foram revisados
manualmente: ambos resolvem o diretório do projeto, criam/usam .venv,
instalam requirements.txt e terminam com `uvicorn app.main:app --host
0.0.0.0 --port 8000`, que é o comando aqui exercitado de fato.
"""

import json
import socket
import subprocess
import sys
import time
import unittest
import urllib.request
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent


def _porta_livre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TesteSubidaRealDoServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.porta = _porta_livre()
        cls.processo = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(cls.porta)],
            cwd=str(RAIZ_PROJETO),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        cls._aguardar_servidor_pronto()

    @classmethod
    def _aguardar_servidor_pronto(cls, tentativas: int = 50, intervalo: float = 0.2):
        url = f"http://127.0.0.1:{cls.porta}/"
        for _ in range(tentativas):
            if cls.processo.poll() is not None:
                saida = cls.processo.stdout.read() if cls.processo.stdout else ""
                raise RuntimeError(f"uvicorn encerrou prematuramente:\n{saida}")
            try:
                with urllib.request.urlopen(url, timeout=1):
                    return
            except Exception:
                time.sleep(intervalo)
        raise TimeoutError("Servidor uvicorn não respondeu a tempo.")

    @classmethod
    def tearDownClass(cls):
        cls.processo.terminate()
        try:
            cls.processo.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.processo.kill()
            cls.processo.wait(timeout=5)

    def test_interface_acessivel_na_raiz(self):
        url = f"http://127.0.0.1:{self.porta}/"
        with urllib.request.urlopen(url, timeout=5) as resposta:
            self.assertEqual(resposta.status, 200)
            corpo = resposta.read().decode("utf-8")
            self.assertIn("Alinhamento de Duas Sequências", corpo)

    def test_api_alinhar_responde_sobre_http_real(self):
        url = f"http://127.0.0.1:{self.porta}/api/alinhar"
        corpo = json.dumps(
            {"seq1": "ACGTAC", "seq2": "ACGTTC", "modo": "GLOBAL", "match": 2, "mismatch": -1, "gap": -2}
        ).encode("utf-8")
        requisicao = urllib.request.Request(
            url, data=corpo, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(requisicao, timeout=5) as resposta:
            self.assertEqual(resposta.status, 200)
            dados = json.loads(resposta.read().decode("utf-8"))
            self.assertEqual(dados["score"], 9)


if __name__ == "__main__":
    unittest.main()
