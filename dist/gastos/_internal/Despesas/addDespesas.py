import sys
import tkinter as tk
from tkinter import ttk, messagebox
from db_conn import conectar, fechar_conexao
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

        self.root.geometry("150x150+100+100")  # Set window size and position
        self.root.resizable(False, False)  # Disable resizing

        # Create a label and a combo box for table selection
        tk.Label(root, text="Selecione a Tabela:").pack(pady=10)

        # Fetch table names and create a combo box
        self.table_names = self.get_table_names()
        self.selected_table = tk.StringVar(value=self.table_names[0] if self.table_names else "")  # Default selection

        self.combobox_tabela = ttk.Combobox(root, textvariable=self.selected_table, values=self.table_names)
        self.combobox_tabela.pack(pady=10)

        # Create a button to confirm the selection and open the entry fields
        btn_confirmar = ttk.Button(root, text="Confirmar", command=self.carregar_colunas)
        btn_confirmar.pack(pady=10)

    def get_table_names(self):
        """Fetch the list of table names from the database, excluding sqlite_sequence."""
        conexao = conectar()
        tabelas = []
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tabelas = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']  # Exclude sqlite_sequence
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao obter tabelas: {e}")
            finally:
                cursor.close()
                fechar_conexao(conexao)
        return tabelas

    def carregar_colunas(self):
        selected_table = self.selected_table.get()
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(f"PRAGMA table_info({selected_table});")
                colunas = cursor.fetchall()

                # Create a new window for adding expenses
                self.janela_tabela = tk.Toplevel(self.root)
                self.janela_tabela.title("Adicionar Despesas")
                self.janela_tabela.geometry("300x300+0+340")  # Set size and position for the new window
                self.janela_tabela.resizable(False, False)

                # Clear previous widgets if any
                for widget in self.janela_tabela.winfo_children():
                    widget.destroy()

                self.entries = {}
                for i, coluna in enumerate(colunas):
                    col_name = coluna[1]  # Column name is the second element
                    if col_name not in ['id', 'datahoje']:  # Skip 'id' and 'datahoje'
                        lbl_coluna = ttk.Label(self.janela_tabela, text=col_name)
                        lbl_coluna.grid(row=i, column=0, padx=2, pady=2, sticky=tk.W)  # Reduced padding

                        entry_coluna = ttk.Entry(self.janela_tabela)
                        entry_coluna.grid(row=i, column=1, padx=2, pady=2)  # Reduced padding
                        self.entries[col_name] = entry_coluna

                # Add a button to add the expense
                btn_adicionar = ttk.Button(self.janela_tabela, text="Adicionar", command=lambda: self.adicionar_gasto(selected_table))
                btn_adicionar.grid(row=len(colunas), column=0, columnspan=2, pady=10)

                # Center the button
                for i in range(len(colunas) + 1):
                    self.janela_tabela.grid_rowconfigure(i, weight=1)
                self.janela_tabela.grid_columnconfigure(0, weight=1)
                self.janela_tabela.grid_columnconfigure(1, weight=1)

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar colunas: {e}")

            finally:
                cursor.close()
                fechar_conexao(conexao)

    def adicionar_gasto(self, selected_table):
        valores = {col: entry.get() for col, entry in self.entries.items()}

        # Add 'datahoje' with the current date
        datahoje = datetime.date.today().strftime("%d/%m/%y")
        valores['datahoje'] = datahoje

        # Connect to the database
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor()
                # Fetch column types for validation
                cursor.execute(f"PRAGMA table_info({selected_table});")
                colunas_info = cursor.fetchall()

                # Create a dictionary to map column names to their types
                column_types = {col[1]: col[2] for col in colunas_info}

                # Validate input data types
                for col_name, value in valores.items():
                    expected_type = column_types.get(col_name)
                    if expected_type == 'INTEGER':
                        if not value.isdigit():  # Check if the value is a valid integer
                            messagebox.showerror("Input Error", f"Valor inválido para a coluna '{col_name}': deve ser um número inteiro.")
                            return
                    elif expected_type == 'REAL':
                        try:
                            float(value)  # Check if the value can be converted to float
                        except ValueError:
                            messagebox.showerror("Input Error", f"Valor inválido para a coluna '{col_name}': deve ser um número real.")
                            return

                # Prepare the insert query
                query = f"INSERT INTO {selected_table} ({', '.join(valores.keys())}) VALUES ({', '.join(['?'] * len(valores))})"
                cursor.execute(query, list(valores.values()))

                conexao.commit()
                messagebox.showinfo("Sucesso", "Gasto adicionado com sucesso.")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar gasto: {e}")

            finally:
                cursor.close()
                fechar_conexao(conexao)

if __name__ == "__main__":
    main()