import flet as ft

class PreferenciasTab(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.theme_var = ft.Ref[ft.Dropdown]()
        self.language_var = ft.Ref[ft.Dropdown]()
        self.create_widgets()

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Preferencias", size=20),
                    ft.Row(
                        controls=[
                            ft.Text("Theme:"),
                            ft.Dropdown(
                                options=[
                                    ft.dropdown.Option("Light"),
                                    ft.dropdown.Option("Dark")
                                ],
                                ref=self.theme_var
                            )
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Language:"),
                            ft.Dropdown(
                                options=[
                                    ft.dropdown.Option("English"),
                                    ft.dropdown.Option("Portuguese")
                                ],
                                ref=self.language_var
                            )
                        ]
                    ),
                    ft.ElevatedButton("Save Preferences", on_click=self.save_preferences)
                ]
            )
        )

    def create_widgets(self):
        pass

    def save_preferences(self, e):
        theme = self.theme_var.current.value
        language = self.language_var.current.value
        # Here you can implement saving preferences to a file or database
        dialog = ft.AlertDialog(title=ft.Text("Preferences Saved"), content=ft.Text(f"Theme: {theme}\nLanguage: {language}"))
        if self.page:
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        # You can also apply the theme and language changes here
        