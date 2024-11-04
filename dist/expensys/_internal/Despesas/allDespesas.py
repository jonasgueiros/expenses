import flet as ft
from flet import AlertDialog
import sys
import os
import subprocess
from db_conn import conectar, fechar_conexao
from openpyxl import Workbook
from Despesas.func.def_allDespesas import alterar_linha, deletar_linha_nova_tabela, salvar_como_excel_nova_tabela
from Despesas.func.addDespesas import JanelaAdicionarGasto  # Import the addDespesas script

class AllDespesas(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.selected_row_id = None  # Store the selected row ID
        self.sort_order = {}  # Store the sort order for each column
        self.conexao = conectar()  # Open the database connection

        # Initialize components
        self.combobox_table = ft.Dropdown(label="Selecione a Tabela", on_change=self.load_columns)
        self.combobox_column1 = ft.Dropdown(label="Coluna X")
        self.combobox_column2 = ft.Dropdown(label="Coluna Y")
        self.row_id_input = ft.TextField(label="ID da Linha", width=200)  # Text entry for row ID
        self.checkbox_diff = ft.Checkbox(label="Calcular Diferença entre Colunas", value=False, on_change=self.toggle_diff)
        self.tree = ft.DataTable(
            columns=[ft.DataColumn(label=ft.Text("Placeholder"), visible=True)],
            rows=[]
        )

        self.page = page
        self.layout = ft.Column(controls=[
            self.create_selection_frame(),
            self.tree,
            self.create_button_frame()
        ])
        self.load_tables()

    def __del__(self):
        """Ensure the database connection is closed when the object is destroyed."""
        if self.conexao:
            fechar_conexao(self.conexao)

    def create_selection_frame(self):
        """Create a frame for selecting table and columns."""
        self.btn_calculate = ft.ElevatedButton("Buscar", on_click=self.load_table_data)
        return ft.Column(controls=[
            ft.Row(controls=[
                self.combobox_table,
                self.combobox_column1,
                self.combobox_column2,
                self.btn_calculate
            ]),
            self.checkbox_diff
        ])

    def create_button_frame(self):
        """Create a frame for action buttons."""
        btn_inserir = ft.ElevatedButton("Inserir", on_click=self.open_add_despesas_dialog)
        btn_deletar = ft.ElevatedButton("Deletar", on_click=lambda e: deletar_linha_nova_tabela(self.page, self.row_id_input, self.combobox_table))
        btn_alterar = ft.ElevatedButton("Alterar", on_click=lambda e: alterar_linha(self.page, self.selected_row_id, self.combobox_table, self.row_id_input))
        btn_salvar = ft.ElevatedButton("Exportar", on_click=lambda e: salvar_como_excel_nova_tabela(self.page, self.tree))
        return ft.Row(controls=[btn_inserir, self.row_id_input, btn_deletar, btn_alterar, btn_salvar])

    def toggle_diff(self, e):
        """Toggle the visibility of the column selection comboboxes based on the checkbox state."""
        self.combobox_column1.visible = self.checkbox_diff.value
        self.combobox_column2.visible = self.checkbox_diff.value
        if self.page:
            self.page.update()

    def open_add_despesas_dialog(self, e):
        """Open the addDespesas dialog."""
        selected_table = self.combobox_table.value
        entries = self.create_entries(selected_table)
        janela_adicionar_gasto = JanelaAdicionarGasto(self.page, selected_table)
        janela_adicionar_gasto.create_widgets()

        add_despesas_dialog = ft.AlertDialog(
            title=ft.Text("Adicionar Despesas"),
            content=ft.Column(
                controls=[
                    janela_adicionar_gasto,
                    ft.ElevatedButton("Adicionar", on_click=janela_adicionar_gasto.adicionar_gasto)
                ]
            ),
            actions=[ft.TextButton("Fechar", on_click=lambda e: setattr(add_despesas_dialog, 'open', False))]
        )

        if self.page:
            self.page.overlay.append(add_despesas_dialog)
            add_despesas_dialog.open = True
            self.page.update()

    def create_entries(self, selected_table):
        """Create entries for the addDespesas window."""
        entries = {}
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(f"PRAGMA table_info({selected_table});")
                colunas = cursor.fetchall()

                for coluna in colunas:
                    col_name = coluna[1]  # Column name is the second element
                    if col_name not in ['id', 'datahoje']:  # Skip 'id' and 'datahoje'
                        entry_coluna = ft.TextField(label=col_name)
                        entries[col_name] = entry_coluna

            except Exception as e:
                dialog = AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao carregar colunas: {e}"))
                if self.page:
                    self.page.overlay.append(dialog)
                    dialog.open = True
            finally:
                cursor.close()
                fechar_conexao(conexao)
        return entries

    def load_tables(self):
        """Load table names from the database, excluding sqlite_sequence."""
        if self.conexao:
            try:
                cursor = self.conexao.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables]
                self.combobox_table.options = [ft.dropdown.Option(name) for name in table_names]
                if self.page:
                    self.page.update()
            except Exception as e:
                dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao carregar tabelas: {e}"), actions=[ft.TextButton("OK")])
                if self.page:
                    self.page.overlay.append(dialog)  # Use overlay to show the dialog
                dialog.open = True

    def load_columns(self, event):
        """Load columns from the selected table."""
        selected_table = self.combobox_table.value
        if self.conexao:
            try:
                cursor = self.conexao.cursor()
                cursor.execute(f"PRAGMA table_info({selected_table});")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns if col[2] in ('INTEGER', 'REAL') and col[1] != 'id']
                self.combobox_column1.options = [ft.dropdown.Option(name) for name in column_names]
                self.combobox_column2.options = [ft.dropdown.Option(name) for name in column_names]
                if self.page:
                    self.page.update()
            except Exception as e:
                dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao carregar colunas: {e}"), actions=[ft.TextButton("OK")])
                if self.page:
                    self.page.overlay.append(dialog)
                dialog.open = True

    def load_table_data(self, e=None):
        selected_table = self.combobox_table.value
        column_x = self.combobox_column1.value
        column_y = self.combobox_column2.value

        if not selected_table:
            dialog = ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("Por favor, selecione a tabela."), actions=[ft.TextButton("OK")])
            if self.page:
                self.page.overlay.append(dialog)
            dialog.open = True
            return

        if self.checkbox_diff.value and (not column_x or not column_y):
            dialog = ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("Por favor, selecione as colunas para calcular a diferença."), actions=[ft.TextButton("OK")])
            if self.page:
                self.page.overlay.append(dialog)
            dialog.open = True
            return

        if self.conexao:
            try:
                cursor = self.conexao.cursor()
                cursor.execute(f"SELECT * FROM {selected_table};")
                results = cursor.fetchall()
                print("Fetched results:", results)  # Debugging line

                if not results:
                    dialog = ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("Nenhum dado encontrado na tabela."), actions=[ft.TextButton("OK")])
                    if self.page:
                        self.page.overlay.append(dialog)
                    dialog.open = True
                    return

                self.tree.columns = [ft.DataColumn(label=ft.Text(desc[0]), visible=True) for desc in cursor.description]
                if self.checkbox_diff.value:
                    self.tree.columns.append(ft.DataColumn(label=ft.Text("Diferença"), visible=True))
                print("Columns set:", [(col.label, col.visible) for col in self.tree.columns])  # Debugging line

                self.tree.rows = []
                for row in results:
                    row_cells = [ft.DataCell(ft.Text(str(cell))) for cell in row]
                    if self.checkbox_diff.value:
                        col_x_index = [desc[0] for desc in cursor.description].index(column_x)
                        col_y_index = [desc[0] for desc in cursor.description].index(column_y)
                        diff_value = float(row[col_x_index]) - float(row[col_y_index])
                        row_cells.append(ft.DataCell(ft.Text(str(diff_value))))
                    self.tree.rows.append(ft.DataRow(cells=row_cells))

                if self.page:
                    self.page.update()  # Ensure the page is updated
            except Exception as e:
                dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao carregar dados da tabela: {e}"), actions=[ft.TextButton("OK")])
                if self.page:
                    self.page.overlay.append(dialog)
                dialog.open = True

    def get_control(self):
        """Return the main layout control."""
        return self.layout