import sqlite3

def conectar():
    try:
        conexao = sqlite3.connect('expenses_db.db', timeout=10)
        conexao.execute('PRAGMA journal_mode=WAL;')
        print("Conexão ao banco de dados estabelecida.")
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def fechar_conexao(conexao):
    if conexao:
        conexao.close()
        print("Conexão ao banco de dados fechada.")

def criar_tabela(conexao):
    try:
        sql_create_table = """CREATE TABLE IF NOT EXISTS expenses (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                description TEXT DEFAULT NULL,
                                amount INTEGER DEFAULT NULL,
                                paid INTEGER DEFAULT NULL,
                                datahoje TEXT DEFAULT NULL,
                                prazo TEXT DEFAULT NULL,  -- Fixed typo here
                                category TEXT DEFAULT NULL
                            );"""
        conexao.execute(sql_create_table)
        print("Tabela 'expenses' criada ou já existe.")
    except sqlite3.Error as e:
        print(f"Erro ao criar a tabela: {e}")

def verificar_tabela_existe(conexao):
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses';")
        table_exists = cursor.fetchone()
        if not table_exists:
            criar_tabela(conexao)
    except sqlite3.Error as e:
        print(f"Erro ao verificar a tabela: {e}")

def executar_com_verificacao(funcao, *args):
    conexao = conectar()
    if conexao:
        verificar_tabela_existe(conexao)
        funcao(conexao, *args)
        fechar_conexao(conexao)

def teste(conexao):
    try:
        # Adicione aqui as operações que irão testar as tabelas
        print("Tabela já criada.")
    except sqlite3.Error as e:
        print(f"Erro ao realizar a operação: {e}")

# Testando a conexão e criação da tabela com verificação
if __name__ == "__main__":
    executar_com_verificacao(teste)