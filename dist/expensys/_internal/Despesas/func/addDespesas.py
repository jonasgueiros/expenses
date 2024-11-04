import flet as ft
from flet import AlertDialog
from db_conn import conectar, fechar_conexao
import datetime

class JanelaAdicionarGasto(ft.UserControl):
    def __init__(self, page, selected_table):
        super().__init__()
        self.page = page
        self.selected_table = selected_table
        self.entries = {}
        self.create_widgets()

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Tabela: {self.selected_table}", size=20),
                    self.entries_container,
                ]
            ),
            bgcolor=ft.colors.BLUE_GREY_900,  # Set background color to match the Flet window
            padding=20,
            width=400,
            height=600
        )

    def create_widgets(self):
        self.entries_container = ft.Column()
        self.load_columns()

    def load_columns(self):
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(f"PRAGMA table_info({self.selected_table});")
                colunas = cursor.fetchall()

                for coluna in colunas:
                    col_name = coluna[1]  # Column name is the second element
                    if col_name not in ['id', 'datahoje']:  # Skip 'id' and 'datahoje'
                        entry_coluna = ft.TextField(label=col_name)
                        self.entries[col_name] = entry_coluna
                        self.entries_container.controls.append(entry_coluna)

                if self.page:
                    self.page.update()
            except Exception as e:
                dialog = AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao carregar colunas: {e}"))
                if self.page:
                    self.page.overlay.append(dialog)
                    dialog.open = True
            finally:
                cursor.close()
                fechar_conexao(conexao)

    def adicionar_gasto(self, e):
        valores = {col: entry.value for col, entry in self.entries.items()}

        # Add 'datahoje' with the current date
        datahoje = datetime.date.today().strftime("%d/%m/%y")
        valores['datahoje'] = datahoje

        # Connect to the database
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                # Fetch column types for validation
                cursor.execute(f"PRAGMA table_info({self.selected_table});")
                colunas_info = cursor.fetchall()

                # Create a dictionary to map column names to their types
                column_types = {col[1]: col[2] for col in colunas_info}

                # Validate input data types
                for col_name, value in valores.items():
                    expected_type = column_types.get(col_name)
                    if expected_type == 'INTEGER':
                        if not value.isdigit():  # Check if the value is a valid integer
                            dialog = AlertDialog(title=ft.Text("Input Error"), content=ft.Text(f"Valor inválido para a coluna '{col_name}': deve ser um número inteiro."))
                            if self.page:
                                self.page.overlay.append(dialog)
                                dialog.open = True
                            return
                    elif expected_type == 'REAL':
                        try:
                            float(value)  # Check if the value can be converted to float
                        except ValueError:
                            dialog = AlertDialog(title=ft.Text("Input Error"), content=ft.Text(f"Valor inválido para a coluna '{col_name}': deve ser um número real."))
                            if self.page:
                                self.page.overlay.append(dialog)
                                dialog.open = True
                            return

                # Prepare the insert query
                query = f"INSERT INTO {self.selected_table} ({', '.join(valores.keys())}) VALUES ({', '.join(['?'] * len(valores))})"
                cursor.execute(query, list(valores.values()))

                conexao.commit()
                dialog = AlertDialog(title=ft.Text("Sucesso"), content=ft.Text("Gasto adicionado com sucesso."))
                if self.page:
                    self.page.overlay.append(dialog)
                    dialog.open = True

            except Exception as e:
                dialog = AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao adicionar gasto: {e}"))
                if self.page:
                    self.page.overlay.append(dialog)
                    dialog.open = True

            finally:
                cursor.close()
                fechar_conexao(conexao)

    def close_window(self, e):
        """Close the addDespesas window."""
        if self.page and self in self.page.overlay:
            self.page.overlay.remove(self)
            self.page.update()