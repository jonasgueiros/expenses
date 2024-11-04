import flet as ft
from db_conn import conectar, fechar_conexao
from openpyxl import Workbook

def alterar_linha(page, selected_row_id, combobox_table, row_id_input):
    """Alter the selected row."""
    row_id = row_id_input.value
    if row_id:
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(f"SELECT * FROM {combobox_table.value} WHERE id = ?;", (row_id,))
                row = cursor.fetchone()
                if row:
                    show_alterar_dialog(page, row, combobox_table)
                else:
                    dialog = ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("ID não encontrado."), actions=[ft.TextButton("OK")])
                    page.overlay.append(dialog)
                    dialog.open = True
            except Exception as e:
                dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao buscar linha: {e}"), actions=[ft.TextButton("OK")])
                page.overlay.append(dialog)
                dialog.open = True
    else:
        dialog = ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("Por favor, insira o ID da linha para alterar."), actions=[ft.TextButton("OK")])
        page.overlay.append(dialog)
        dialog.open = True

def show_alterar_dialog(page, row, combobox_table):
    """Show a dialog with the row data for alteration."""
    selected_table = combobox_table.value
    conexao = conectar()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(f"PRAGMA table_info({selected_table});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            # Create text fields for each column
            text_fields = []
            for col_name, value in zip(column_names, row):
                if col_name.lower() in ['id', 'datahoje']:
                    text_fields.append(ft.TextField(label=col_name, value=str(value), read_only=True))
                else:
                    text_fields.append(ft.TextField(label=col_name, value=str(value)))

            def save_changes(e):
                new_values = [tf.value for tf in text_fields if tf.label.lower() not in ['id', 'datahoje']]
                update_query = f"UPDATE {selected_table} SET " + ", ".join([f"{col} = ?" for col in column_names if col.lower() not in ['id', 'datahoje']]) + " WHERE id = ?"
                try:
                    cursor.execute(update_query, new_values + [row[0]])
                    conexao.commit()
                    dialog = ft.AlertDialog(title=ft.Text("Sucesso"), content=ft.Text("Linha alterada com sucesso!"), actions=[ft.TextButton("OK")])
                    page.overlay.append(dialog)
                    dialog.open = True
                except Exception as e:
                    dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao alterar linha: {e}"), actions=[ft.TextButton("OK")])
                    page.overlay.append(dialog)
                    dialog.open = True

            alterar_dialog = ft.AlertDialog(
                title=ft.Text("Alterar Linha"),
                content=ft.Column(controls=text_fields),
                actions=[ft.TextButton("Salvar", on_click=save_changes), ft.TextButton("Cancelar")]
            )
            page.overlay.append(alterar_dialog)
            alterar_dialog.open = True
        except Exception as e:
            dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao carregar colunas: {e}"), actions=[ft.TextButton("OK")])
            page.overlay.append(dialog)
            dialog.open = True

def deletar_linha_nova_tabela(page, row_id_input, combobox_table):
    """Delete the selected row."""
    row_id = row_id_input.value
    if row_id:
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(f"DELETE FROM {combobox_table.value} WHERE id = ?;", (row_id,))
                conexao.commit()
                dialog = ft.AlertDialog(title=ft.Text("Sucesso"), content=ft.Text("Linha deletada com sucesso!"), actions=[ft.TextButton("OK")])
                page.overlay.append(dialog)
                dialog.open = True
            except Exception as e:
                dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao deletar linha: {e}"), actions=[ft.TextButton("OK")])
                page.overlay.append(dialog)
                dialog.open = True

    else:
        dialog = ft.AlertDialog(title=ft.Text("Aviso"), content=ft.Text("Por favor, insira o ID da linha para deletar."), actions=[ft.TextButton("OK")])
        page.overlay.append(dialog)
        dialog.open = True

def salvar_como_excel_nova_tabela(page, tree):
    """Save the Treeview data as an Excel file."""
    # Obter o nome da tabela
    table_name = "ExportedData"
    
    # Abrir um diálogo para salvar o arquivo
    def on_file_picked(e):
        file_path = e.files[0].path if e.files else None

        if file_path:
            # Criar um novo arquivo Excel
            wb = Workbook()
            ws = wb.active
            if ws is None:
                return

            # Obter os dados da Treeview
            data = []
            for row in tree.rows or []:
                data.append([cell.content.value for cell in row.cells])

            # Inserir os dados no arquivo Excel
            for row in data:
                ws.append(row)

            # Salvar o arquivo Excel
            wb.save(file_path)
            dialog = ft.AlertDialog(title=ft.Text("Sucesso"), content=ft.Text("Arquivo salvo com sucesso!"), actions=[ft.TextButton("OK")])
            page.overlay.append(dialog)
            dialog.open = True

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)
    file_picker.pick_files(allow_multiple=False)