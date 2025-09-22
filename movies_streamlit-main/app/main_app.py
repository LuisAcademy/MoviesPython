import streamlit as st
import pandas as pd
import os
import pickle
import sys

# --- INÍCIO DA SOLUÇÃO 2: CORREÇÃO DO CAMINHO (PYTHONPATH) ---
# Adiciona o diretório raiz do projeto ao caminho de busca de módulos do Python.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
# --- FIM DA SOLUÇÃO ---

# --- Checagem de Bibliotecas ---
try:
    from sklearn.model_selection import train_test_split
except ImportError:
    st.error("A biblioteca scikit-learn não está instalada. Rode: pip install scikit-learn")
    st.stop()

# --- Importar as Funções do Projeto ---
from core.database import (
    create_database_connection,
    load_sot_data_for_training
)
# As funções 'create_tables' e 'transform_data' foram removidas das importações.
from core.features.preprocess import make_preprocess_pipeline
from core.models.train import train_regressor
from core.models.predict import evaluate_regressor
from core.explain.coefficients import extract_linear_importances
from core.chatbot.rules import answer_from_metrics

# --- Configurações da Página e Diretórios ---
st.set_page_config(page_title="Análise de Filmes TMDB", layout="wide")

# Ajusta os caminhos para serem relativos à raiz do projeto
DB_FILE = os.path.join(project_root, "tmdb.db")
MODEL_DIR = os.path.join(project_root, "model")

if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
MODEL_PATH = os.path.join(MODEL_DIR, "movie_rating_predictor.pickle")

# --- Estado da Sessão (Session State) ---
# Inicializa o estado para garantir que as chaves existam
if "model_trained" not in st.session_state:
    st.session_state.model_trained = False
if "predictions_made" not in st.session_state:
    st.session_state.predictions_made = False
if "prediction_df" not in st.session_state:
    st.session_state.prediction_df = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role": "assistant", "content": "Olá! Treine um modelo ou carregue um modelo salvo para começar."}]
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "importances" not in st.session_state:
    st.session_state.importances = None

# --- Funções Auxiliares ---
@st.cache_data
def convert_df_to_csv(df):
    """Converte um DataFrame para CSV codificado em UTF-8."""
    return df.to_csv(index=False).encode('utf-8')

# --- Título e Sidebar ---
st.title("🎬 Pipeline Preditivo de Notas de Filmes (TMDB)")

