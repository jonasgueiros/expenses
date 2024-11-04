import flet as ft
from flet import AlertDialog
from func.listaTab import ListaTab
from func.novaTab import NovaTab
from func.preference import PreferenciasTab
from db_conn import conectar

# Define the current version of the software
CURRENT_VERSION = "0.8"

class ConfigInterface(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.page.title = "Configurações"
        
        self.page.window_width = 730
        self.page.window_height = 730 
        self.page.window_min_width = 730
        self.page.window_min_height = 730
        
        # Connect to the database
        self.conexao = conectar()
        if not self.conexao:
            dialog = AlertDialog(title=ft.Text("Erro"), content=ft.Text("Erro ao conectar ao banco de dados."))
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.window.close()  # Close the application if connection fails
        
        # Create a sidebar for navigation
        sidebar = ft.Column(
            controls=[
                ft.ElevatedButton("Lista de Tabelas", on_click=self.abrir_tabelas),
                ft.ElevatedButton("Criar Tabela", on_click=self.abrir_nova),
                ft.ElevatedButton("Preferencias", on_click=self.abrir_preferencias),
                ft.Container(height=300),  # Add some space before the links
                ft.TextButton(f"V {CURRENT_VERSION}", on_click=lambda e: self.page.launch_url("https://github.com/jonasgueiros/expenses")),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # Set sidebar background color
        sidebar_container = ft.Container(
            content=sidebar,
            bgcolor=ft.colors.BLUE_GREY_900,
            padding=10,
            width=170,
            border_radius=20
        )

        # Create a main content area
        self.content_area = ft.Container(
            content=ft.Column(),
            bgcolor=ft.colors.BLUE_GREY_900,
            padding=20,
            border_radius=20,
            expand=True
        )

        # Add sidebar and content area to the page
        self.page.add(ft.Row(controls=[sidebar_container, self.content_area], expand=True))
        self.abrir_tabelas(None)
        
    def abrir_tabelas(self, _):
        self.content_area.content = ListaTab(self.page)
        if self.page:
            self.page.update()

    def abrir_nova(self, _):
        self.content_area.content = NovaTab(self.page)
        if self.page:
            self.page.update()

    def abrir_preferencias(self, _):
        janela_preferencia = PreferenciasTab(self.page)
        self.content_area.content = janela_preferencia
        if self.page:
            self.page.update()

def main(page):
    # Center the window on the screen
    screen_width = page.window_width
    screen_height = page.window_height
    window_width = 800  # Set the desired width of the config_interface window
    window_height = 600  # Set the desired height of the config_interface window
    page.window_left = (screen_width - window_width) // 2
    page.window_top = (screen_height - window_height) // 2
    page.window_width = window_width
    page.window_height = window_height

    config_interface = ConfigInterface(page)
    page.add(config_interface)

ft.app(target=main)