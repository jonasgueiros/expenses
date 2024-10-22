from subprocess import call
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from db_conn import conectar, fechar_conexao

def open_window(script_name):
    call(["python", f"{script_name}.py"])

def atualizar_dados():
    # Função para atualizar os dados e redesenhar o gráfico
    empresa_selecionada = combobox_empresas.get()
    filtrar_amount = var_amount.get()
    filtrar_paid = var_paid.get()

    if filtrar_amount and filtrar_paid:
        print("Não é permitido selecionar ambos Amount e Paid.")
        return

    conexao = conectar()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
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
        print("Nenhum dado encontrado.")
        fechar_conexao(conexao)
        return

    global categorias, valores, valores_paid, diferencas, total_gastos, total_paid, total_diferenca
    categorias = [item[0] for item in resultado]
    valores = [item[1] for item in resultado]
    valores_paid = [item[2] for item in resultado]
    diferencas = [item[1] - item[2] for item in resultado]
    total_gastos = sum(valores)
    total_paid = sum(valores_paid)
    total_diferenca = sum(diferencas)

    # Atualizar o gráfico
    ax.clear()
    if empresa_selecionada == "Todas Empresas":
        ax.pie(diferencas, labels=categorias, autopct='%1.1f%%', startangle=140)
        ax.set_title("Todas Empresas")
    else:
        ax.pie(diferencas, labels=categorias, autopct='%1.1f%%', startangle=140)
        ax.set_title(f"- {empresa_selecionada}")
    ax.axis('equal')
    canvas.draw()

def exibir_resumo():
    # Função para exibir a lista de resumo em uma nova janela
    resumo_janela = tk.Toplevel(root)
    resumo_janela.title("Resumo dos Gastos")
    resumo_janela.geometry("300x650+1020+0")  # Janela fixa no canto direito
    resumo_janela.resizable(False,False)
    lista_resumo = tk.Text(resumo_janela, wrap=tk.WORD, height=15)
    lista_resumo.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    if combobox_empresas.get() == "Todas Empresas":
        lista_resumo.insert(tk.END, "Gastos por Empresa:\n")
        for categoria, valor, valor_paid, diferenca in zip(categorias, valores, valores_paid, diferencas):
            lista_resumo.insert(tk.END, f"{categoria}:\n Quantia: R$ {valor:.2f}\n Quantia Paga: R$ {valor_paid:.2f}\n Diferença: R$ {diferenca:.2f}\n")
    else:
        lista_resumo.insert(tk.END, f"Gastos por Categoria - {combobox_empresas.get()}:\n")
        for categoria, valor, valor_paid, diferenca in zip(categorias, valores, valores_paid, diferencas):
            lista_resumo.insert(tk.END, f"{categoria}:\n Quantia: R$ {valor:.2f}\n Quantia Paga: R$ {valor_paid:.2f}\n Diferença: R$ {diferenca:.2f}\n")
    lista_resumo.insert(tk.END, f"\nValor Total dos Gastos: R$ {total_gastos:.2f}")
    lista_resumo.insert(tk.END, f"\nValor Total dos Pagamentos: R$ {total_paid:.2f}")
    lista_resumo.insert(tk.END, f"\nDiferença Total: R$ {total_diferenca:.2f}")

def exibir_grafico_despesas():
    # Criar a janela principal
    global root
    root = tk.Tk()
    root.title("Gastos por Categoria")
    root.geometry("630x300+370+350")
    root.minsize(630, 300)
    root.resizable(False, True)

    # Criar um frame para os controles no topo
    frame_controles = ttk.Frame(root)
    frame_controles.pack(side=tk.TOP, anchor='nw', padx=10, pady=10)

    # Adicionar um Combobox para selecionar a empresa
    global combobox_empresas
    combobox_empresas = ttk.Combobox(frame_controles)
    combobox_empresas.pack(side=tk.LEFT, padx=5)

    # Preencher o Combobox com as empresas do banco de dados
    conexao = conectar()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT DISTINCT description FROM expenses")
        empresas = [row[0] for row in cursor.fetchall()]
        empresas.append("Todas Empresas")
        combobox_empresas['values'] = empresas
        fechar_conexao(conexao)

    # Adicionar checkboxes para filtrar os dados
    global var_amount, var_paid
    var_amount = tk.BooleanVar()
    var_paid = tk.BooleanVar()
    var_amount = tk.BooleanVar(value=True)

    # Botão para atualizar os dados
    botao_atualizar = ttk.Button(frame_controles, text="Atualizar Dados", command=atualizar_dados)
    botao_atualizar.pack(side=tk.LEFT, padx=5)

    # Botão para exibir o resumo
    botao_resumo = ttk.Button(frame_controles, text="Exibir Resumo", command=exibir_resumo)
    botao_resumo.pack(side=tk.LEFT, padx=5)

    # Criar um frame para o gráfico
    frame_grafico = ttk.Frame(root)
    frame_grafico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Criar o gráfico de pizza
    global fig, ax, canvas
    fig, ax = plt.subplots(figsize=(6, 6))
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Atualizar os dados inicialmente para mostrar todas as empresas
    atualizar_dados()

    root.mainloop()

if __name__ == "__main__":
    exibir_grafico_despesas()
