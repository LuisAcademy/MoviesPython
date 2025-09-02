import streamlit as st
import pandas as pd
import os
import pickle
import sys

# --- INÍCIO DA SOLUÇÃO 2: CORREÇÃO DO CAMINHO (PYTHONPATH) ---
# Adiciona o diretório raiz do projeto (que está um nível acima de onde este
# arquivo pode estar) ao caminho de busca de módulos do Python.
# Isso garante que a importação "from core..." funcione corretamente.
#
# __file__ -> Caminho do arquivo atual (ex: .../app/main_app.py)
# os.path.dirname(__file__) -> Caminho da pasta do arquivo (ex: .../app)
# os.path.dirname(...) -> Caminho da pasta raiz do projeto (ex: ...)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# --- FIM DA SOLUÇÃO ---


# --- Checagem de Bibliotecas ---
try:
    from sklearn.model_selection import train_test_split
except ImportError:
    st.error("A biblioteca scikit-learn não está instalada. Rode: pip install scikit-learn")
    sys.exit(1)

# --- Importar as Funções do Projeto ---
# Agora esta parte funcionará, pois o Python sabe onde encontrar o módulo 'core'
from core.database import (
    create_database_connection, create_tables, transform_data, drop_database,
    load_sot_data_for_training
)
from core.ingestion import ingest_all_data
from core.features.preprocess import make_preprocess_pipeline
from core.models.train import train_regressor
from core.models.predict import evaluate_regressor
from core.explain.coefficients import extract_linear_importances
from core.chatbot.rules import answer_from_metrics

# --- Configurações da Página e Diretórios ---
st.set_page_config(page_title="Análise de Filmes TMDB", layout="wide")

# Ajusta os caminhos para serem relativos à raiz do projeto
DB_FILE = os.path.join(project_root, "tmdb.db")
DATA_FOLDER = os.path.join(project_root, "data")
SQL_FOLDER = os.path.join(project_root, "sql")
MODEL_DIR = os.path.join(project_root, "model")

if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
MODEL_PATH = os.path.join(MODEL_DIR, "movie_rating_predictor.pickle")

# --- Estado da Sessão (Session State) ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Olá! Execute o pipeline e depois me pergunte sobre o modelo treinado."}
    ]
for key in ["model_trained", "last_metrics", "last_importances"]:
    st.session_state.setdefault(key, None)

# --- Título e Sidebar ---
st.title("🎬 Análise Preditiva de Notas de Filmes (TMDB)")

with st.sidebar:
    st.header("1. Configurações do Modelo")
    st.info("Esta aplicação treina um modelo para prever a nota de um filme (`vote_average`).")
    test_size = st.slider("Tamanho do conjunto de teste", 0.1, 0.4, 0.2, 0.05)
    
    st.header("2. Controle do Pipeline")
    if st.button("Executar Pipeline Completo", type="primary"):
        with st.spinner("Executando pipeline de dados e treino... Aguarde!"):
            # Etapa 1: Limpar e Criar DB
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            conn = create_database_connection(DB_FILE)

            if conn:
                # Etapa 2: Criar tabelas, ingerir e transformar dados
                create_tables(conn, SQL_FOLDER)
                ingest_all_data(conn, DATA_FOLDER)
                transform_data(conn, SQL_FOLDER)

                # Etapa 3: Carregar dados para treino
                df_train = load_sot_data_for_training(conn)
                
                # Etapa 4: Treinar o modelo
                target = "vote_average"
                y = df_train[target]
                X = df_train.drop(columns=[target])
                
                pre = make_preprocess_pipeline(X)
                model, X_test, y_test = train_regressor(X, y, pre, test_size=test_size)
                
                # Etapa 5: Salvar o modelo e as métricas
                with open(MODEL_PATH, "wb") as f:
                    pickle.dump(model, f)
                
                metrics = evaluate_regressor(model, X_test, y_test)
                importances = extract_linear_importances(model, X.columns)
                
                # Salvar no estado da sessão para usar nas abas
                st.session_state.model_trained = True
                st.session_state.last_task = "Regressão"
                st.session_state.last_metrics = metrics
                st.session_state.last_importances = importances
                
                conn.close() # Fechar conexão após o uso
                st.success("Pipeline executado com sucesso!")
            else:
                st.error("Falha ao conectar ao banco de dados.")

    if st.button("Limpar Ambiente"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        # Resetar o estado da sessão
        for key in ["model_trained", "last_metrics", "last_importances"]:
            st.session_state[key] = None
        st.info("Banco de dados e modelo limpos. Estado resetado.")
        st.rerun()

# --- Abas Principais ---
tab_results, tab_chat = st.tabs(["📊 Resultados do Treino", "💬 Chat com o Modelo"])

with tab_results:
    if not st.session_state.model_trained:
        st.info("⬅️ Execute o pipeline na barra lateral para ver os resultados.")
    else:
        st.subheader("📈 Métricas de Desempenho (Regressão)")
        st.json(st.session_state.last_metrics)
        
        st.subheader("🔎 Importância das Features (Coeficientes do Modelo)")
        st.dataframe(st.session_state.last_importances, use_container_width=True)
        
        if os.path.exists(MODEL_PATH):
            st.success(f"Modelo salvo com sucesso em: `{MODEL_PATH}`")

with tab_chat:
    st.caption("Converse sobre os resultados do último modelo treinado.")
    for m in st.session_state.chat_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ex: Qual a variável mais importante?")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        if not st.session_state.model_trained:
            ans = "O modelo ainda não foi treinado. Por favor, execute o pipeline primeiro."
        else:
            ans = answer_from_metrics(
                prompt,
                st.session_state.last_task,
                st.session_state.last_metrics,
                st.session_state.last_importances
            )
        
        st.session_state.chat_messages.append({"role": "assistant", "content": ans})
        st.rerun()