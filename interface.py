import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from processamento import processar_pdf


class InterfaceTransformador:
    def __init__(self, janela):
        self.janela = janela
        self.caminho_excel_criado = None

        self.janela.title(
            "Transformador Seguro de Documentos - PMBA/DEPLAN/CPG"
        )

        self.janela.geometry("760x540")
        self.janela.minsize(680, 500)

        self.caminho_pdf = tk.StringVar()

        self.pasta_saida = tk.StringVar(
            value=str(Path("saida").resolve())
        )

        self.criar_estilos()
        self.criar_componentes()

    def criar_estilos(self):
        estilo = ttk.Style()

        estilo.configure(
            "Titulo.TLabel",
            font=("Segoe UI", 18, "bold"),
        )

        estilo.configure(
            "Subtitulo.TLabel",
            font=("Segoe UI", 10),
            foreground="#555555",
        )

        estilo.configure(
            "Acao.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=10,
        )

    def criar_componentes(self):
        quadro_principal = ttk.Frame(
            self.janela,
            padding=24,
        )

        quadro_principal.pack(
            fill="both",
            expand=True,
        )

        titulo = ttk.Label(
            quadro_principal,
            text="Transformador Seguro de Documentos - PMBA/DEPLAN/CPG",
            style="Titulo.TLabel",
        )

        titulo.pack(
            anchor="w",
            pady=(0, 4),
        )

        subtitulo = ttk.Label(
            quadro_principal,
            text=(
                "Selecione um PDF com tabelas "
                "e converta o conteúdo para Excel.\n " \
                "Desenvolvido por SD PM Erik Bonifácio - Mat:92.037.339\n" \
                "email:erik.fernando@pm.ba.gov.br - Auxiliar do DEPLAN/CPG"
            ),
            style="Subtitulo.TLabel",
        )

        subtitulo.pack(
            anchor="w",
            pady=(0, 24),
        )

        quadro_pdf = ttk.LabelFrame(
            quadro_principal,
            text="Arquivo PDF",
            padding=14,
        )

        quadro_pdf.pack(
            fill="x",
            pady=(0, 14),
        )

        campo_pdf = ttk.Entry(
            quadro_pdf,
            textvariable=self.caminho_pdf,
        )

        campo_pdf.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10),
        )

        botao_pdf = ttk.Button(
            quadro_pdf,
            text="Selecionar PDF",
            command=self.selecionar_pdf,
        )

        botao_pdf.pack(side="right")

        quadro_saida = ttk.LabelFrame(
            quadro_principal,
            text="Pasta de saída",
            padding=14,
        )

        quadro_saida.pack(
            fill="x",
            pady=(0, 18),
        )

        campo_saida = ttk.Entry(
            quadro_saida,
            textvariable=self.pasta_saida,
        )

        campo_saida.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10),
        )

        botao_saida = ttk.Button(
            quadro_saida,
            text="Selecionar pasta",
            command=self.selecionar_pasta_saida,
        )

        botao_saida.pack(side="right")

        self.botao_converter = ttk.Button(
            quadro_principal,
            text="Converter para Excel",
            command=self.iniciar_conversao,
            style="Acao.TButton",
        )

        self.botao_converter.pack(
            fill="x",
            pady=(0, 14),
        )

        self.barra_progresso = ttk.Progressbar(
            quadro_principal,
            mode="indeterminate",
        )

        self.barra_progresso.pack(
            fill="x",
            pady=(0, 14),
        )

        quadro_status = ttk.LabelFrame(
            quadro_principal,
            text="Status",
            padding=14,
        )

        quadro_status.pack(
            fill="both",
            expand=True,
            pady=(0, 14),
        )

        self.texto_status = tk.Text(
            quadro_status,
            height=7,
            wrap="word",
            font=("Consolas", 10),
            state="disabled",
        )

        self.texto_status.pack(
            fill="both",
            expand=True,
        )

        quadro_acoes = ttk.Frame(
            quadro_principal,
        )

        quadro_acoes.pack(fill="x")

        self.botao_abrir_excel = ttk.Button(
            quadro_acoes,
            text="Abrir arquivo Excel",
            command=self.abrir_excel,
            state="disabled",
        )

        self.botao_abrir_excel.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 6),
        )

        self.botao_abrir_pasta = ttk.Button(
            quadro_acoes,
            text="Abrir pasta de saída",
            command=self.abrir_pasta_saida,
        )

        self.botao_abrir_pasta.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(6, 0),
        )

        self.atualizar_status(
            "Selecione um arquivo PDF para iniciar."
        )

    def selecionar_pdf(self):
        arquivo_selecionado = filedialog.askopenfilename(
            title="Selecione o arquivo PDF",
            filetypes=[
                ("Arquivos PDF", "*.pdf"),
            ],
        )

        if arquivo_selecionado:
            self.caminho_pdf.set(
                arquivo_selecionado
            )

            self.atualizar_status(
                "PDF selecionado:\n"
                f"{arquivo_selecionado}"
            )

    def selecionar_pasta_saida(self):
        pasta_selecionada = filedialog.askdirectory(
            title="Selecione a pasta de saída"
        )

        if pasta_selecionada:
            self.pasta_saida.set(
                pasta_selecionada
            )

            self.atualizar_status(
                "Pasta de saída selecionada:\n"
                f"{pasta_selecionada}"
            )

    def validar_selecao(self):
        caminho_pdf = self.caminho_pdf.get().strip()
        pasta_saida = self.pasta_saida.get().strip()

        if not caminho_pdf:
            messagebox.showwarning(
                "Arquivo não selecionado",
                "Selecione um arquivo PDF.",
            )
            return False

        if not Path(caminho_pdf).is_file():
            messagebox.showerror(
                "Arquivo inválido",
                "O arquivo selecionado não existe.",
            )
            return False

        if Path(caminho_pdf).suffix.lower() != ".pdf":
            messagebox.showerror(
                "Formato inválido",
                "Selecione um arquivo PDF.",
            )
            return False

        if not pasta_saida:
            messagebox.showwarning(
                "Pasta não selecionada",
                "Selecione a pasta de saída.",
            )
            return False

        return True

    def iniciar_conversao(self):
        if not self.validar_selecao():
            return

        self.caminho_excel_criado = None

        self.botao_converter.configure(
            state="disabled"
        )

        self.botao_abrir_excel.configure(
            state="disabled"
        )

        self.barra_progresso.start(10)

        self.atualizar_status(
            "Iniciando o processamento..."
        )

        tarefa = threading.Thread(
            target=self.executar_conversao,
            daemon=True,
        )

        tarefa.start()

    def executar_conversao(self):
        caminho_pdf = self.caminho_pdf.get().strip()
        pasta_saida = self.pasta_saida.get().strip()

        try:
            (
                sucesso,
                caminho_excel,
                mensagem,
            ) = processar_pdf(
                caminho_pdf,
                pasta_saida,
                atualizar_status=(
                    self.agendar_atualizacao_status
                ),
            )

            self.janela.after(
                0,
                self.finalizar_conversao,
                sucesso,
                caminho_excel,
                mensagem,
            )

        except Exception as erro:
            mensagem = (
                "Ocorreu um erro inesperado.\n"
                f"Tipo: {type(erro).__name__}\n"
                f"Detalhe: {erro}"
            )

            self.janela.after(
                0,
                self.finalizar_conversao,
                False,
                None,
                mensagem,
            )

    def finalizar_conversao(
        self,
        sucesso,
        caminho_excel,
        mensagem,
    ):
        self.barra_progresso.stop()

        self.botao_converter.configure(
            state="normal"
        )

        self.atualizar_status(mensagem)

        if sucesso:
            self.caminho_excel_criado = Path(
                caminho_excel
            )

            self.botao_abrir_excel.configure(
                state="normal"
            )

            messagebox.showinfo(
                "Conversão concluída",
                mensagem,
            )

        else:
            messagebox.showerror(
                "Falha no processamento",
                mensagem,
            )

    def agendar_atualizacao_status(self, mensagem):
        self.janela.after(
            0,
            self.atualizar_status,
            mensagem,
        )

    def atualizar_status(self, mensagem):
        self.texto_status.configure(
            state="normal"
        )

        self.texto_status.delete(
            "1.0",
            tk.END,
        )

        self.texto_status.insert(
            tk.END,
            mensagem,
        )

        self.texto_status.configure(
            state="disabled"
        )

    def abrir_excel(self):
        if self.caminho_excel_criado is None:
            return

        if not self.caminho_excel_criado.exists():
            messagebox.showerror(
                "Arquivo não encontrado",
                "O arquivo Excel não existe mais.",
            )
            return

        os.startfile(
            str(self.caminho_excel_criado)
        )

    def abrir_pasta_saida(self):
        caminho_pasta = self.pasta_saida.get().strip()

        if not caminho_pasta:
            messagebox.showwarning(
                "Pasta não selecionada",
                "Selecione uma pasta de saída.",
            )
            return

        pasta_saida = Path(caminho_pasta)

        try:
            pasta_saida.mkdir(
                parents=True,
                exist_ok=True,
            )

            os.startfile(str(pasta_saida))

        except OSError as erro:
            messagebox.showerror(
                "Não foi possível abrir a pasta",
                f"Detalhe técnico: {erro}",
            )


def iniciar_aplicativo():
    janela = tk.Tk()

    InterfaceTransformador(janela)

    janela.mainloop()


if __name__ == "__main__":
    iniciar_aplicativo()