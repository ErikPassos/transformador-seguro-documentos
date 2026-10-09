from pathlib import Path


TAMANHO_MAXIMO_MB = 20
TAMANHO_MAXIMO_BYTES = TAMANHO_MAXIMO_MB * 1024 * 1024


def validar_pdf(caminho_arquivo):
    """
    Realiza validações iniciais em um arquivo PDF.

    Valida:
    - tipo do argumento recebido;
    - existência do caminho;
    - se o caminho representa um arquivo;
    - extensão permitida;
    - tamanho máximo;
    - assinatura básica de PDF.

    Retorna:
        tuple:
            bool: True quando o arquivo passa nas validações.
            str: mensagem explicativa.
    """

    if not isinstance(caminho_arquivo, (str, Path)):
        return False, (
            "O caminho do arquivo deve ser informado como texto "
            "ou como um objeto Path."
        )

    if not str(caminho_arquivo).strip():
        return False, "O caminho do arquivo não pode estar vazio."

    try:
        caminho = Path(caminho_arquivo)

        if not caminho.exists():
            return False, "O arquivo informado não existe."

        if not caminho.is_file():
            return False, (
                "O caminho informado não representa um arquivo."
            )

        if caminho.suffix.lower() != ".pdf":
            return False, "Apenas arquivos PDF são permitidos."

        tamanho_bytes = caminho.stat().st_size
        tamanho_mb = tamanho_bytes / (1024 * 1024)

        if tamanho_bytes == 0:
            return False, "O arquivo PDF está vazio."

        if tamanho_bytes > TAMANHO_MAXIMO_BYTES:
            return False, (
                f"O arquivo possui {tamanho_mb:.2f} MB. "
                f"O limite permitido é {TAMANHO_MAXIMO_MB} MB."
            )

        with caminho.open("rb") as arquivo:
            inicio_arquivo = arquivo.read(1024)

        if b"%PDF-" not in inicio_arquivo:
            return False, (
                "A extensão é PDF, mas o conteúdo não apresenta "
                "uma assinatura PDF reconhecida."
            )

        return True, (
            "Arquivo validado com sucesso. "
            f"Tamanho: {tamanho_mb:.2f} MB."
        )

    except PermissionError:
        return False, (
            "O programa não possui permissão para acessar o arquivo."
        )

    except OSError as erro:
        return False, (
            "O sistema operacional não conseguiu acessar o arquivo. "
            f"Detalhe técnico: {erro}"
        )

    except Exception as erro:
        return False, (
            "Ocorreu um erro inesperado durante a validação. "
            f"Tipo: {type(erro).__name__}. "
            f"Detalhe técnico: {erro}"
        )