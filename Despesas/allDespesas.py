import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from db_conn import conectar, fechar_conexao
from openpyxl import Workbook

class AllDespesas:
    def __init__(self, root):
        self.root = root
        self.root.title("All Despesas")

        self.root.geometry("870x320+370+0")
        self.root.minsize(950, 300)
        self.root.resizable(False, True)

        # Frame para seleção de tabela e colunas
        self.frame_selection = tk.Frame(root)
        self.frame_selection.pack(pady=10)

        # Combobox para selecionar a tabela
        self.label_table = tk.Label(self.frame_selection, text="Selecione a Tabela:")
        self.label_table.grid(row=0, column=0, padx=5)

        self.combobox_table = ttk.Combobox(self.frame_selection)
        self.combobox_table.grid(row=0, column=1, padx=5)
        self.combobox_table.bind("<<ComboboxSelected>>", self.load_columns)

        # Combobox para selecionar colunas
        self.label_column1 = tk.Label(self.frame_selection, text="Coluna X:")
        self.label_column1.grid(row=0, column=2, padx=5)

        self.combobox_column1 = ttk.Combobox(self.frame_selection)
        self.combobox_column1.grid(row=0, column=3, padx=5)

        self.label_column2 = tk.Label(self.frame_selection, text="Coluna Y:")
        self.label_column2.grid(row=0, column=4, padx=5)

        self.combobox_column2 = ttk.Combobox(self.frame_selection)
        self.combobox_column2.grid(row=0, column=5, padx=5)

        self.btn_calculate = tk.Button(self.frame_selection, text="Calcular Diferença", command=self.calculate_difference)
        self.btn_calculate.grid(row=0, column=6, padx=5)

        # Frame para Treeview
        self.frame_tree = tk.Frame(root)
        self.frame_tree.pack(expand=True, fill=tk.BOTH)

        self.tree = ttk.Treeview(self.frame_tree, show="headings")
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Permitir ordenação por coluna
        self.tree.bind("<Button-1>", self.sort_column)

        # Frame para botões
        self.frame_botoes = tk.Frame(root)
        self.frame_botoes.pack(pady=10)

        # Botão para deletar linha
        btn_deletar = tk.Button(self.frame_botoes, text="Deletar Linha", command=self.deletar_linha_nova_tabela)
        btn_deletar.pack(side=tk.LEFT, padx=5)

        # Botão para alterar linha
        btn_alterar = tk.Button(self.frame_botoes, text="Alterar Linha", command=self.alterar_linha_nova_tabela)
        btn_alterar.pack(side=tk.LEFT, padx=5)

        # Botão para salvar como Excel
        btn_salvar = tk.Button(self.frame_botoes, text="Salvar como Excel", command=self.salvar_como_excel_nova_tabela)
        btn_salvar.pack(side=tk.LEFT, padx=5)

        self.load_tables()

    def load_tables(self):
        """Load table names from the database, excluding sqlite_sequence."""
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables]
                self.combobox_table['values'] = table_names
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar tabelas: {e}")
            finally:
                cursor.close()
                fechar_conexao(conexao)

    def load_columns(self, event):
        """Load columns from the selected table, excluding 'id'."""
        selected_table = self.combobox_table.get()
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(f"PRAGMA table_info({selected_table});")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns if col[2] in ('INTEGER', 'REAL') and col[1] != 'id']  # Filter INTEGER or REAL and exclude 'id'
                self.combobox_column1['values'] = column_names
                self.combobox_column2['values'] = column_names
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar colunas: {e}")
            finally:
                cursor.close()
                fechar_conexao(conexao)

    def calculate_difference(self):
        """Calculate the difference between the two selected columns for each ID and display all columns."""
        selected_table = self.combobox_table.get()
        column_x = self.combobox_column1.get()
        column_y = self.combobox_column2.get()

        if not selected_table or not column_x or not column_y:
            messagebox.showwarning("Aviso", "Por favor, selecione a tabela e as colunas.")
            return

        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(f"SELECT * FROM {selected_table};")
                results = cursor.fetchall()

                # Clear the treeview
                self.tree.delete(*self.tree.get_children())
                self.tree["columns"] = [desc[0] for desc in cursor.description] + ["Diferença"]
                
                # Set headings for all columns including the difference
                for col in self.tree["columns"]:
                    self.tree.heading(col, text=col, anchor="w")

                # Insert rows into the treeview
                for row in results:
                    # Calculate the difference
                    difference = row[list(self.tree["columns"]).index(column_x)] - row[list(self.tree["columns"]).index(column_y)]
                    # Insert the row with the calculated difference
                    self.tree.insert("", "end", values=list(row) + [difference])
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao calcular diferença: {e}")
            finally:
                cursor.close()
                fechar_conexao(conexao)

    def sort_column(self, event):
        """Sort the Treeview by the clicked column."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            col = self.tree.identify_column(event.x)
            col_name = self.tree.column(col, "id")
            data = [(self.tree.set(child, col_name), child) for child in self.tree.get_children('')]
            data.sort(reverse=False)
            for i, item in enumerate(data):
                self.tree.move(item[1], '', i)

    def get_selected_row(self):
        """Get the ID of the selected row."""
        selected_item = self.tree.focus()
        if selected_item:
            return self.tree.item(selected_item, "values")[0]
        else:
            return None

    def deletar_linha_nova_tabela(self):
        """Delete the selected row."""
        selected_id = self.get_selected_row()
        if selected_id:
            conexao = conectar()
            if conexao:
                try:
                    cursor = conexao.cursor()
                    cursor.execute(f"DELETE FROM {self.combobox_table.get()} WHERE id = {selected_id};")
                    conexao.commit()
                    self.tree.delete(self.tree.focus())
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao deletar linha: {e}")
                finally:
                    cursor.close()
                    fechar_conexao(conexao)
        else:
            messagebox.showwarning("Aviso", "Selecione uma linha para deletar.")

    def alterar_linha_nova_tabela(self):
        selected_id = self.get_selected_row()
        if selected_id:
            conexao = conectar()
            if conexao:
                try:
                    cursor = conexao.cursor()
                    cursor.execute(f"SELECT * FROM {self.combobox_table.get()} WHERE id = {selected_id};")
                    row = cursor.fetchone()

                    # Criar uma interface para alterar os dados
                    alterar_window = tk.Toplevel(self.root)
                    alterar_window.title("Alterar Linha")

                    labels = []
                    entries = []
                    for i, col in enumerate(self.tree["columns"]):
                        if col not in ("ID", "id", "datahoje", "Diferença"):
                            label = tk.Label(alterar_window, text=col)
                            label.grid(row=i, column=0, padx=5, pady=5)  # Adicionando padding para melhor espaçamento
                            entry = tk.Entry(alterar_window)
                            entry.insert(0, row[i])
                            entry.grid(row=i, column=1, padx=5, pady=5)  # Adicionando padding para melhor espaçamento
                            labels.append(label)
                            entries.append(entry)

                    def update_row():
                        conexao = conectar()
                        if conexao:
                            try:
                                cursor = conexao.cursor()
                                for i, entry in enumerate(entries):
                                    cursor.execute(f"UPDATE {self.combobox_table.get()} SET {self.tree['columns'][i]} = ? WHERE id = {selected_id};", (entry.get(),))
                                conexao.commit()
                                alterar_window.destroy()
                                self.tree.delete(self.tree.focus())
                                self.calculate_difference()
                            except Exception as e:
                                messagebox.showerror("Erro", f"Erro ao alterar linha: {e}")
                            finally:
                                cursor.close()
                                fechar_conexao(conexao)

                    # Mover o botão "Atualizar" para a linha abaixo dos campos de entrada
                    btn_update = tk.Button(alterar_window, text="Atualizar", command=update_row)
                    btn_update.grid(row=len(labels), column=10, columnspan=2, padx=5, pady=10)  # Colocando o botão na linha abaixo

                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao alterar linha: {e}")
                finally:
                    cursor.close()
                    fechar_conexao(conexao)
        else:
            messagebox.showwarning("Aviso", "Selecione uma linha para alterar.")

    def salvar_como_excel_nova_tabela(self):
        """Save the Treeview data as an Excel file."""
        # Obter o nome da tabela
        table_name = self.combobox_table.get()
        
        # Abrir um diálogo para salvar o arquivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", 
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"{table_name}.xlsx",  # Nome padrão do arquivo
            title="Salvar como"
        )

        if file_path:  # Verifica se o usuário não cancelou o diálogo
            # Criar um novo arquivo Excel
            wb = Workbook()
            ws = wb.active

            # Obter os dados da Treeview
            data = []
            for child in self.tree.get_children(''):
                data.append([self.tree.item(child, "values")[i] for i in range(len(self.tree["columns"]))])

            # Inserir os dados no arquivo Excel
            for row in data:
                ws.append(row)

            # Salvar o arquivo Excel
            wb.save(file_path)
            messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AllDespesas(root)
    root.mainloop()