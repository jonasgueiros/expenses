import sys
import tkinter as tk
from tkinter import ttk, messagebox
from db_conn import conectar, fechar_conexao, verificar_tabela_existe
import datetime

def main():
    # Check if an instance is already running
    if len(sys.argv) > 1 and sys.argv[1] == 'running':
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showinfo("Info", "A janela de adicionar gasto já está aberta.")
        sys.exit()

    root = tk.Tk()
    app = JanelaAdicionarGasto(root)
    root.mainloop()

class JanelaAdicionarGasto:
    def __init__(self, root):
        self.root = root
        self.root.title("Adicionar Gasto")

        self.root.geometry("350x300+0+350")
        self.root.minsize(350, 250)  # Set minimum size
        self.root.resizable(False, True)

        # Criar variáveis para armazenar os dados do gasto
        self.descricao_var = tk.StringVar()
        self.valor_var = tk.DoubleVar()
        self.pago_var = tk.DoubleVar()
        self.data_var = tk.StringVar()
        self.prazo_var = tk.StringVar()
        self.categoria_var = tk.StringVar()

        # Criar rótulos e entradas para descrição, valor, data e categoria
        lbl_descricao = ttk.Label(root, text="Empresa/Evento:")
        entry_descricao = ttk.Entry(root, textvariable=self.descricao_var)

        lbl_valor = ttk.Label(root, text="Valor:")
        entry_valor = ttk.Entry(root, textvariable=self.valor_var)

        lbl_pago = ttk.Label(root, text="Pago:")
        entry_pago = ttk.Entry(root, textvariable=self.pago_var)

        lbl_prazo = ttk.Label(root, text="Prazo (AAAA-MM-DD):")
        entry_prazo = ttk.Entry(root, textvariable=self.prazo_var)

        lbl_categoria = ttk.Label(root, text="Recursos/Materias:")
        entry_categoria = ttk.Entry(root, textvariable=self.categoria_var)

        btn_adicionar = ttk.Button(root, text="Adicionar", command=self.adicionar_gasto)

        # Posicionar os widgets na janela
        lbl_descricao.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        entry_descricao.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        lbl_valor.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        entry_valor.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        lbl_pago.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        entry_pago.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        lbl_prazo.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        entry_prazo.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

        lbl_categoria.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        entry_categoria.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)

        btn_adicionar.grid(row=6, column=0, columnspan=2, pady=10)

    def adicionar_gasto(self):
        # Obter os valores dos widgets
        descricao = self.descricao_var.get()
        valor = self.valor_var.get()
        pago = self.pago_var.get()
        prazo = self.prazo_var.get()
        categoria = self.categoria_var.get()

        # Conectar ao banco de dados
        conexao = conectar()

        if conexao:
            verificar_tabela_existe(conexao)  # Verifique se a tabela existe
            
            try:
                # Criar um cursor
                cursor = conexao.cursor()
                
                # Get the current date and time
                now = datetime.datetime.now()
                # Format the date as you like
                data = now.strftime("%Y/%m/%d")
                
                # Inserir os dados na tabela de gastos
                query = "INSERT INTO expenses (description, amount, paid, date, prazo, category) VALUES (?, ?, ?, ?, ?, ?)"
                valores = (descricao, valor, pago, data, prazo, categoria)
                cursor.execute(query, valores)

                # Commit para salvar as alterações
                conexao.commit()

                messagebox.showinfo("Sucesso", "Gasto adicionado com sucesso.")

            except Exception as e:
                print(f"Erro ao adicionar gasto: {e}")
                messagebox.showerror("Erro", f"Erro ao adicionar gasto:\n{e}")

            finally:
                # Fechar o cursor e a conexão
                cursor.close()
                fechar_conexao(conexao)

if __name__ == "__main__":
    root = tk.Tk()
    app = JanelaAdicionarGasto(root)
    root.mainloop()
