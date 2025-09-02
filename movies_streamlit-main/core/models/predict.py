from sklearn.metrics import mean_squared_error, r2_score

def evaluate_regressor(model, X_test, y_test):
    """Avalia o modelo e retorna um dicionário de métricas."""
    predictions = model.predict(X_test)
    
    metrics = {
        "R-squared (R2)": r2_score(y_test, predictions),
        "Mean Squared Error (MSE)": mean_squared_error(y_test, predictions)
    }
    
    print(f"Métricas de avaliação: {metrics}")
    return metrics