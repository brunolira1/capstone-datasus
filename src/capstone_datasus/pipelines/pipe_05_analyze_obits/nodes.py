import pandas as pd
import matplotlib.pyplot as plt
import logging
from pathlib import Path
from typing import List


def obits_per_age_barplot(
    df: pd.DataFrame,
    output_path: str,
    col_idade: str = "PA_IDADE",
    col_obito: str = "PA_OBITO",
) -> None:
    """
    Gera um gráfico de barras com a quantidade de óbitos (PA_OBITO == 1)
    por faixa de idade (bucketizada) e salva no caminho especificado.

    Regras:
    - Ignora idades < 1
    - Bucketização:
        1-10   -> 0
        11-20  -> 1
        21-30  -> 2
        ...
        91-100 -> 9
    """

    logger = logging.getLogger(__name__)

    # Removendo registros do tipo Consolidado pois não são dados individuais
    df = df[df["PA_DOCORIG"] != "C"]

    # Mantém apenas as colunas necessárias
    df = df[[col_idade, col_obito]].copy()

    # Garante tipo numérico
    df[col_idade] = pd.to_numeric(df[col_idade], errors="coerce")
    df[col_obito] = pd.to_numeric(df[col_obito], errors="coerce")

    # Remove valores inválidos
    df = df[(df[col_idade] >= 1) & (df[col_idade] <= 100)]

    # Bucketização
    df["idade_bucket"] = ((df[col_idade] - 1) // 10).astype(int)

    # Filtra apenas óbitos
    df_obitos = df[df[col_obito] == 1]

    # Contagem por bucket
    counts = (
        df_obitos["idade_bucket"]
        .value_counts()
        .sort_index()
    )

    logger.info("Distribuição de óbitos por faixa de idade:\n%s", counts)

    # Plot
    plt.figure(figsize=(10, 6))
    ax = counts.plot(kind="bar")

    labels = [
        "1-10" if i == 0 else f"{i*10+1}-{(i+1)*10}"
        for i in counts.index
    ]
    ax.set_xticklabels(labels, rotation=0)

    plt.title("Óbitos por faixa de idade")
    plt.xlabel("Faixa de idade")
    plt.ylabel("Quantidade de óbitos")

    plt.tight_layout()

    # Garante que o diretório existe
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva imagem
    plt.savefig(output_path)
    plt.close()

    logger.info("Gráfico salvo em: %s", output_path)

def obits_rate_per_age_barplot(
    df: pd.DataFrame,
    output_path: str,
    col_idade: str = "PA_IDADE",
    col_obito: str = "PA_OBITO",
) -> None:
    """
    Gera um gráfico de barras com o percentual de óbitos
    por faixa de idade e salva no caminho especificado.

    Regras:
    - Ignora idades < 1
    - Bucketização:
        1-10   -> 0
        11-20  -> 1
        21-30  -> 2
        ...
        91-100 -> 9
    """

    logger = logging.getLogger(__name__)

    # Removendo registros do tipo Consolidado pois não são dados individuais
    df = df[df["PA_DOCORIG"] != "C"]

    # Mantém apenas colunas necessárias
    df = df[[col_idade, col_obito]].copy()

    # Garante tipo numérico
    df[col_idade] = pd.to_numeric(df[col_idade], errors="coerce")
    df[col_obito] = pd.to_numeric(df[col_obito], errors="coerce")

    # Remove inválidos
    df = df[(df[col_idade] >= 1) & (df[col_idade] <= 100)]

    # Bucketização
    df["idade_bucket"] = ((df[col_idade] - 1) // 10).astype(int)

    # Total por bucket
    total = df.groupby("idade_bucket").size()

    # Total de óbitos por bucket
    obitos = df[df[col_obito] == 1].groupby("idade_bucket").size()

    # Calcula percentual
    percentual = (obitos / total).fillna(0) * 100
    percentual = percentual.sort_index()

    logger.info("Percentual de óbitos por faixa:\n%s", percentual)

    # Plot
    plt.figure(figsize=(10, 6))
    ax = percentual.plot(kind="bar")

    labels = [
        "1-10" if i == 0 else f"{i*10+1}-{(i+1)*10}"
        for i in percentual.index
    ]
    ax.set_xticklabels(labels, rotation=0)

    plt.title("Percentual de óbitos por faixa de idade")
    plt.xlabel("Faixa de idade")
    plt.ylabel("% de óbitos")

    plt.tight_layout()

    # Garante diretório
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva
    plt.savefig(output_path)
    plt.close()

    logger.info("Gráfico salvo em: %s", output_path)


def obits_per_complexity_barplot(
    df: pd.DataFrame,
    output_path: str,
    col_obito: str = "PA_OBITO",
    col_complexity: str = "PA_NIVCPL"
) -> None:
    logger = logging.getLogger(__name__)

    df = df[[col_complexity, col_obito]].copy()
    df[col_complexity] = pd.to_numeric(df[col_complexity], errors="coerce")
    df[col_obito] = pd.to_numeric(df[col_obito], errors="coerce")

    # Filtra apenas óbitos
    df_obitos = df[df[col_obito] == 1]

    counts = (
        df_obitos[col_complexity]
        .value_counts()
        .sort_index()
    )

    logger.info("Distribuição de óbitos por complexidade do procedimento:\n%s", counts)

    # Plot
    plt.figure(figsize=(10, 6))
    counts.plot(kind="bar")

    plt.title("Óbitos por complexidade do procedimento")
    plt.xlabel("Complexidade do procedimento")
    plt.ylabel("Quantidade de óbitos")

    plt.tight_layout()

    # Garante que o diretório existe
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva imagem
    plt.savefig(output_path)
    plt.close()

    logger.info("Gráfico salvo em: %s", output_path)

    return None


REPLACE_DICT_TPFIN ={
    "02": "MAC",
    "04": "FAEC",
    "06": "Assist_Farmacêutica"
}

REPLACE_DICT_TPUPS = {
    "43": "Farmácia",
    "36": "Clínica",
    "04": "Policlinica",
    "05": "Hospital Geral",
    "07": "Hospital Especializado",
    "39": "SADT"
}


def replace_tuple(tuple, dict1, dict2):
    return (
        dict1.get(tuple[0], tuple[0]),
        dict2.get(tuple[1], tuple[1])
    )


def plot_obit_rate_stratified(
    df: pd.DataFrame,
    output_dir: str,
    col_idade: str = "PA_IDADE",
    col_obito: str = "PA_OBITO",
    strat_cols: List[str] = None,
    min_samples: int = 5000,
) -> None:
    """
    Gera múltiplos gráficos de % de óbitos por faixa etária,
    estratificados por colunas categóricas.

    Parâmetros:
    - strat_cols: lista de colunas para estratificação
      (ex: ["PA_TPUPS", "PA_TPFIN"])
    - min_samples: mínimo de registros por grupo para gerar gráfico
    """

    logger = logging.getLogger(__name__)

    # Removendo registros do tipo Consolidado pois não são dados individuais
    df = df[df["PA_DOCORIG"] != "C"]

    if strat_cols is None:
        strat_cols = []

    # Mantém apenas colunas necessárias
    cols_needed = [col_idade, col_obito] + strat_cols
    df = df[cols_needed].copy()

    # Tipos
    df[col_idade] = pd.to_numeric(df[col_idade], errors="coerce")
    df[col_obito] = pd.to_numeric(df[col_obito], errors="coerce")

    # Filtro idade
    df = df[(df[col_idade] >= 1) & (df[col_idade] <= 100)]

    # Bucketização
    df["idade_bucket"] = ((df[col_idade] - 1) // 10).astype(int)

    # Cria diretório base
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Se não houver estratificação → roda global
    if not strat_cols:
        groups = [("global", df)]
    else:
        groups = df.groupby(strat_cols)

    for group_key, group_df in groups:
        # Nome do grupo
        if isinstance(group_key, tuple):
            group_name = replace_tuple(
                group_key,
                REPLACE_DICT_TPFIN,
                REPLACE_DICT_TPUPS,
            )
        else:
            group_name = str(group_key)

        # Filtra grupos pequenos
        if len(group_df) < min_samples:
            continue

        # Total por bucket
        total = group_df.groupby("idade_bucket").size()

        # Óbitos por bucket
        obitos = (
            group_df[group_df[col_obito] == 1]
            .groupby("idade_bucket")
            .size()
        )

        # Percentual
        percentual = (obitos / total).fillna(0) * 100
        percentual = percentual.sort_index()

        # Plot
        plt.figure(figsize=(10, 6))
        ax = percentual.plot(kind="bar")

        labels = [
            "1-10" if i == 0 else f"{i*10+1}-{(i+1)*10}"
            for i in percentual.index
        ]
        ax.set_xticklabels(labels, rotation=0)

        plt.title(f"% de óbitos por idade | {group_name}")
        plt.xlabel("Faixa de idade")
        plt.ylabel("% de óbitos")

        plt.tight_layout()

        # Caminho do arquivo
        file_path = Path(output_dir) / f"obit_rate_{group_name}.png"

        plt.savefig(file_path)
        plt.close()

        logger.info("Salvo: %s | n=%d", file_path, len(group_df))

    return None