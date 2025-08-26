import sys
import os

# Adiciona a raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np

# (Opcional) heatmap
try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

# Imports internos do projeto
from core.data.io import read_csv_smart
from core.features.preprocess import make_preprocess_pipeline
from core.models.train import train_classifier, train_regressor
from core.models.predict import evaluate_classifier, evaluate_regressor
from core.explain.coefficients import extract_logit_importances, extract_linear_importances
from core.chatbot.rules import answer_from_metrics

# Configuração da página
st.set_page_config(page_title="Chatbot MVP - Empréstimos", layout="wide")
st.title("🏦 Chatbot MVP — Análise de Aprovação de Empréstimos")

# Estado inicial da sessão
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Olá! Envie um CSV com dados de empréstimos, treine o modelo e depois me pergunte sobre métricas ou variáveis importantes. 🙂"}
    ]
for key in ["last_task", "last_metrics", "last_importances"]:
    st.session_state.setdefault(key, None)

# Sidebar
with st.sidebar:
    st.header("Configurações")
    task = st.selectbox("Tarefa", ["Classificação (Loan_Status)", "Regressão (Approval_Score)"])
    test_size = st.slider("Tamanho do teste", 0.1, 0.4, 0.2, 0.05)
    uploaded = st.file_uploader("Envie o CSV de Empréstimos", type=["csv"])

# Abas
tab_train, tab_chat = st.tabs(["📊 Treino & Métricas", "💬 Chat"])

# Aba de treino
with tab_train:
    question_train = st.text_input("Pergunte algo durante o treino (opcional):", placeholder="Ex.: Quais variáveis mais importam?")

    if uploaded:
        df = read_csv_smart(uploaded)
        st.write("Prévia dos dados", df.head())

        # Remover colunas desnecessárias
        drop_cols = [c for c in ["Loan_ID"] if c in df.columns]
        df = df.drop(columns=drop_cols)

        # Classificação
        if task.startswith("Classificação"):
            target = "Loan_Status"
            if target not in df.columns:
                st.error(f"Coluna alvo '{target}' não encontrada no CSV.")
                st.stop()

            # ✅ Conversão de 'Y'/'N' para 1/0
            df[target] = df[target].map({'Y': 1, 'N': 0})
            if df[target].isnull().any():
                st.error("Valores inválidos encontrados em 'Loan_Status'. Esperado: 'Y' ou 'N'.")
                st.stop()

            y = df[target]
            X = df.drop(columns=[target])

            pre = make_preprocess_pipeline(X)
            model, X_test, y_test = train_classifier(X, y, pre, test_size=test_size)

            # Métricas
            metrics, cm = evaluate_classifier(model, X_test, y_test)
            st.subheader("📈 Métricas (Classificação)")
            st.json(metrics)

            # Matriz de confusão
            st.subheader("🧮 Matriz de Confusão")
            cm_arr = np.array(cm)
            idx = ["Verdadeiro 0", "Verdadeiro 1"][:cm_arr.shape[0]]
            cols = ["Predito 0", "Predito 1"][:cm_arr.shape[1]]
            df_cm = pd.DataFrame(cm_arr, index=idx, columns=cols)
            st.dataframe(df_cm, use_container_width=True)

            if HAS_MPL:
                fig, ax = plt.subplots()
                im = ax.imshow(df_cm.values, cmap="Blues")
                ax.set_xticks(range(df_cm.shape[1])); ax.set_xticklabels(cols)
                ax.set_yticks(range(df_cm.shape[0])); ax.set_yticklabels(idx)
                ax.set_xlabel("Predito"); ax.set_ylabel("Verdadeiro")
                for i in range(df_cm.shape[0]):
                    for j in range(df_cm.shape[1]):
                        ax.text(j, i, df_cm.values[i, j], ha="center", va="center")
                fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                st.pyplot(fig, use_container_width=True)

            # Importâncias
            importances = extract_logit_importances(model, X.columns, pre)
            st.subheader("🔎 Importâncias (Odds Ratio / Coef)")
            st.dataframe(importances.head(20), use_container_width=True)

            # Estado do chat
            st.session_state.last_task = task
            st.session_state.last_metrics = metrics
            st.session_state.last_importances = importances

            if question_train:
                ans = answer_from_metrics(question_train, task, metrics, importances)
                st.info(ans)
                st.session_state.chat_messages.append({"role": "user", "content": question_train})
                st.session_state.chat_messages.append({"role": "assistant", "content": ans})

        # Regressão
        else:
            target = "Approval_Score"
            if target not in df.columns:
                st.error(f"Coluna alvo '{target}' não encontrada no CSV.")
                st.stop()
            y = df[target]
            X = df.drop(columns=[target])

            pre = make_preprocess_pipeline(X)
            model, X_test, y_test = train_regressor(X, y, pre, test_size=test_size)

            # Métricas
            metrics = evaluate_regressor(model, X_test, y_test)
            st.subheader("📈 Métricas (Regressão)")
            st.json(metrics)

            # Importâncias
            importances = extract_linear_importances(model, X.columns, pre)
            st.subheader("🔎 Importâncias (Coeficientes)")
            st.dataframe(importances.head(20), use_container_width=True)

            st.session_state.last_task = task
            st.session_state.last_metrics = metrics
            st.session_state.last_importances = importances

            if question_train:
                ans = answer_from_metrics(question_train, task, metrics, importances)
                st.info(ans)
                st.session_state.chat_messages.append({"role": "user", "content": question_train})
                st.session_state.chat_messages.append({"role": "assistant", "content": ans})
    else:
        st.info("⬆️ Envie um CSV com dados de empréstimos na barra lateral para começar.")

# Aba de chat
with tab_chat:
    st.caption("Converse com o assistente sobre as métricas e importâncias do último treino.")
    for m in st.session_state.chat_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Faça sua pergunta (ex.: Quais variáveis mais importam?)")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        task_ctx = st.session_state.get("last_task")
        metrics_ctx = st.session_state.get("last_metrics")
        importances_ctx = st.session_state.get("last_importances")

        if task_ctx and metrics_ctx is not None and importances_ctx is not None:
            ans = answer_from_metrics(prompt, task_ctx, metrics_ctx, importances_ctx)
        else:
            ans = "Ainda não há um modelo treinado nesta sessão. Vá em **📊 Treino & Métricas**, envie o CSV e treine o modelo primeiro."

        st.session_state.chat_messages.append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
