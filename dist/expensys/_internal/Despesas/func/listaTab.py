import flet as ft
import sqlite3
from db_conn import conectar, fechar_conexao

class ListaTab(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.table_list = ft.Column()
        self.table_name_combobox = ft.Dropdown()
        self.create_widgets()
        self.update_table_list()

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Lista de Tabelas", size=20),
                    self.table_name_combobox,
                    self.table_list,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton("Deletar", on_click=self.delete_table),
                            ft.ElevatedButton("Modificar", on_click=self.modify_table)
                        ]
                    )
                ]
            )
        )

    def create_widgets(self):
        pass

    def update_table_list(self):
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('sqlite_sequence', 'expenses');")
                tables = cursor.fetchall()
                self.table_list.controls.clear()  # Clear existing entries
                self.table_name_combobox.options = [ft.dropdown.Option(table[0]) for table in tables]
                if self.page:
                    self.page.update()
            except Exception as e:
                dialog = ft.AlertDialog(title=ft.Text("Error"), content=ft.Text(f"Error updating table list: {e}"))
                if self.page:
                    self.page.overlay.append(dialog)
                dialog.open = True
            finally:
                fechar_conexao(conexao)

    def delete_table(self, e):
        table_name = self.table_name_combobox.value
        if not table_name:
            dialog = ft.AlertDialog(title=ft.Text("Error"), content=ft.Text("Please select a table to delete."))
            if self.page:
                self.page.overlay.append(dialog)
            dialog.open = True
            return

        conexao = conectar()
        if conexao:
            try:
                sql_delete_table = f"DROP TABLE IF EXISTS {table_name};"
                conexao.execute(sql_delete_table)
                dialog = ft.AlertDialog(title=ft.Text("Success"), content=ft.Text(f"Table '{table_name}' deleted successfully."))
                if self.page:
                    self.page.overlay.append(dialog)
                dialog.open = True
                self.update_table_list()
            except Exception as e:
                dialog = ft.AlertDialog(title=ft.Text("Error"), content=ft.Text(f"Error deleting table: {e}"))
                if self.page:
                    self.page.overlay.append(dialog)
                dialog.open = True
            finally:
                fechar_conexao(conexao)

    def modify_table(self, e):
        table_name = self.table_name_combobox.value
        if not table_name:
            dialog = ft.AlertDialog(title=ft.Text("Error"), content=ft.Text("Please select a table to modify."))
            if self.page:
                self.page.overlay.append(dialog)
            dialog.open = True
            return

        self.modificar_tabela_interface(table_name)

    def modificar_tabela_interface(self, table_name):
        def on_save_changes(e):
            new_table_name = new_table_name_entry.value
            column_updates = []
            for entry in column_entries:
                col_name = entry[0].value
                col_type = entry[1].value
                if col_name and col_type:
                    column_updates.append(f"{col_name} {col_type}")
            if new_table_name:
                self.executar_com_verificacao(self.modificar_tabela, table_name, new_table_name, column_updates)
                modificar_dialog.open = False  # Close the modification window
                if self.page:
                    self.page.update()
            else:
                dialog = ft.AlertDialog(title=ft.Text("Input Error"), content=ft.Text("Por favor, preencha todos os campos."))
                if self.page:
                    self.page.overlay.append(dialog)
                dialog.open = True

        column_entries = []
        conexao = conectar()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for column in columns:
                if column[1] not in ['datahoje', 'id']:  # Skip 'datahoje' and 'id' columns
                    col_name_entry = ft.TextField(value=column[1])
                    col_type_entry = ft.TextField(value=column[2])
                    column_entries.append((col_name_entry, col_type_entry))
            fechar_conexao(conexao)

        new_table_name_entry = ft.TextField(value=table_name)

        modificar_dialog = ft.AlertDialog(
            title=ft.Text("Modificar Tabela"),
            content=ft.Column(
                controls=[
                    ft.Text("Novo nome da tabela:"),
                    new_table_name_entry,
                    ft.Text("Colunas:"),
                    *[ft.Row(controls=[col_name_entry, col_type_entry]) for col_name_entry, col_type_entry in column_entries],
                    ft.ElevatedButton("Salvar alterações", on_click=on_save_changes)
                ]
            ),
            actions=[ft.TextButton("Fechar", on_click=lambda e: setattr(modificar_dialog, 'open', False))]
        )

        if self.page:
            self.page.overlay.append(modificar_dialog)
            modificar_dialog.open = True
            self.page.update()

    def modificar_tabela(self, conexao, old_table_name, new_table_name, column_updates):
        """Modifica a tabela no banco de dados."""
        try:
            # Step 1: Create a new table with the new structure
            columns_definition = ", ".join(column_updates)
            conexao.execute(f"CREATE TABLE {new_table_name} ({columns_definition});")

            # Step 2: Copy data from the old table to the new table
            columns_names = ", ".join([update.split()[0] for update in column_updates])
            conexao.execute(f"INSERT INTO {new_table_name} ({columns_names}) SELECT {columns_names} FROM {old_table_name};")

            # Step 3: Drop the old table
            conexao.execute(f"DROP TABLE {old_table_name};")

            # Step 4: Rename the new table to the old table's name
            conexao.execute(f"ALTER TABLE {new_table_name} RENAME TO {old_table_name};")

            conexao.commit()  # Commit the changes
            dialog = ft.AlertDialog(title=ft.Text("Success"), content=ft.Text(f"Tabela '{old_table_name}' modificada com sucesso."))
            if self.page:
                self.page.overlay.append(dialog)
            dialog.open = True
        except sqlite3.Error as e:
            dialog = ft.AlertDialog(title=ft.Text("Error"), content=ft.Text(f"Erro ao modificar a tabela: {e}"))
            if self.page:
                self.page.overlay.append(dialog)
            dialog.open = True

    def executar_com_verificacao(self, func, *args):
        conexao = conectar()
        if conexao:
            try:
                func(conexao, *args)
            finally:
                fechar_conexao(conexao)
