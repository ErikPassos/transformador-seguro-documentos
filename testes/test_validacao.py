import tempfile
import unittest
from pathlib import Path

from validacao import (
    TAMANHO_MAXIMO_BYTES,
    validar_pdf,
)


class TestarValidacaoPdf(unittest.TestCase):

    def setUp(self):
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.pasta_teste = Path(self.diretorio_temporario.name)

    def tearDown(self):
        self.diretorio_temporario.cleanup()

    def criar_arquivo(self, nome, conteudo=b""):
        caminho = self.pasta_teste / nome
        caminho.write_bytes(conteudo)
        return caminho

    def test_pdf_valido_deve_ser_aceito(self):
        caminho = self.criar_arquivo(
            "documento.pdf",
            b"%PDF-1.7\nConteudo de teste",
        )

        valido, mensagem = validar_pdf(caminho)

        self.assertTrue(valido)
        self.assertIn(
            "Arquivo validado com sucesso",
            mensagem,
        )

    def test_pdf_com_extensao_maiuscula_deve_ser_aceito(self):
        caminho = self.criar_arquivo(
            "documento.PDF",
            b"%PDF-1.7\nConteudo de teste",
        )

        valido, _ = validar_pdf(caminho)

        self.assertTrue(valido)

    def test_arquivo_inexistente_deve_ser_rejeitado(self):
        caminho = self.pasta_teste / "nao_existe.pdf"

        valido, mensagem = validar_pdf(caminho)

        self.assertFalse(valido)
        self.assertEqual(
            mensagem,
            "O arquivo informado não existe.",
        )

    def test_diretorio_deve_ser_rejeitado(self):
        valido, mensagem = validar_pdf(
            self.pasta_teste
        )

        self.assertFalse(valido)
        self.assertEqual(
            mensagem,
            "O caminho informado não representa um arquivo.",
        )

    def test_extensao_diferente_de_pdf_deve_ser_rejeitada(self):
        caminho = self.criar_arquivo(
            "documento.txt",
            b"Arquivo de texto",
        )

        valido, mensagem = validar_pdf(caminho)

        self.assertFalse(valido)
        self.assertEqual(
            mensagem,
            "Apenas arquivos PDF são permitidos.",
        )

    def test_arquivo_vazio_deve_ser_rejeitado(self):
        caminho = self.criar_arquivo(
            "vazio.pdf",
            b"",
        )

        valido, mensagem = validar_pdf(caminho)

        self.assertFalse(valido)
        self.assertEqual(
            mensagem,
            "O arquivo PDF está vazio.",
        )

    def test_pdf_falso_deve_ser_rejeitado(self):
        caminho = self.criar_arquivo(
            "falso.pdf",
            b"Este arquivo nao e um PDF",
        )

        valido, mensagem = validar_pdf(caminho)

        self.assertFalse(valido)
        self.assertIn(
            "assinatura PDF",
            mensagem,
        )

    def test_arquivo_acima_do_limite_deve_ser_rejeitado(self):
        caminho = self.pasta_teste / "grande.pdf"

        with caminho.open("wb") as arquivo:
            arquivo.write(b"%PDF-")
            arquivo.seek(TAMANHO_MAXIMO_BYTES)
            arquivo.write(b"0")

        valido, mensagem = validar_pdf(caminho)

        self.assertFalse(valido)
        self.assertIn(
            "limite permitido",
            mensagem,
        )

    def test_caminho_vazio_deve_ser_rejeitado(self):
        valido, mensagem = validar_pdf("")

        self.assertFalse(valido)
        self.assertEqual(
            mensagem,
            "O caminho do arquivo não pode estar vazio.",
        )

    def test_tipo_invalido_deve_ser_rejeitado(self):
        valido, mensagem = validar_pdf(None)

        self.assertFalse(valido)
        self.assertIn(
            "deve ser informado como texto",
            mensagem,
        )


if __name__ == "__main__":
    unittest.main()