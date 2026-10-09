from deteccao_tabelas import detectar_tabelas_pdf
from exportacao_excel import exportar_tabelas_excel
from extracao_tabelas import extrair_tabelas_pdf
from inspecao import inspecionar_pdf
from validacao import validar_pdf


# --------------------------------------------------
# ARQUIVO QUE SERÁ PROCESSADO
# --------------------------------------------------

caminho_pdf = "entrada/tabela_teste.pdf"


# --------------------------------------------------
# ETAPA 1: VALIDAÇÃO DO ARQUIVO
# --------------------------------------------------

arquivo_valido, mensagem_validacao = validar_pdf(
    caminho_pdf
)

print(mensagem_validacao)


if not arquivo_valido:
    print("O processamento foi interrompido.")

else:

    # --------------------------------------------------
    # ETAPA 2: INSPEÇÃO DO PDF
    # --------------------------------------------------

    (
        inspecao_concluida,
        dados_inspecao,
        mensagem_inspecao,
    ) = inspecionar_pdf(caminho_pdf)

    print(mensagem_inspecao)


    if not inspecao_concluida:
        print("O processamento foi interrompido.")

    else:

        # --------------------------------------------------
        # APRESENTAÇÃO DO RESUMO DA INSPEÇÃO
        # --------------------------------------------------

        print()
        print("RESUMO DA INSPEÇÃO")

        print(
            f"Arquivo: "
            f"{dados_inspecao['arquivo']}"
        )

        print(
            f"Quantidade de páginas: "
            f"{dados_inspecao['quantidade_paginas']}"
        )

        print(
            f"Páginas com texto: "
            f"{dados_inspecao['paginas_com_texto']}"
        )

        print(
            f"Páginas sem texto: "
            f"{dados_inspecao['paginas_sem_texto']}"
        )

        print(
            f"Total de caracteres extraídos: "
            f"{dados_inspecao['total_caracteres']}"
        )

        print(
            f"Possível PDF digitalizado: "
            f"{dados_inspecao['possivel_pdf_digitalizado']}"
        )


        # --------------------------------------------------
        # ETAPA 3: DETECÇÃO DE TABELAS
        # --------------------------------------------------

        (
            deteccao_concluida,
            tabelas_detectadas,
            mensagem_deteccao,
        ) = detectar_tabelas_pdf(caminho_pdf)

        print()
        print(mensagem_deteccao)


        if not deteccao_concluida:
            print("O processamento foi interrompido.")

        elif not tabelas_detectadas:
            print(
                "O documento poderá exigir outra "
                "estratégia de extração."
            )

        else:

            # --------------------------------------------------
            # APRESENTAÇÃO DAS TABELAS DETECTADAS
            # --------------------------------------------------

            print()
            print("TABELAS ENCONTRADAS")

            for tabela_detectada in tabelas_detectadas:
                estrategia = tabela_detectada.get(
                    "estrategia",
                    "não informada",
                )

                print(
                    f"Página "
                    f"{tabela_detectada['pagina']} | "
                    f"Tabela "
                    f"{tabela_detectada['numero_tabela']} | "
                    f"Linhas: "
                    f"{tabela_detectada['quantidade_linhas']} | "
                    f"Colunas: "
                    f"{tabela_detectada['quantidade_colunas']} | "
                    f"Estratégia: {estrategia}"
                )


            # --------------------------------------------------
            # ETAPA 4: EXTRAÇÃO DAS TABELAS
            # --------------------------------------------------

            (
                extracao_concluida,
                tabelas_extraidas,
                mensagem_extracao,
            ) = extrair_tabelas_pdf(caminho_pdf)

            print()
            print(mensagem_extracao)


            if not extracao_concluida:
                print(
                    "O processamento foi interrompido."
                )

            elif not tabelas_extraidas:
                print(
                    "Nenhuma tabela válida foi extraída."
                )

            else:

                # --------------------------------------------------
                # APRESENTAÇÃO DA PRÉVIA
                # --------------------------------------------------

                print()
                print("PRÉVIA DAS TABELAS EXTRAÍDAS")

                for tabela_extraida in tabelas_extraidas:
                    print()
                    print("-" * 70)

                    print(
                        f"Página: "
                        f"{tabela_extraida['pagina']}"
                    )

                    print(
                        f"Tabela: "
                        f"{tabela_extraida['numero_tabela']}"
                    )

                    print(
                        f"Estratégia: "
                        f"{tabela_extraida['estrategia']}"
                    )

                    print(
                        f"Linhas de dados: "
                        f"{tabela_extraida['quantidade_linhas']}"
                    )

                    print(
                        f"Quantidade de colunas: "
                        f"{tabela_extraida['quantidade_colunas']}"
                    )

                    print(
                        f"Colunas: "
                        f"{tabela_extraida['colunas']}"
                    )

                    print()
                    print(
                        tabela_extraida["dataframe"]
                    )


                # --------------------------------------------------
                # ETAPA 5: EXPORTAÇÃO PARA EXCEL
                # --------------------------------------------------

                (
                    exportacao_concluida,
                    caminho_excel,
                    mensagem_exportacao,
                ) = exportar_tabelas_excel(
                    tabelas_extraidas,
                    caminho_pdf,
                    pasta_saida="saida",
                )

                print()
                print(mensagem_exportacao)


                if exportacao_concluida:
                    print(
                        "Arquivo Excel criado em: "
                        f"{caminho_excel}"
                    )

                else:
                    print(
                        "O arquivo Excel não foi criado."
                    )