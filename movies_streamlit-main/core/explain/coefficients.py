import numpy as np
import pandas as pd

def extract_linear_importances(model_pipeline, original_cols):
    """
    Extrai os coeficientes de um modelo de regressão linear de dentro de um pipeline.
    Esta versão é adaptada para um pré-processador simples que não altera
    os nomes ou a ordem das features.

    Args:
        model_pipeline (sklearn.pipeline.Pipeline): O pipeline treinado que contém um passo chamado 'regressor'.
        original_cols (list): A lista de nomes das colunas originais (features).

    Returns:
        pandas.DataFrame: Um DataFrame com as features e seus coeficientes, ordenado pela importância.
    """
    # 1. Acessa o passo do regressor no nosso pipeline (que chamamos de 'regressor')
    regressor = model_pipeline.named_steps['regressor']
    
    # 2. Extrai os coeficientes do modelo treinado
    coefs = regressor.coef_.ravel()
    
    # 3. Cria o DataFrame final
    # Como nosso pré-processador não muda as colunas, podemos usar os nomes originais
    df = pd.DataFrame({
        "Feature": original_cols, 
        "Coefficient": coefs
    })

    # 4. Adiciona uma coluna com o valor absoluto para poder ordenar pela magnitude
    df["abs_coef"] = df["Coefficient"].abs()
    
    # 5. Ordena o DataFrame pela importância (maior coeficiente em módulo)
    # e remove a coluna auxiliar antes de retornar.
    return df.sort_values(by="abs_coef", ascending=False).drop(columns="abs_coef")