with st.sidebar:
    st.header("1. Upload dos Dados")
    uploaded_files = st.file_uploader(
        "Envie os arquivos CSV do TMDB para treino e/ou um arquivo para previsão",
        type=["csv"],
        accept_multiple_files=True
    )

    st.header("2. Ações do Pipeline")

    # --- AÇÃO 1: Treinar um novo modelo ---
    st.subheader("Treinar Novo Modelo")
    test_size = st.slider("Tamanho do conjunto de teste (validação)", 0.1, 0.4, 0.2, 0.05)
    if st.button("Executar Treinamento", type="primary"):
        movies_file = next((f for f in uploaded_files if "movies" in f.name.lower()), None)
        credits_file = next((f for f in uploaded_files if "credits" in f.name.lower()), None)

        if movies_file and credits_file:
            with st.spinner("Executando pipeline de dados e treino..."):
                # Etapa 1: Limpar e Criar DB
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
                conn = create_database_connection(DB_FILE)

                if conn:
                    pipeline_success = False
                    try:
                        # Etapa 2.1: Ingestão de Dados
                        movies_df = pd.read_csv(movies_file)
                        credits_df = pd.read_csv(credits_file)
                        movies_df.to_sql("sor_movies", conn, if_exists="replace", index=False)
                        credits_df.to_sql("sor_credits", conn, if_exists="replace", index=False)

                        # Etapa 2.2: Transformação de Dados (junção das tabelas)
                        sor_movies = pd.read_sql_query("SELECT * FROM sor_movies", conn)
                        sor_credits = pd.read_sql_query("SELECT * FROM sor_credits", conn)
                        
                        sor_credits.rename(columns={'movie_id': 'id'}, inplace=True)
                        
                        sot_df = pd.merge(sor_movies, sor_credits, on='id')
                        
                        sot_df.to_sql("sot_movies", conn, if_exists="replace", index=False)

                        # Etapa 3: Carregar dados para treino
                        df_train = load_sot_data_for_training(conn)
                        
                        if df_train.empty:
                            st.error("A tabela de treino está vazia. Verifique a etapa de transformação.")
                        else:
                            # Etapa 4: Treinar o modelo
                            target = "vote_average"
                            y = df_train[target]
                            X = df_train.drop(columns=[target])
                            
                            pre = make_preprocess_pipeline(X)
                            model, X_test, y_test = train_regressor(X, y, pre, test_size=test_size)
                            
                            # Etapa 5: Salvar o modelo e as métricas na sessão
                            with open(MODEL_PATH, "wb") as f:
                                pickle.dump(model, f)
                            
                            st.session_state.metrics = evaluate_regressor(model, X_test, y_test)
                            st.session_state.importances = extract_linear_importances(model, X.columns, pre)
                            st.session_state.model_trained = True
                            st.session_state.predictions_made = False # Reseta a aba de previsão
                            
                            pipeline_success = True

                    except Exception as e:
                        st.error(f"Ocorreu um erro durante o pipeline: {e}")
                    finally:
                        # Esta linha garante que a conexão seja fechada, liberando o arquivo.
                        conn.close()
                        if pipeline_success:
                            st.success("Modelo treinado e salvo com sucesso!")
                else:
                    st.error("Falha ao conectar ao banco de dados.")
        else:
            st.warning("Arquivos 'tmdb_5000_movies.csv' e 'tmdb_5000_credits.csv' são necessários para o treino.")

    # --- AÇÃO 2: Usar o modelo salvo para prever ---
    st.subheader("Usar Modelo Existente")
    if st.button("Carregar Modelo e Fazer Previsões"):
        if not os.path.exists(MODEL_PATH):
            st.error("Nenhum modelo treinado foi encontrado! Execute o treinamento primeiro.")
        else:
            predict_file = next((f for f in uploaded_files if "predict" in f.name.lower() or "test" in f.name.lower()), None)
            
            if predict_file:
                with st.spinner("Carregando modelo e fazendo previsões..."):
                    df_predict = pd.read_csv(predict_file)
                    
                    with open(MODEL_PATH, 'rb') as f:
                        model = pickle.load(f)

                    # Faz as previsões
                    predictions = model.predict(df_predict)
                    
                    # Monta o DataFrame de resultados
                    result_df = df_predict.copy()
                    result_df['predicted_vote_average'] = predictions
                    
                    st.session_state.prediction_df = result_df
                    st.session_state.predictions_made = True
                st.success("Previsões geradas com sucesso!")
            else:
                st.warning("Envie um arquivo para prever (deve conter 'predict' ou 'test' no nome).")

    # --- AÇÃO 3: Limpeza ---
    st.header("3. Manutenção")
    if st.button("Limpar Tudo"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        st.session_state.clear()
        st.info("Banco de dados, modelo salvo e sessão resetados.")
        st.rerun()

# --- Abas Principais ---
tab_train, tab_predict, tab_chat = st.tabs(["📊 Resultados do Treino", "🚀 Previsões", "💬 Chat com o Modelo"])

with tab_train:
    st.header("Métricas e Importância do Modelo")
    if not st.session_state.model_trained:
        st.info("⬅️ Execute o treinamento na barra lateral para ver os resultados.")
    else:
        st.subheader("📈 Métricas (Regressão)")
        st.json(st.session_state.metrics)
        st.subheader("🔎 Importâncias (Coeficientes)")
        st.dataframe(st.session_state.importances, use_container_width=True)

with tab_predict:
    st.header("Previsões para Novos Dados")
    if not st.session_state.predictions_made:
        st.info("⬅️ Carregue um modelo e faça uma previsão na barra lateral para ver os resultados.")
    else:
        st.dataframe(st.session_state.prediction_df)
        csv_data = convert_df_to_csv(st.session_state.prediction_df)
        st.download_button(
           label="Download das Previsões em CSV",
           data=csv_data,
           file_name='movie_predictions.csv',
           mime='text/csv',
        )

with tab_chat:
    st.header("Converse com o Assistente do Modelo")
    if not st.session_state.model_trained:
        st.info("Treine um modelo primeiro para poder conversar sobre seus resultados.")
    else:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Qual a variável mais importante?"):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            response = answer_from_metrics(
                question=prompt,
                task="Regressão",
                metrics_df_or_dict=st.session_state.metrics,
                importances_df=st.session_state.importances
            )
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()

