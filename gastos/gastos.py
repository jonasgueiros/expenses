import tkinter as tk
from tkinter import ttk, messagebox
from db_conn import conectar, fechar_conexao
import subprocess
import os
import sys
import psutil  # Import psutil to manage processes

# Dictionary to keep track of open windows
open_windows = {}

def open_window(script_name, *args):
    """Open a new window for the specified script."""
    # Allow multiple instances of statsDespesas.py
    if script_name == "statsDespesas":
        # Determine the base path
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        # Get the full path to the script in the "despesas" directory
        script_path = os.path.join(base_path, "despesas", f"{script_name}.py")
        # Call the script with separate arguments
        proc = subprocess.Popen(["python", script_path] + list(args), creationflags=subprocess.CREATE_NO_WINDOW)
        return  # Do not track this instance in open_windows

    # For other scripts, enforce single instance
    if script_name in open_windows and open_windows[script_name].poll() is None:
        # Window is already open, bring it to front
        messagebox.showinfo("Info", f"A janela {script_name} já está aberta.")
        return

    # Determine the base path
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    # Get the full path to the script in the "despesas" directory
    script_path = os.path.join(base_path, "despesas", f"{script_name}.py")
    # Call the script with separate arguments
    proc = subprocess.Popen(["python", script_path] + list(args), creationflags=subprocess.CREATE_NO_WINDOW)
    open_windows[script_name] = proc

def close_other_instances():
    """Close other instances of the application."""
    current_process = os.getpid()  # Get the current process ID
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'python.exe' and proc.info['pid'] != current_process:
            proc.terminate()  # Terminate other instances

class JanelaInicial:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciamento de Gastos")

        # Define window dimensions
        self.root.geometry("350x300+0+0")
        self.root.resizable(False, False)

        # Connect to the database
        conexao = conectar()
        if conexao:
            self.conexao = conexao
        else:
            messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")

        # Create a frame to center the buttons
        frame_botoes = ttk.Frame(self.root)
        frame_botoes.place(relx=0.5, rely=0.5, anchor="center")

        # Create buttons for different functionalities
        btn_adicionar = ttk.Button(frame_botoes, text="Adicionar Gasto", command=self.abrir_adicionar_gasto)
        btn_visualizar = ttk.Button(frame_botoes, text="Visualizar Gastos", command=self.abrir_visualizar_gastos)
        btn_visualizar_stats = ttk.Button(frame_botoes, text="Visualizar Estatísticas", command=self.abrir_visualizar_estatisticas)
        btn_config = ttk.Button(frame_botoes, text="Configurações", command=self.abrir_config)

        # Position buttons in the frame
        btn_adicionar.pack(pady=10)
        btn_visualizar.pack(pady=10)
        btn_visualizar_stats.pack(pady=10)
        btn_config.pack(pady=10)

        # Set the protocol for closing the main window
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handle the closing of the main window."""
        close_other_instances()  # Close other instances
        self.root.quit()  # Close the main window

    def abrir_adicionar_gasto(self):
        open_window("addDespesas")  # Single instance enforced

    def abrir_visualizar_gastos(self):
        open_window("allDespesas")  # Single instance enforced

    def abrir_visualizar_estatisticas(self):
        open_window("statsDespesas")  # Multiple instances allowed

    def abrir_config(self):
        open_window("config")  # Single instance enforced

if __name__ == "__main__":
    root = tk.Tk()
    app = JanelaInicial(root)
    root.mainloop()