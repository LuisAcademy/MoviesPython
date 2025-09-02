def answer_from_metrics(prompt, task, metrics, importances):
    """Gera uma resposta baseada em regras simples sobre as métricas do modelo."""
    prompt = prompt.lower()
    
    if "importante" in prompt or "relevante" in prompt or "influencia" in prompt:
        top_feature = importances.iloc[0]['Feature']
        return f"Com base nos coeficientes do modelo, a variável mais influente foi **{top_feature}**."

    elif "métrica" in prompt or "performance" in prompt or "desempenho" in prompt:
        return f"As principais métricas foram: **R-squared de {metrics['R-squared (R2)']:.2f}** e **MSE de {metrics['Mean Squared Error (MSE)']:.2f}**."

    elif "r2" in prompt or "r-squared" in prompt:
        return f"O **R-squared (R2)** do modelo foi de **{metrics['R-squared (R2)']:.2f}**. Isso representa a proporção da variância da variável dependente que é previsível a partir das variáveis independentes."

    elif "mse" in prompt or "erro" in prompt:
        return f"O **Mean Squared Error (MSE)** foi de **{metrics['Mean Squared Error (MSE)']:.2f}**. Ele mede a média dos quadrados dos erros entre os valores estimados e os valores reais."
        
    else:
        return "Desculpe, não entendi a pergunta. Você pode perguntar sobre as 'métricas' ou qual a variável 'mais importante'."