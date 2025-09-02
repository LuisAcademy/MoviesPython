Kaggle Chatbot MVP
MVP educacional para responder perguntas sobre datasets do Kaggle via Streamlit, com treino de modelos simples (regressão logística ou linear) e documentação organizada.

📖 Documentação
A documentação completa está na pasta docs/:

PMC
Arquitetura
Modelagem de Dados
Governança LGPD/DAMA
Testes
Deploy
🖥️ Como rodar o projeto no Visual Studio Code
1. Abrir o projeto
Abra o VS Code.
Vá em File → Open Folder e escolha a pasta do seu projeto, exemplo, movies_streamlit/.
2. Criar e ativar ambiente virtual
No terminal integrado do VS Code (Ctrl+):

# Criar ambiente virtual
python3 -m venv .venv

# Ativar no Linux/Mac
source .venv/bin/activate

# Ativar no Windows (PowerShell)
.venv\Scripts\Activate.ps1
⚠️ No canto inferior direito do VS Code, selecione o interpretador Python da pasta .venv.

3. Instalar dependências
Com o ambiente ativo:

pip install -r requirements.txt
4. Rodar o Streamlit
No terminal do VS Code:

streamlit run app/main_app.py
O app abrirá no navegador em http://localhost:8501.

5. Trabalhar com o código
Front-end: app/main_app.py (UI em Streamlit).
Back-end: core/ (dados, features, modelos, explicabilidade e chatbot).
Notebooks: notebooks/01_eda_titanic.ipynb (exploração inicial).
6. Rodar testes
pytest tests/
📂 Estrutura de pastas
kaggle-chatbot-mvp/
├─ app/            # Interface com o usuário (Streamlit)
├─ core/           # Lógica de negócio (dados, modelos, chatbot)
├─ configs/        # Arquivos de configuração
├─ data/           # Dados brutos, processados e modelos
├─ notebooks/      # Notebooks de exploração (EDA)
├─ tests/          # Testes unitários e de integração
├─ docs/           # Documentação (PMC, arquitetura, dados, LGPD, etc.)
├─ requirements.txt
└─ README.md
🚀 Deploy
Para publicar rapidamente, veja docs/deployment.md.
