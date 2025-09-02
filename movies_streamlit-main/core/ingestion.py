import pandas as pd
from sqlite3 import Connection
import os

def ingest_csv_to_sor(conn: Connection, csv_path: str, table_name: str):
    """
    Lê dados de um arquivo CSV e os insere em uma tabela SOR no banco de dados.
    """
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo CSV não encontrado em '{csv_path}'")
        return

    print(f"Iniciando ingestão do '{os.path.basename(csv_path)}' para a tabela '{table_name}'...")
    
    try:
        df = pd.read_csv(csv_path)

        # Tratamento para a coluna 'cast' no arquivo de créditos
        if 'cast' in df.columns:
            df.rename(columns={'cast': '"cast"'}, inplace=True)

        df.to_sql(table_name, conn, if_exists='append', index=False)
        
        print(f"Ingestão de {len(df)} registros para '{table_name}' concluída.")

    except Exception as e:
        print(f"Ocorreu um erro durante a ingestão para a tabela '{table_name}': {e}")

def ingest_all_data(conn: Connection, data_folder: str):
    """
    Orquestra a ingestão de todos os arquivos CSV para suas respectivas tabelas SOR.
    """
    print("\n--- Iniciando a ingestão de dados (CSV -> SOR) ---")
    
    ingestion_map = {
        "tmdb_5000_movies.csv": "sor_tmdb_movies",
        "tmdb_5000_credits.csv": "sor_tmdb_credits"
    }
    
    for csv_file, table_name in ingestion_map.items():
        csv_path = os.path.join(data_folder, csv_file)
        ingest_csv_to_sor(conn, csv_path, table_name)