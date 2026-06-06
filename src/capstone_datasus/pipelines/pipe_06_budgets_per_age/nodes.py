import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

def plot_mean_median_per_age(
    df: pd.DataFrame,
    output_path: str,
    col_idade: str = "PA_IDADE",
    col_budget: str = "PA_VALAPR",
):
    logger = logging.getLogger(__name__)
    
    # Removendo registros do tipo Consolidado pois não são dados individuais
    df = df[df["PA_DOCORIG"] != 'C']

    # Mantém apenas colunas necessárias
    df = df[[col_idade, col_budget]].copy()

    # Garante tipo numérico
    df[col_idade] = pd.to_numeric(df[col_idade], errors="coerce")
    df[col_budget] = pd.to_numeric(df[col_budget], errors="coerce")

    # Remove inválidos
    df = df[(df[col_idade] >= 1) & (df[col_idade] <= 100)]

    # Bucketização
    df["idade_bucket"] = ((df[col_idade] - 1) // 10).astype(int)

    # Agrupamento
    agg_df = (
        df.groupby("idade_bucket")[col_budget]
        .agg(media="mean", mediana="median")
        .reset_index()
        .sort_values(by="idade_bucket")
    )

    # Plot
    plt.figure(figsize=(10, 6))
    
    plt.plot(agg_df["idade_bucket"], agg_df["media"], marker="o", label="Média")
    plt.plot(agg_df["idade_bucket"], agg_df["mediana"], marker="s", label="Mediana")

    plt.title("Média e Mediana de Valor aprovado por faixa de Idade")
    plt.xlabel("Faixa de idade (0=1-10, 1=11-20, ...)")
    plt.ylabel("Valor aprovado (R$)")
    #plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    # Garante diretório
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva
    plt.savefig(output_path)
    plt.close()

    logger.info("Gráfico salvo em: %s", output_path)

    return None



def plot_boxplot_per_age(
    df: pd.DataFrame,
    output_path: str,
    col_idade: str = "PA_IDADE",
    col_budget: str = "PA_VALAPR",
):
    logger = logging.getLogger(__name__)

    # Removendo registros do tipo Consolidado pois não são dados individuais
    df = df[df["PA_DOCORIG"] != 'C']

    # Mantém apenas colunas necessárias
    df = df[[col_idade, col_budget]].copy()

    # Garante tipo numérico
    df[col_idade] = pd.to_numeric(df[col_idade], errors="coerce")
    df[col_budget] = pd.to_numeric(df[col_budget], errors="coerce")

    # Remove inválidos
    df = df[(df[col_idade] >= 1) & (df[col_idade] <= 100)]

    # Bucketização
    df["idade_bucket"] = ((df[col_idade] - 1) // 10).astype(int)

    #ver apenas faixas 0 e 7 (1-10 e 71-80)
    #df = df[df["idade_bucket"].isin([0, 7])]

    # Plot
    plt.figure(figsize=(10, 6))
    
    df.boxplot(column=col_budget, by="idade_bucket", grid=False)

    plt.title("Boxplot de Valor aprovado por faixa de Idade")
    plt.suptitle("")
    #plt.xlabel("Faixa de idade (0=1-10, 1=11-20, ...)")
    plt.xlabel("Faixa de idade (0=1-10, 7=71-80)")
    plt.ylabel("Valor aprovado (R$)")
    plt.axhline(y=10000, color='red', linestyle='--', linewidth=2)

    # Garante diretório
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva
    plt.savefig(output_path)
    plt.close()

    logger.info("Gráfico salvo em: %s", output_path)

    return None