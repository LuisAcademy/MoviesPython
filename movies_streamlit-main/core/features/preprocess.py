from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

def make_preprocess_pipeline(X):
    """Cria um pipeline de pré-processamento para as features."""
    # Para este projeto, todas as nossas features são numéricas.
    # Vamos apenas aplicar a padronização (StandardScaler).
    numeric_features = X.select_dtypes(include=['number']).columns
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features)
        ],
        remainder='passthrough' # Mantém outras colunas, se houver
    )
    
    return preprocessor