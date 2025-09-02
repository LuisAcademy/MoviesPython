import sqlite3
import os
import pandas as pd
from sqlite3 import Connection

def create_database_connection(db_file: str) -> Connection | None:
    """Cria uma conexão com o banco de dados SQLite."""
    conn = None
    try:
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        conn = sqlite3.connect(db_file)
        print(f"Banco de dados '{os.path.basename(db_file)}' conectado com sucesso.")
        return conn
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao conectar ao banco de dados: {e}")
        return None

def execute_sql_from_file(conn: Connection, filepath: str):
    """Lê um arquivo .sql e executa seu conteúdo."""
    print(f"Executando script: {os.path.basename(filepath)}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        print("Script executado com sucesso.")
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao executar o script {os.path.basename(filepath)}: {e}")

def create_tables(conn: Connection, sql_folder: str):
    """Cria as tabelas SOR e SOT executando os scripts SQL correspondentes."""
    print("\n--- Iniciando a criação das tabelas SOR e SOT ---")
    scripts = ["sor_tmdb_movies.sql", "sor_tmdb_credits.sql", "sot_movies.sql", "sot_credits.sql"]
    for script_name in scripts:
        script_path = os.path.join(sql_folder, script_name)
        execute_sql_from_file(conn, script_path)

def transform_data(conn: Connection, sql_folder: str):
    """Executa os scripts de transformação para popular as tabelas SOT."""
    print("\n--- Iniciando a transformação de dados (SOR -> SOT) ---")
    scripts = ["spec_sot_movies.sql", "spec_sot_credits.sql"]
    for script_name in scripts:
        script_path = os.path.join(sql_folder, script_name)
        execute_sql_from_file(conn, script_path)

def load_sot_data_for_training(conn: Connection) -> pd.DataFrame:
    """Carrega os dados da tabela SOT, prontos para o treinamento."""
    print("Carregando dados da SOT para treinamento...")
    query = """
        SELECT budget, revenue, popularity, runtime, vote_average
        FROM sot_movies
        WHERE budget > 1000 AND revenue > 1000 AND runtime > 0 AND vote_average > 0
    """
    df = pd.read_sql_query(query, conn)
    print(f"Carregados {len(df)} registros para treinamento.")
    return df

# --- FUNÇÃO QUE FALTAVA ---
def drop_database(conn: Connection, db_file: str):
    """Fecha a conexão e apaga o arquivo do banco de dados."""
    print(f"\n--- Finalizando o tratamento e dropando o database ---")
    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")
    
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Arquivo do banco de dados '{os.path.basename(db_file)}' removido com sucesso.")