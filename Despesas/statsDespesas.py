from subprocess import call
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from db_conn import conectar, fechar_conexao

def main():
    # Check if an instance is already running
    if len(sys.argv) > 1 and sys.argv[1] == 'running':
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showinfo("Info", "A janela já está aberta.")
        sys.exit()

    root = tk.Tk()
    app = JanelaStats(root)
    root.mainloop()
    
class JanelaStats:
    def __init__(self, root):
        self.root = root
        self.root.title("Gastos por Categoria")
        
        self.root.geometry("630x300+370+350")
        self.root.minsize(630, 300)
        self.root.resizable(False, True)

        self.categorias = []
        self.valores = []
        self.valores_paid = []
        self.diferencas = []
        self.total_gastos = 0
        self.total_paid = 0
        self.total_diferenca = 0

        self.create_widgets()
        self.atualizar_dados()  # Initialize data

    def create_widgets(self):
        # Create a frame for controls at the top
        frame_controles = ttk.Frame(self.root)
        frame_controles.pack(side=tk.TOP, anchor='nw', padx=10, pady=10)

        # Add a Combobox to select the company
        self.combobox_empresas = ttk.Combobox(frame_controles)
        self.combobox_empresas.pack(side=tk.LEFT, padx=5)

        # Fill the Combobox with companies from the database
        self.populate_combobox()

        # Add checkboxes to filter data
        self.var_amount = tk.BooleanVar(value=True)
        self.var_paid = tk.BooleanVar()

        # Button to update data
        botao_atualizar = ttk.Button(frame_controles, text="Atualizar Dados", command=self.atualizar_dados)
        botao_atualizar.pack(side=tk.LEFT, padx=5)

        # Button to display summary
        botao_resumo = ttk.Button(frame_controles, text="Exibir Resumo", command=self.exibir_resumo)
        botao_resumo.pack(side=tk.LEFT, padx=5)

        # Create a frame for the graph
        frame_grafico = ttk.Frame(self.root)
        frame_grafico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create the pie chart
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def populate_combobox(self):
        conexao = conectar()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT DISTINCT description FROM expenses")
            empresas = [row[0] for row in cursor.fetchall()]
            empresas.append("Todas Empresas")
            self.combobox_empresas['values'] = empresas
            fechar_conexao(conexao)

    def atualizar_dados(self):
        # Function to update data and redraw the graph
        empresa_selecionada = self.combobox_empresas.get()
        filtrar_amount = self.var_amount.get()
        filtrar_paid = self.var_paid.get()

        if filtrar_amount and filtrar_paid:
            messagebox.showerror("Erro", "Não é permitido selecionar ambos Amount e Paid.")
            return

        conexao = conectar()
        if not conexao:
            messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
            return

        cursor = conexao.cursor()
        if empresa_selecionada == "Todas Empresas":
            if filtrar_amount:
                cursor.execute("SELECT description, SUM(amount), SUM(paid) FROM expenses GROUP BY description")
            elif filtrar_paid:
                cursor.execute("SELECT description, SUM(amount), SUM(paid) FROM expenses GROUP BY description")
        else:
            if filtrar_amount:
                cursor.execute("SELECT category, SUM(amount), SUM(paid) FROM expenses WHERE description = ? GROUP BY category", (empresa_selecionada,))
            elif filtrar_paid:
                cursor.execute("SELECT category, SUM(amount), SUM(paid) FROM expenses WHERE description = ? GROUP BY category", (empresa_selecionada,))
        resultado = cursor.fetchall()

        if not resultado:
            messagebox.showerror("Erro", "Nenhum dado encontrado.")
            fechar_conexao(conexao)
            return

        self.categorias = [item[0] for item in resultado]
        self.valores = [item[1] for item in resultado]
        self.valores_paid = [item[2] for item in resultado]
        self.diferencas = [item[1] - item[2] for item in resultado]
        self.total_gastos = sum(self.valores)
        self.total_paid = sum(self.valores_paid)
        self.total_diferenca = sum(self.diferencas)

        # Update the graph
        self.ax.clear()
        if empresa_selecionada == "Todas Empresas":
            self.ax.pie(self.diferencas, labels=self.categorias, autopct='%1.1f%%', startangle=140)
            self.ax.set_title("Todas Empresas")
        else:
            self.ax.pie(self.diferencas, labels=self.categorias, autopct='%1.1f%%', startangle=140)
            self.ax.set_title(f"- {empresa_selecionada}")
        self.ax.axis('equal')
        self.canvas.draw()

    def exibir_resumo(self):
        # Function to display the summary in a new window
        resumo_janela = tk.Toplevel(self.root)
        resumo_janela.title("Resumo dos Gastos")
        resumo_janela.geometry("300x650+1020+0")  # Fixed window on the right side
        resumo_janela.resizable(False, False)
        lista_resumo = tk.Text(resumo_janela, wrap=tk.WORD, height=15)
        lista_resumo.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        if self.combobox_empresas.get() == "Todas Empresas":
            lista_resumo.insert(tk.END, "Gastos por Empresa:\n")
            for categoria, valor, valor_paid, diferenca in zip(self.categorias, self.valores, self.valores_paid, self.diferencas):
                lista_resumo.insert(tk.END, f"{categoria}:\n Quantia: R$ {valor:.2f}\n Quantia Paga: R$ {valor_paid:.2f}\n Diferença: R$ {diferenca:.2f}\n")
        else:
            lista_resumo.insert(tk.END, f"Gastos por Categoria - {self.combobox_empresas.get()}:\n")
            for categoria, valor, valor_paid, diferenca in zip(self.categorias, self.valores, self.valores_paid, self.diferencas):
                lista_resumo.insert(tk.END, f"{categoria}:\n Quantia: R$ {valor:.2f}\n Quantia Paga: R$ {valor_paid:.2f}\n Diferença: R$ {diferenca:.2f}\n")
        lista_resumo.insert(tk.END, f"\nValor Total dos Gastos: R$ {self.total_gastos:.2f}")
        lista_resumo.insert(tk.END, f"\nValor Total dos Pagamentos: R$ {self.total_paid:.2f}")
        lista_resumo.insert(tk.END, f"\nDiferença Total: R$ {self.total_diferenca:.2f}")

if __name__ == "__main__":
    main()