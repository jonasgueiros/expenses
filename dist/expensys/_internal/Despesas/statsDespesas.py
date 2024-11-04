import flet as ft
import matplotlib.pyplot as plt
import matplotlib
from db_conn import conectar, fechar_conexao

# Use the Agg backend for Matplotlib to avoid GUI issues
matplotlib.use('Agg')

class JanelaStats(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.categorias = []
        self.valores = []
        self.total_gastos = 0
        
        self.combobox_empresas_ref = ft.Ref[ft.Dropdown]()
        self.create_widgets()
        self.populate_combobox()
        self.atualizar_dados()  # Initialize data

    def build(self):
        return ft.Column(
            controls=[
                self.frame_controles,
                self.frame_grafico_resumo  # Use a Row to hold the graph and summary side by side
            ]
        )

    def create_widgets(self):
        # Create a frame for controls at the top
        self.frame_controles = ft.Row(
            controls=[
                ft.Dropdown(
                    hint_text="Selecione uma empresa",
                    on_change=self.atualizar_dados,
                    ref=self.combobox_empresas_ref
                ),
                ft.ElevatedButton("Atualizar Dados", on_click=self.atualizar_dados)
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        # Create a frame for the graph
        self.frame_grafico = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Gráfico de Gastos", size=20),
                    ft.Image(src="", key="grafico")  # Placeholder for the graph image
                ]
            ),
            padding=10
        )

        # Create a frame for the summary
        self.text_resumo = ft.TextField(label="Resumo dos Gastos", height=400, read_only=True, multiline=True, key="resumo")
        self.frame_resumo = ft.Container(content=self.text_resumo, padding=10)

        # Combine the graph and summary into a Row
        self.frame_grafico_resumo = ft.Row(
            controls=[
                self.frame_grafico,
                self.frame_resumo
            ],
            alignment=ft.MainAxisAlignment.START
        )

    def populate_combobox(self):
        conexao = conectar()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT DISTINCT description FROM expenses")
            empresas = [row[0] for row in cursor.fetchall()]
            empresas.append("Todas Empresas")
            # Update dropdown options using the reference
            self.combobox_empresas_ref.current.options = [ft.dropdown.Option(text=empresa) for empresa in empresas]
            self.combobox_empresas_ref.current.value = "Todas Empresas"  # Set default selection
            fechar_conexao(conexao)

    def atualizar_dados(self, e=None):
        empresa_selecionada = self.combobox_empresas_ref.current.value
        conexao = conectar()
        if not conexao:
            dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text("Erro ao conectar ao banco de dados."), modal=True)
            if self.page:
                self.page.overlay.append(dialog)  # Append the dialog to the page's overlay
                dialog.open = True
                self.page.update()  # Update the page to show the dialog
            return

        cursor = conexao.cursor()
        if empresa_selecionada == "Todas Empresas":
            cursor.execute("SELECT description, SUM(amount) FROM expenses GROUP BY description")
        else:
            cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE description = ? GROUP BY category", (empresa_selecionada,))
        
        resultado = cursor.fetchall()

        if not resultado:
            dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text("Nenhum dado encontrado."), modal=True)
            if self.page:    
                self.page.overlay.append(dialog)  # Append the dialog to the page's overlay
                dialog.open = True
                self.page.update()  # Update the page to show the dialog
            fechar_conexao(conexao)
            return

        # Update categories and values based on the query results
        self.categorias = [item[0] for item in resultado]
        self.valores = [item[1] for item in resultado]
        self.total_gastos = sum(self.valores)

        # Update the graph and summary
        self.update_graph(empresa_selecionada)
        self.update_summary(empresa_selecionada)

        fechar_conexao(conexao)

    def update_graph(self, empresa_selecionada):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(self.valores, labels=self.categorias, autopct='%1.1f%%', startangle=140)
        ax.set_title(f"Gastos - {empresa_selecionada}" if empresa_selecionada != "Todas Empresas" else "Gastos - Todas Empresas")
        ax.axis('equal')

        # Save the graph to a file
        plt.savefig("temp_graph.png")
        plt.close(fig)  # Close the figure to avoid display issues

        # Update the graph image
        if self.frame_grafico.content and len(self.frame_grafico.content.controls) > 1:
            self.frame_grafico.content.controls[1].src = "temp_graph.png"
            if self.page:
                self.page.update()  # Ensure the page is updated to reflect the changes

    def update_summary(self, empresa_selecionada):
        resumo = ""
        if empresa_selecionada == "Todas Empresas":
            resumo += "Gastos por Empresa:\n"
            for categoria, valor in zip(self.categorias, self.valores):
                resumo += f"{categoria}:\n Quantia: R$ {valor:.2f}\n"
        else:
            resumo += f"Gastos por Categoria - {empresa_selecionada}:\n"
            for categoria, valor in zip(self.categorias, self.valores):
                resumo += f"{categoria}:\n Quantia: R$ {valor:.2f}\n"
        resumo += f"\nValor Total dos Gastos: R$ {self.total_gastos:.2f}"

        self.text_resumo.value = resumo
        if self.page:
            self.page.update()  # Update the page to show the summary