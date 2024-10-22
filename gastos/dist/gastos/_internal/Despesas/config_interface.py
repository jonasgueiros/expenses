# config_interface.py

import tkinter as tk
from tkinter import filedialog
import config

def aplicar_tema(root, theme):
    if theme == "dark":
        root.configure(bg="black")
        for widget in root.winfo_children():
            widget.configure(bg="black", fg="white")
        print("Aplicando tema escuro")
    else:
        root.configure(bg="white")
        for widget in root.winfo_children():
            widget.configure(bg="white", fg="black")
        print("Aplicando tema claro")

def salvar_configuracoes(theme, labels, caminho_excel):
    config.THEME = theme
    config.LABELS = labels
    config.EXCEL_SAVE_PATH = caminho_excel
    with open('config.py', 'w') as f:
        f.write(f'# config.py\n\n')
        f.write(f'# Configurações de tema\n')
        f.write(f'THEME = "{theme}"  # Opções: "light", "dark"\n\n')
        f.write(f'# Renomear labels no addDespesas\n')
        f.write(f'LABELS = {labels}\n\n')
        f.write(f'# Configurações do Excel\n')
        f.write(f'EXCEL_SAVE_PATH = "{caminho_excel}"\n')
    print("Configurações salvas com sucesso!")

def criar_interface():
    root = tk.Tk()
    root.title("Configurações do Programa")

    # Frame para seleção de tema
    frame_tema = tk.Frame(root)
    frame_tema.pack(pady=10)

    tk.Label(frame_tema, text="Selecione o Tema:").pack(side=tk.LEFT)

    tema_var = tk.StringVar(value=config.THEME)
    tk.Radiobutton(frame_tema, text="Claro", variable=tema_var, value="light", command=lambda: aplicar_tema(root, tema_var.get())).pack(side=tk.LEFT)
    tk.Radiobutton(frame_tema, text="Escuro", variable=tema_var, value="dark", command=lambda: aplicar_tema(root, tema_var.get())).pack(side=tk.LEFT)

    # Frame para renomear labels
    frame_labels = tk.Frame(root)
    frame_labels.pack(pady=10)

    labels = {}
    for label_key, label_value in config.LABELS.items():
        tk.Label(frame_labels, text=f"{label_key}:").pack(side=tk.LEFT)
        entry = tk.Entry(frame_labels)
        entry.insert(0, label_value)
        entry.pack(side=tk.LEFT)
        labels[label_key] = entry

    # Botão para selecionar o caminho do Excel
    frame_excel = tk.Frame(root)
    frame_excel.pack(pady=10)

    tk.Label(frame_excel, text="Caminho para salvar o Excel:").pack(side=tk.LEFT)
    caminho_excel_var = tk.StringVar(value=config.EXCEL_SAVE_PATH)
    tk.Entry(frame_excel, textvariable=caminho_excel_var).pack(side=tk.LEFT)
    tk.Button(frame_excel, text="Selecionar", command=lambda: caminho_excel_var.set(filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]))).pack(side=tk.LEFT)

    # Botão para salvar as configurações
    tk.Button(root, text="Salvar Configurações", command=lambda: salvar_configuracoes(tema_var.get(), {k: v.get() for k, v in labels.items()}, caminho_excel_var.get())).pack(pady=10)

    aplicar_tema(root, tema_var.get())

    root.mainloop()

if __name__ == "__main__":
    criar_interface()
