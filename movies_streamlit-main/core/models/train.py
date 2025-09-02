from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

def train_regressor(X, y, preprocessor, test_size=0.2):
    """Treina um modelo de regressão e retorna o modelo e os dados de teste."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Cria o pipeline final que inclui o pré-processamento e o modelo
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])
    
    print("Treinando o modelo de Regressão Linear...")
    model_pipeline.fit(X_train, y_train)
    
    return model_pipeline, X_test, y_test