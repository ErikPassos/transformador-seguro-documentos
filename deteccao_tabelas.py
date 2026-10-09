from pathlib import Path

import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect


CONFIGURACOES_DETECCAO = [
    {
        "nome": "linhas",
        "configuracao": {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
        },
    },
    {
        "nome": "texto",
        "configuracao": {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "min_words_vertical": 3,
            "min_words_horizontal": 1,
        },
    },
]


def detectar_tabelas_pdf(caminho_arquivo):
    """
    Detecta tabelas em todas as páginas de um arquivo PDF.

    A função testa duas estratégias:

    1. linhas:
       procura tabelas delimitadas por bordas horizontais
       e verticais;

    2. texto:
       procura tabelas formadas pelo alinhamento das palavras.

    Parâmetro:
        caminho_arquivo:
            caminho do arquivo PDF que será analisado.

    Retorno:
        tuple:
            bool:
                indica se a operação foi concluída;

            list ou None:
                contém informações sobre as tabelas encontradas;

            str:
                mensagem explicativa sobre o resultado.
    """

    # Valida o tipo do valor recebido.
    if not isinstance(caminho_arquivo, (str, Path)):
        return (
            False,
            None,
            "O caminho deve ser informado como texto ou objeto Path.",
        )

    # Rejeita textos vazios ou formados somente por espaços.
    if not str(caminho_arquivo).strip():
        return (
            False,
            None,
            "O caminho não pode estar vazio.",
        )

    try:
        caminho = Path(caminho_arquivo)

        # Verifica se o caminho existe.
        if not caminho.exists():
            return (
                False,
                None,
                "O arquivo informado não existe.",
            )

        # Verifica se o caminho representa um arquivo.
        if not caminho.is_file():
            return (
                False,
                None,
                "O caminho informado não representa um arquivo.",
            )

        # Verifica se a extensão é PDF.
        if caminho.suffix.lower() != ".pdf":
            return (
                False,
                None,
                "Apenas arquivos PDF são permitidos.",
            )

        # Armazena as informações das tabelas encontradas.
        tabelas_encontradas = []

        # Abre o PDF e garante o fechamento automático.
        with pdfplumber.open(caminho) as pdf:

            # Verifica se o PDF contém páginas.
            if len(pdf.pages) == 0:
                return (
                    False,
                    None,
                    "O PDF não contém páginas.",
                )

            # Percorre todas as páginas do PDF.
            for numero_pagina, pagina in enumerate(
                pdf.pages,
                start=1,
            ):
                tabelas_da_pagina = []
                nome_estrategia = None

                # Testa as estratégias de detecção.
                for estrategia in CONFIGURACOES_DETECCAO:
                    configuracao = estrategia["configuracao"]

                    tabelas_detectadas = pagina.find_tables(
                        table_settings=configuracao
                    )

                    # Se encontrar alguma tabela, guarda o resultado.
                    if len(tabelas_detectadas) > 0:
                        tabelas_da_pagina = tabelas_detectadas
                        nome_estrategia = estrategia["nome"]

                        # Não é necessário testar outra estratégia
                        # depois que uma delas encontra tabelas.
                        break

                # Percorre as tabelas encontradas na página atual.
                for numero_tabela, tabela in enumerate(
                    tabelas_da_pagina,
                    start=1,
                ):
                    dados_tabela = tabela.extract() or []

                    linhas_validas = []

                    # Descarta linhas representadas por None.
                    for linha in dados_tabela:
                        if linha is not None:
                            linhas_validas.append(linha)

                    quantidade_linhas = len(linhas_validas)
                    quantidade_colunas = 0

                    # Descobre a maior quantidade de colunas.
                    for linha in linhas_validas:
                        if len(linha) > quantidade_colunas:
                            quantidade_colunas = len(linha)

                    informacoes_tabela = {
                        "pagina": numero_pagina,
                        "numero_tabela": numero_tabela,
                        "quantidade_linhas": quantidade_linhas,
                        "quantidade_colunas": quantidade_colunas,
                        "estrategia": nome_estrategia,
                        "area": tabela.bbox,
                    }

                    tabelas_encontradas.append(
                        informacoes_tabela
                    )

        quantidade_total = len(tabelas_encontradas)

        # A operação pode funcionar mesmo sem localizar tabelas.
        if quantidade_total == 0:
            return (
                True,
                [],
                "A detecção foi concluída, mas nenhuma tabela "
                "foi encontrada pelas estratégias disponíveis.",
            )

        return (
            True,
            tabelas_encontradas,
            "Detecção concluída. Foram encontradas "
            f"{quantidade_total} tabela(s).",
        )

    except PDFPasswordIncorrect:
        return (
            False,
            None,
            "O PDF está protegido por senha.",
        )

    except PermissionError:
        return (
            False,
            None,
            "O programa não possui permissão para acessar o PDF.",
        )

    except OSError as erro:
        return (
            False,
            None,
            "O sistema operacional não conseguiu acessar o PDF. "
            f"Detalhe técnico: {erro}",
        )

    except Exception as erro:
        return (
            False,
            None,
            "Não foi possível detectar tabelas no PDF. "
            f"Tipo do erro: {type(erro).__name__}. "
            f"Detalhe técnico: {erro}",
        )