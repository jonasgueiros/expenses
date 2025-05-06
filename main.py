import flet as ft
from flet import AlertDialog
import subprocess
import win32gui
import win32con
import win32api
import os
import sys
import psutil
from db_conn import conectar, fechar_conexao, verificar_tabela_existe  # Import the necessary functions
from Despesas.allDespesas import AllDespesas  # Import the AllDespesas class
from Despesas.statsDespesas import JanelaStats  # Import the JanelaStats class

open_windows = {}

def open_window(page, script_name, *args):
    """Open a new window for the specified script."""
    try:
        # Allow multiple instances of statsDespesas.py
        if script_name == "statsDespesas":
            # Determine the base path
            if getattr(sys, 'frozen', False):
                base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
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
            dialog = AlertDialog(title=ft.Text("Info"), content=ft.Text(f"A janela {script_name} já está aberta."))
            page.overlay.append(dialog)  # Use overlay to show the dialog
            dialog.open = True
            return

        # Determine the base path
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        else:
            base_path = os.path.abspath(".")

        # Get the full path to the script in the "despesas" directory
        script_path = os.path.join(base_path, "despesas", f"{script_name}.py")
        
        # Check if the script exists
        if not os.path.exists(script_path):
            dialog = AlertDialog(title=ft.Text("Error"), content=ft.Text(f"O script '{script_name}.py' não foi encontrado."))
            page.overlay.append(dialog)
            dialog.open = True
            print(f"Script not found: {script_path}")  # Print if the script is not found
            return
        
        # Call the script with separate arguments
        proc = subprocess.Popen(["python", script_path] + list(args), creationflags=subprocess.CREATE_NO_WINDOW)
        open_windows[script_name] = proc

    except Exception as e:
        dialog = AlertDialog(title=ft.Text("Error"), content=ft.Text(f"Erro ao abrir a janela: {str(e)}"))
        page.overlay.append(dialog)
        dialog.open = True
        print(f"Exception occurred: {str(e)}")  # Print the exception message

def close_window(page, script_name):
    """Close the specified window."""
    if script_name in open_windows:
        window = open_windows.pop(script_name, None)
        if window:
            window.terminate()
            dialog = AlertDialog(title=ft.Text("Info"), content=ft.Text(f"A janela {script_name} foi fechada."))
            page.overlay.append(dialog)
            dialog.open = True

def close_all_windows():
    """Close all open windows."""
    for script_name in list(open_windows.keys()):
        window = open_windows.pop(script_name, None)
        if window:
            window.terminate()

def close_other_instances():
    """Close other instances of the application."""
    current_process = os.getpid()  # Get the current process ID
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'python.exe' and proc.info['pid'] != current_process:
            proc.terminate()  # Terminate other instances

class JanelaInicial:
    def __init__(self, page):
        self.page = page
        self.page.title = "Gerenciamento de Dados"
        
        self.page.window_width = 1270  # Set initial window width
        self.page.window_height = 900  # Set initial window height
        self.page.window_min_width = 1270  # Set minimum window width
        self.page.window_min_height = 900  # Set minimum window height

        # Connect to the database
        self.conexao = conectar()
        if not self.conexao:
            dialog = AlertDialog(title=ft.Text("Erro"), content=ft.Text("Erro ao conectar ao banco de dados."))
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.window.close()  # Close the application if connection fails
        
        # Check and create the expenses table
        verificar_tabela_existe(self.conexao)

        # Create a sidebar for navigation
        sidebar = ft.Column(
            controls=[
                ft.ElevatedButton("Home", on_click=self.show_home),
                ft.ElevatedButton("Tabelas", on_click=self.abrir_visualizar_gastos),
                ft.ElevatedButton("Estatísticas", on_click=self.abrir_visualizar_estatisticas),
                ft.Container(height=550),  # Add some space before the links
                ft.TextButton("GitHub", on_click=lambda e: self.page.launch_url("https://github.com/jonasgueiros")),
                ft.ElevatedButton("Configurações", on_click=self.abrir_config),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # Set sidebar background color and rounded corners
        sidebar_container = ft.Container(
            content=sidebar,
            bgcolor=ft.colors.BLACK,
            padding=10,
            width=170,  # Adjust the width to be slightly larger than the buttons
            border_radius=10,  # Set rounded corners
            expand=False  # Make the sidebar container resizable in height
        )

        # Create a main content area with rounded corners
        self.content_area = ft.Container(
            content=ft.Column(),
            bgcolor=ft.colors.BLUE_GREY_900,
            padding=20,
            border_radius=10,  # Set rounded corners
            expand=True  # Make the content area resizable
        )

        # Add sidebar and content area to the page
        self.page.add(ft.Row(controls=[sidebar_container, self.content_area], expand=True))

        # Set the protocol for closing the main window
        self.page.on_close = self.on_close
        
        self.show_home(None)  # Show the home page

    def on_close(self):
        """Handle the closing of the main window."""
        close_all_windows()  # Close all open windows
        close_other_instances()  # Close other instances
        if self.conexao:
            fechar_conexao(self.conexao)  # Close the database connection
        self.page.window.close()  # Properly close the main window

    def show_home(self, _):
        #AI = AIChat(self.page)
        #self.content_area.content = AI
        self.page.update()

    def abrir_visualizar_gastos(self, _):
        all_despesas = AllDespesas(self.page)
        self.content_area.content = all_despesas.get_control()
        self.page.update()

    def abrir_visualizar_estatisticas(self, _):
        janela_stats = JanelaStats(self.page)
        self.content_area.content = janela_stats
        self.page.update()

    def abrir_config(self, _):
        open_window(self.page, "config_interface")  # Execute the script

    def abrir_add_despesas(self, _):
        open_window(self.page, "addDespesas")  # Open the addDespesas window

    def fechar_add_despesas(self, _):
        close_window(self.page, "addDespesas")  # Close the addDespesas window

ft.app(target=JanelaInicial)