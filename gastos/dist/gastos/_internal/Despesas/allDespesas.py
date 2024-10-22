import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from db_conn import conectar, fechar_conexao
import openpyxl

class JanelaVisualizarGastos:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizar Gastos")

        self.root.geometry("870x300+370+0")
        self.root.minsize(950, 300)  # Define o tamanho mínimo
        self.root.resizable(False, True)

        # Conectar ao banco de dados
        conexao = conectar()

        if conexao:
            try:
                cursor = conexao.cursor()
                # Executar a consulta para obter os gastos
                cursor.execute("SELECT * FROM expenses")

                # Obter os resultados da consulta
                resultados = cursor.fetchall()

                # Criar uma treeview para exibir os dados
                self.tree = ttk.Treeview(root, show="headings")
                self.tree["columns"] = ("ID", "Descrição", "Valor", "Pago", "Data", "Prazo", "Categoria", "Diferença")
                self.tree["displaycolumns"] = self.tree["columns"]

                # Definir as colunas
                self.tree.column("#0", width=0, stretch=tk.NO)  # Espaço em branco
                self.tree.column("ID", anchor=tk.W, width=50)
                self.tree.column("Descrição", anchor=tk.W, width=150)
                self.tree.column("Valor", anchor=tk.W, width=100)
                self.tree.column("Pago", anchor=tk.W, width=100)
                self.tree.column("Data", anchor=tk.W, width=100)
                self.tree.column("Prazo", anchor=tk.W, width=100)
                self.tree.column("Categoria", anchor=tk.W, width=150)
                self.tree.column("Diferença", anchor=tk.W, width=100)

                # Configurar os cabeçalhos das colunas
                for col in self.tree["columns"]:
                    self.tree.heading(col, text=col, anchor=tk.W, command=lambda c=col: self.sort_by(c, False))

                # Adicionar os dados à treeview
                for row in resultados:
                    id, descricao, valor, pago, data, prazo, categoria = row
                    diferenca = valor - pago
                    self.tree.insert("", "end", values=(id, descricao, valor, pago, data, prazo, categoria, diferenca))

                # Definir a ordem inicial das colunas
                self.tree["displaycolumns"] = ("ID", "Descrição", "Categoria", "Valor", "Pago", "Diferença", "Data", "Prazo")

                # Posicionar a treeview na janela
                self.tree.pack(expand=True, fill=tk.BOTH)

                # Adicionar evento de clique e arraste para reordenar colunas
                self.tree.bind("<ButtonPress-1>", self.iniciar_arraste)
                self.tree.bind("<B1-Motion>", self.arrastar_coluna)

                self.coluna_origem = None
                self.coluna_destino = None

                frame_botoes = tk.Frame(root)
                frame_botoes.pack(pady=10)
                
                # Adicionar botão para deletar linha
                btn_deletar = tk.Button(frame_botoes, text="Deletar Linha", command=self.deletar_linha)
                btn_deletar.pack(side=tk.LEFT, padx=5)

                # Adicionar botão para alterar linha
                btn_alterar = tk.Button(frame_botoes, text="Alterar Linha", command=self.alterar_linha)
                btn_alterar.pack(side=tk.LEFT, padx=5)

                # Adicionar botão para salvar como Excel
                btn_salvar = tk.Button(frame_botoes, text="Salvar como Excel", command=self.salvar_como_excel)
                btn_salvar.pack(side=tk.LEFT, padx=5)

            except Exception as e:
                print(f"Erro ao visualizar gastos: {e}")

            finally:
                cursor.close()
                fechar_conexao(conexao)

    def iniciar_arraste(self, event):
        coluna_id = self.tree.identify_column(event.x)
        if coluna_id:
            self.coluna_origem = int(coluna_id.replace("#", "")) - 1

    def arrastar_coluna(self, event):
        coluna_id = self.tree.identify_column(event.x)
        if coluna_id:
            coluna_destino = int(coluna_id.replace("#", "")) - 1
            
            if self.coluna_origem is not None and self.coluna_origem != coluna_destino:
                colunas = list(self.tree["columns"])
                colunas.insert(coluna_destino, colunas.pop(self.coluna_origem))
                self.tree["displaycolumns"] = colunas
                self.coluna_origem = coluna_destino

    def sort_by(self, col, descending):
        data_list = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        data_list.sort(reverse=descending)
        for index, (val, child) in enumerate(data_list):
            self.tree.move(child, "", index)
        self.tree.heading(col, command=lambda: self.sort_by(col, not descending))

    def deletar_linha(self):
        try:
            selected_item = self.tree.selection()[0]  # Select the item
            id_selecionado = self.tree.item(selected_item, "values")[0]  # Get the ID of the selected item
            
            # Delete from the database
            conexao = conectar()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM expenses WHERE id = ?", (id_selecionado,))
                conexao.commit()  # Commit the changes
                cursor.close()
                fechar_conexao(conexao)

            self.tree.delete(selected_item)  # Delete the item from the Treeview
            print("Linha deletada com sucesso!")
        except IndexError:
            print("Nenhuma linha selecionada para deletar.")
        except Exception as e:
            print(f"Erro ao deletar linha: {e}")

    def alterar_linha(self):
        item_selecionado = self.tree.selection()
        if item_selecionado:
            # Get the values of the selected item
            id_selecionado = self.tree.item(item_selecionado, "values")[0]
            descricao = self.tree.item(item_selecionado, "values")[1]
            valor = self.tree.item(item_selecionado, "values")[2]
            pago = self.tree.item(item_selecionado, "values")[3]
            data = self.tree.item(item_selecionado, "values")[4]
            prazo = self.tree.item(item_selecionado, "values")[5]            
            categoria = self.tree.item(item_selecionado, "values")[6]

            # Open a new window for editing
            self.janela_edicao = tk.Toplevel(self.root)
            self.janela_edicao.title(f"Editar Gasto ID: {id_selecionado}")

            self.janela_edicao.geometry("350x300+370+0")
            self.janela_edicao.minsize(350, 250)  # Set minimum size
            self.janela_edicao.resizable(False, True)

            # Create widgets for editing
            lbl_descricao = ttk.Label(self.janela_edicao, text="Empresa:")
            entry_descricao = ttk.Entry(self.janela_edicao)
            entry_descricao.insert(0, descricao)

            lbl_valor = ttk.Label(self.janela_edicao, text="Valor:")
            entry_valor = ttk.Entry(self.janela_edicao)
            entry_valor.insert(0, valor)

            lbl_pago = ttk.Label(self.janela_edicao, text="Pago:")
            entry_pago = ttk.Entry(self.janela_edicao)
            entry_pago.insert(0, pago)

            lbl_data = ttk.Label(self.janela_edicao, text="Data (AAAA-MM-DD):")
            entry_data = ttk.Entry(self.janela_edicao)
            entry_data.insert(0, data)

            lbl_prazo = ttk.Label(self.janela_edicao, text="Prazo (AAAA-MM-DD):")
            entry_prazo = ttk.Entry(self.janela_edicao)
            entry_prazo.insert(0, prazo)

            lbl_categoria = ttk.Label(self.janela_edicao, text="Material:")
            entry_categoria = ttk.Entry(self.janela_edicao)
            entry_categoria.insert(0, categoria)

            btn_confirmar = ttk.Button(self.janela_edicao, text="Confirmar Edição", command=lambda: self.confirmar_edicao(
                id_selecionado, 
                entry_descricao.get(), 
                entry_valor.get(), 
                entry_pago.get(), 
                entry_data.get(), 
                entry_prazo.get(),  # Ensure this is included
                entry_categoria.get()
                ))

            # Position the widgets in the editing window
            lbl_descricao.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
            entry_descricao.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

            lbl_valor.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
            entry_valor.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

            lbl_pago.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
            entry_pago.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

            lbl_data.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
            entry_data.grid(row= 3, column=1, padx=10, pady=10, sticky=tk.W)

            lbl_prazo.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
            entry_prazo.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

            lbl_categoria.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
            entry_categoria.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)

            btn_confirmar.grid(row=6, column=0, columnspan=2, pady=10)
        else:
            messagebox.showwarning("Aviso", "Selecione um item para editar.")
            
    def confirmar_edicao(self, id_selecionado, nova_descricao, novo_valor, novo_pago, nova_data, novo_prazo, nova_categoria):
        # Log the changes for debugging
        print(f"Editar ID {id_selecionado}:")
        print(f"Nova Empresa: {nova_descricao}")
        print(f"Novo Valor (total): {novo_valor}")
        print(f"Novo Valor (pago): {novo_pago}")
        print(f"Nova Data: {nova_data}")
        print(f"Novo Prazo: {novo_prazo}")
        print(f"Nova Material: {nova_categoria}")

        # Update the Treeview
        item_selecionado = self.tree.selection()
        if item_selecionado:
            self.tree.item(item_selecionado, values=(id_selecionado, nova_descricao, novo_valor, novo_pago, nova_data, novo_prazo, nova_categoria))
            
            conexao = conectar()
            if conexao:
                try:
                    # Create a cursor
                    cursor = conexao.cursor()

                    # Prepare the SQL update query
                    query = "UPDATE expenses SET description = ?, amount = ?, paid = ?, date = ?, prazo = ?, category = ? WHERE id = ?"
                    valores = (nova_descricao, novo_valor, novo_pago, nova_data, novo_prazo, nova_categoria, id_selecionado)

                    # Execute the query
                    cursor.execute(query, valores)

                    # Commit to save the changes
                    conexao.commit()

                    messagebox.showinfo("Sucesso", "Gasto alterado com sucesso.")

                except Exception as e:
                    print(f"Erro ao alterar gasto: {e}")
                    messagebox.showerror("Erro", f"Erro ao alterar gasto:\n{e}")

                finally:
                    # Close the cursor and the connection
                    cursor.close()
                    fechar_conexao(conexao)
        else:
            messagebox.showwarning("Aviso", "Selecione um item para editar.")
            
    def salvar_como_excel(self):
        # Criar um novo workbook e uma nova planilha
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Gastos"

        # Adicionar cabeçalhos
        headers = ["ID", "Empresa", "Valor", "Pago", "Data", "Prazo", "Categoria", "Diferença"]
        sheet.append(headers)

        # Dicionário para armazenar a soma dos valores por empresa
        soma_por_empresa = {}
        total_gastos = 0

        # Adicionar dados da treeview
        for row_id in self.tree.get_children():
            row = self.tree.item(row_id)['values']
            sheet.append(row)
            
            empresa = row[1]
            valor = float(row[2])
            
            if empresa in soma_por_empresa:
                soma_por_empresa[empresa] += valor
            else:
                soma_por_empresa[empresa] = valor
            
            total_gastos += valor

        # Adicionar a soma dos valores por empresa ao final da planilha
        sheet.append([])
        sheet.append(["Empresa", "Soma dos Valores"])
        for empresa, soma in soma_por_empresa.items():
            sheet.append([empresa, soma])

        # Adicionar o valor total dos gastos
        sheet.append([])
        sheet.append(["Total dos Gastos", total_gastos])

        # Salvar o arquivo
        try:
            workbook.save("gastos.xlsx")
            messagebox.showinfo("Sucesso", "Tabela salva como gastos.xlsx")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JanelaVisualizarGastos(root)
    root.mainloop()
