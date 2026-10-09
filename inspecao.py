from pathlib import Path

import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect


def inspecionar_pdf(caminho_arquivo):
    """
    Inspeciona a estrutura básica de um arquivo PDF.

    Verifica:
    - se o argumento recebido é válido;
    - se o arquivo existe;
    - se o caminho representa um arquivo;
    - se a extensão é PDF;
    - se o documento pode ser aberto;
    - quantas páginas existem;
    - quais páginas possuem texto extraível;
    - quais páginas não possuem texto extraível.

    Retorna:
        tuple:
            bool: indica se a inspeção foi concluída;
            dict ou None: dados encontrados;
            str: mensagem explicativa.
    """

    if not isinstance(caminho_arquivo, (str, Path)):
        return (
            False,
            None,
            "O caminho deve ser informado como texto ou objeto Path.",
        )

    if not str(caminho_arquivo).strip():
        return False, None, "O caminho não pode estar vazio."

    try:
        caminho = Path(caminho_arquivo)

        if not caminho.exists():
            return False, None, "O arquivo informado não existe."

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

        with pdfplumber.open(caminho) as pdf:
            quantidade_paginas = len(pdf.pages)

            if quantidade_paginas == 0:
                return (
                    False,
                    None,
                    "O PDF não contém páginas.",
                )

            paginas_com_texto = []
            paginas_sem_texto = []
            caracteres_por_pagina = []

            for numero_pagina, pagina in enumerate(
                pdf.pages,
                start=1,
            ):
                texto = pagina.extract_text() or ""
                quantidade_caracteres = len(texto.strip())

                caracteres_por_pagina.append(
                    {
                        "pagina": numero_pagina,
                        "caracteres": quantidade_caracteres,
                    }
                )

                if quantidade_caracteres > 0:
                    paginas_com_texto.append(numero_pagina)
                else:
                    paginas_sem_texto.append(numero_pagina)

            total_caracteres = sum(
                item["caracteres"]
                for item in caracteres_por_pagina
            )

            possivel_pdf_digitalizado = (
                len(paginas_com_texto) == 0
            )

            resultado = {
                "arquivo": caminho.name,
                "quantidade_paginas": quantidade_paginas,
                "paginas_com_texto": paginas_com_texto,
                "paginas_sem_texto": paginas_sem_texto,
                "quantidade_paginas_com_texto": len(
                    paginas_com_texto
                ),
                "quantidade_paginas_sem_texto": len(
                    paginas_sem_texto
                ),
                "total_caracteres": total_caracteres,
                "caracteres_por_pagina": caracteres_por_pagina,
                "possivel_pdf_digitalizado": (
                    possivel_pdf_digitalizado
                ),
            }

            return (
                True,
                resultado,
                "Inspeção do PDF concluída com sucesso.",
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
            "Não foi possível inspecionar o PDF. "
            f"Tipo do erro: {type(erro).__name__}. "
            f"Detalhe técnico: {erro}",
        )