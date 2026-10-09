from pathlib import Path

import pandas as pd
import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect


CONFIGURACOES_EXTRACAO = [
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


def limpar_valor_celula(valor):
    """
    Limpa o conteúdo textual de uma célula.

    Converte valores None em texto vazio e remove
    espaços desnecessários no início e no final.
    """

    if valor is None:
        return ""

    return str(valor).strip()


def extrair_tabelas_pdf(caminho_arquivo):
    """
    Extrai as tabelas encontradas em um arquivo PDF.

    Cada tabela válida é convertida em um DataFrame
    do pandas.

    Retorna:
        tuple:
            bool:
                indica se a extração foi concluída;

            list ou None:
                lista com informações e DataFrames;

            str:
                mensagem explicativa.
    """

    if not isinstance(caminho_arquivo, (str, Path)):
        return (
            False,
            None,
            "O caminho deve ser informado como texto ou objeto Path.",
        )

    if not str(caminho_arquivo).strip():
        return (
            False,
            None,
            "O caminho não pode estar vazio.",
        )

    try:
        caminho = Path(caminho_arquivo)

        if not caminho.exists():
            return (
                False,
                None,
                "O arquivo informado não existe.",
            )

        if not caminho.is_file():
            return (
                False,
                None,
                "O caminho informado não representa um arquivo.",
            )

        if caminho.suffix.lower() != ".pdf":
            return (
                False,
                None,
                "Apenas arquivos PDF são permitidos.",
            )

        tabelas_extraidas = []

        with pdfplumber.open(caminho) as pdf:
            if len(pdf.pages) == 0:
                return (
                    False,
                    None,
                    "O PDF não contém páginas.",
                )

            for numero_pagina, pagina in enumerate(
                pdf.pages,
                start=1,
            ):
                tabelas_da_pagina = []
                nome_estrategia = None

                for estrategia in CONFIGURACOES_EXTRACAO:
                    configuracao = estrategia["configuracao"]

                    tabelas_detectadas = pagina.find_tables(
                        table_settings=configuracao
                    )

                    if len(tabelas_detectadas) > 0:
                        tabelas_da_pagina = tabelas_detectadas
                        nome_estrategia = estrategia["nome"]
                        break

                for numero_tabela, tabela in enumerate(
                    tabelas_da_pagina,
                    start=1,
                ):
                    dados_brutos = tabela.extract() or []

                    linhas_limpas = []

                    for linha in dados_brutos:
                        if linha is None:
                            continue

                        linha_limpa = []

                        for valor in linha:
                            valor_limpo = limpar_valor_celula(
                                valor
                            )

                            linha_limpa.append(valor_limpo)

                        if any(linha_limpa):
                            linhas_limpas.append(linha_limpa)

                    if len(linhas_limpas) < 2:
                        continue

                    cabecalho = linhas_limpas[0]
                    registros = linhas_limpas[1:]

                    cabecalho_ajustado = []

                    for indice, nome_coluna in enumerate(
                        cabecalho,
                        start=1,
                    ):
                        if nome_coluna:
                            cabecalho_ajustado.append(
                                nome_coluna
                            )
                        else:
                            cabecalho_ajustado.append(
                                f"Coluna_{indice}"
                            )

                    dataframe = pd.DataFrame(
                        registros,
                        columns=cabecalho_ajustado,
                    )

                    informacoes_tabela = {
                        "pagina": numero_pagina,
                        "numero_tabela": numero_tabela,
                        "estrategia": nome_estrategia,
                        "quantidade_linhas": len(dataframe),
                        "quantidade_colunas": len(
                            dataframe.columns
                        ),
                        "colunas": dataframe.columns.tolist(),
                        "dataframe": dataframe,
                    }

                    tabelas_extraidas.append(
                        informacoes_tabela
                    )

        quantidade_total = len(tabelas_extraidas)

        if quantidade_total == 0:
            return (
                True,
                [],
                "A extração foi concluída, mas nenhuma tabela "
                "válida foi extraída.",
            )

        return (
            True,
            tabelas_extraidas,
            "Extração concluída. Foram extraídas "
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

    except pd.errors.EmptyDataError:
        return (
            False,
            None,
            "A tabela encontrada não possui dados utilizáveis.",
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
            "Não foi possível extrair as tabelas do PDF. "
            f"Tipo do erro: {type(erro).__name__}. "
            f"Detalhe técnico: {erro}",
        )