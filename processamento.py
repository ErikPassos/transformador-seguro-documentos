from deteccao_tabelas import detectar_tabelas_pdf
from exportacao_excel import exportar_tabelas_excel
from extracao_tabelas import extrair_tabelas_pdf
from inspecao import inspecionar_pdf
from validacao import validar_pdf


def processar_pdf(
    caminho_pdf,
    pasta_saida,
    atualizar_status=None,
):
    """
    Executa todas as etapas da conversão de PDF para Excel.

    Parâmetros:
        caminho_pdf:
            arquivo PDF que será processado;

        pasta_saida:
            pasta onde o Excel será criado;

        atualizar_status:
            função opcional usada pela interface para
            apresentar o andamento do processamento.

    Retorna:
        tuple:
            bool:
                True quando a conversão for concluída;

            Path ou None:
                caminho do Excel criado;

            str:
                mensagem final.
    """

    def informar_status(mensagem):
        if atualizar_status is not None:
            atualizar_status(mensagem)

    informar_status("Validando o arquivo PDF...")

    arquivo_valido, mensagem_validacao = validar_pdf(
        caminho_pdf
    )

    if not arquivo_valido:
        return (
            False,
            None,
            mensagem_validacao,
        )

    informar_status(
        "Arquivo validado.\n"
        "Inspecionando o documento..."
    )

    (
        inspecao_concluida,
        dados_inspecao,
        mensagem_inspecao,
    ) = inspecionar_pdf(caminho_pdf)

    if not inspecao_concluida:
        return (
            False,
            None,
            mensagem_inspecao,
        )

    if dados_inspecao["possivel_pdf_digitalizado"]:
        return (
            False,
            None,
            "O documento não possui texto extraível. "
            "Esse arquivo poderá exigir OCR.",
        )

    informar_status(
        "Documento inspecionado.\n"
        "Procurando tabelas..."
    )

    (
        deteccao_concluida,
        tabelas_detectadas,
        mensagem_deteccao,
    ) = detectar_tabelas_pdf(caminho_pdf)

    if not deteccao_concluida:
        return (
            False,
            None,
            mensagem_deteccao,
        )

    if not tabelas_detectadas:
        return (
            False,
            None,
            "Nenhuma tabela foi encontrada no PDF.",
        )

    quantidade_detectada = len(
        tabelas_detectadas
    )

    informar_status(
        f"{quantidade_detectada} tabela(s) detectada(s).\n"
        "Extraindo o conteúdo..."
    )

    (
        extracao_concluida,
        tabelas_extraidas,
        mensagem_extracao,
    ) = extrair_tabelas_pdf(caminho_pdf)

    if not extracao_concluida:
        return (
            False,
            None,
            mensagem_extracao,
        )

    if not tabelas_extraidas:
        return (
            False,
            None,
            "Nenhuma tabela válida foi extraída.",
        )

    informar_status(
        "Tabelas extraídas.\n"
        "Criando o arquivo Excel..."
    )

    (
        exportacao_concluida,
        caminho_excel,
        mensagem_exportacao,
    ) = exportar_tabelas_excel(
        tabelas_extraidas,
        caminho_pdf,
        pasta_saida=pasta_saida,
    )

    if not exportacao_concluida:
        return (
            False,
            None,
            mensagem_exportacao,
        )

    quantidade_extraida = len(
        tabelas_extraidas
    )

    mensagem_final = (
        "Conversão concluída com sucesso.\n"
        f"Tabelas exportadas: {quantidade_extraida}\n"
        f"Arquivo criado: {caminho_excel}"
    )

    informar_status(mensagem_final)

    return (
        True,
        caminho_excel,
        mensagem_final,
    )