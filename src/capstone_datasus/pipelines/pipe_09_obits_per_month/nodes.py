import pandas as pd
import matplotlib.pyplot as plt
import logging
from pathlib import Path
from typing import List
import numpy as np
import os
from scipy.stats import chi2_contingency


logger = logging.getLogger(__name__)


def plot_obits_rate_per_month(
    df: pd.DataFrame,
    output_path: str,
    col_mes: str = "PA_MVM",
    col_obito: str = "PA_OBITO"
) -> None:

    """
    Gera gráfico de linha da taxa de óbito por mês.

    Args:
        df: DataFrame de entrada
        col_mes: coluna de mês (ex: PA_MVM no formato YYYYMM)
        col_obito: coluna binária de óbito (ex: PA_OBITO)
        output_path: caminho onde a imagem será salva
    """

    # Removendo registros do tipo Consolidado pois não são dados individuais
    df = df[df["PA_DOCORIG"] != 'C']

    # Garantir tipos corretos
    df[col_obito] = df[col_obito].astype(int)

    # Converter YYYYMM para datetime
    df["mes_dt"] = pd.to_datetime(df[col_mes].astype(str), format="%Y%m")

    # Calcular taxa de óbito por mês
    df_agg = (
        df.groupby("mes_dt")[col_obito]
        .mean()
        .reset_index()
        .sort_values("mes_dt")
    )

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df_agg["mes_dt"], df_agg[col_obito], marker="o")

    plt.title("Taxa de Óbito por Mês")
    plt.xlabel("Ano - Mês")
    plt.ylabel("Taxa de Óbito (%)")

    plt.grid(True)

    # Melhorar eixo x
    plt.xticks(rotation=45)

    # Salvar
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()



REPLACE_DICT_TPUPS = {
    "43": "Farmácia",
    "36": "Clínica",
    "04": "Policlinica",
    "05": "Hospital Geral",
    "07": "Hospital Especializado",
    "39": "SADT"
}

REPLACE_DICT_TPFIN ={
    "02": "MAC",
    "04": "FAEC",
    "06": "Assist_Farmacêutica"
}


def replace_tuple(tuple, dict1, dict2):
    if dict2 is None:
        return (
            dict1.get(tuple[0], tuple[0]),
            tuple[1]
        )
    return (
        dict1.get(tuple[0], tuple[0]),
        dict2.get(tuple[1], tuple[1])
    )


def plot_obit_rate_monthly_stratified(
    df: pd.DataFrame,
    output_dir: str,
    col_mes: str = "PA_MVM",
    col_obito: str = "PA_OBITO",
    strat_cols: List[str] = None,
    min_samples: int = 5000,
) -> None:
    """
    Gera múltiplos gráficos de taxa de óbitos por mês,
    estratificados por colunas categóricas.

    Parâmetros:
    - strat_cols: lista de colunas para estratificação (ex: ["PA_TPUPS"])
    - min_samples: mínimo de registros por grupo para gerar gráfico
    """

    logger = logging.getLogger(__name__)

    # Removendo registros do tipo Consolidado
    df = df[df["PA_DOCORIG"] != 'C']

    if strat_cols is None:
        strat_cols = []

    # Mantém apenas colunas necessárias
    cols_needed = [col_mes, col_obito] + strat_cols
    df = df[cols_needed].copy()

    # Tipos
    df[col_mes] = df[col_mes].astype(str)
    df[col_obito] = pd.to_numeric(df[col_obito], errors="coerce")

    # Converter mês
    df["mes_dt"] = pd.to_datetime(df[col_mes], format="%Y%m", errors="coerce")

    # Remove inválidos
    df = df.dropna(subset=["mes_dt", col_obito])

    # Cria diretório
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Agrupamento
    if not strat_cols:
        groups = [("global", df)]
    else:
        groups = df.groupby(strat_cols)

    for group_key, group_df in groups:

        # Nome do grupo
        if isinstance(group_key, tuple) and len(group_key) == 2:
            group_name = replace_tuple(group_key, REPLACE_DICT_TPFIN, REPLACE_DICT_TPUPS)
        elif isinstance(group_key, tuple) and len(group_key) == 1:
            group_name = group_key[0]
            for key, value in REPLACE_DICT_TPUPS.items():
                if group_name == key:
                    group_name = value

        else:
            group_name = str(group_key)

        # Filtra grupos pequenos
        if len(group_df) < min_samples:
            continue

        # Taxa de óbito por mês (média do binário)
        df_agg = (
            group_df
            .groupby("mes_dt")[col_obito]
            .mean()
            .reset_index()
            .sort_values("mes_dt")
        )

        # Plot
        plt.figure(figsize=(12, 6))
        plt.plot(df_agg["mes_dt"], df_agg[col_obito], marker="o")

        plt.title(f"Taxa de óbitos por mês | {group_name}")
        plt.xlabel("Mês")
        plt.ylabel("Taxa de óbito")

        plt.grid(True)
        plt.xticks(rotation=45)

        plt.tight_layout()

        # Caminho do arquivo
        file_path = Path(output_dir) / f"obit_rate_monthly_{group_name}.png"

        plt.savefig(file_path)
        plt.close()

        logger.info("Salvo: %s | n=%d", file_path, len(group_df))



def analyze_obit_vs_glosa(
    df: pd.DataFrame,
    output_dir: str,
    col_estab: str = "PA_TPUPS",
    col_data: str = "PA_MVM",  # formato YYYYMM (ex: 201910)
    col_val_apr: str = "PA_VALAPR",
    col_val_tot: str = "PA_VALPRO",  # ou equivalente na sua base
    col_obito: str = "PA_OBITO",  # precisa já existir (1 = óbito, 0 = não)
    estab_value: str = "36"
):
    """
    Analisa a relação entre óbito e glosa comparando fev/2019 vs out/2019
    para um tipo de estabelecimento específico.
    """

    os.makedirs(output_dir, exist_ok=True)

    df = df[df["PA_DOCORIG"] != 'C']

    # Filtrar estabelecimento
    df_estab = df[df[col_estab] == estab_value].copy()

    # Filtrar meses
    df_estab = df_estab[df_estab[col_data].isin(["201902", "201910"])].copy()

    # Criar flag de glosa
    df_estab["FLAG_GLOSA"] = (df_estab[col_val_apr] < df_estab[col_val_tot]).astype(int)

    print("quantidade glosa 201902:" , df_estab[(df_estab["FLAG_GLOSA"] == 1) & (df_estab[col_data] == "201902")]["FLAG_GLOSA"].sum())
    print("quantidade glosa 201910:" , df_estab[(df_estab["FLAG_GLOSA"] == 1) & (df_estab[col_data] == "201910")]["FLAG_GLOSA"].sum())
    print("mortes 201902 com glosa:", df_estab[(df_estab[col_obito] == 1) & (df_estab["FLAG_GLOSA"] == 1) & (df_estab[col_data] == "201902")][col_obito].sum())
    print("mortes 201910 com glosa:", df_estab[(df_estab[col_obito] == 1) & (df_estab["FLAG_GLOSA"] == 1) & (df_estab[col_data] == "201910")][col_obito].sum())
    print("mortes 201902 sem glosa:", df_estab[(df_estab[col_obito] == 1) & (df_estab["FLAG_GLOSA"] == 0) & (df_estab[col_data] == "201902")][col_obito].sum())
    print("mortes 201910 sem glosa:", df_estab[(df_estab[col_obito] == 1) & (df_estab["FLAG_GLOSA"] == 0) & (df_estab[col_data] == "201910")][col_obito].sum())

    results = {}

    for comp in ["201902", "201910"]:
        df_mes = df_estab[df_estab[col_data] == comp]

        # Tabela de contingência
        contingency = pd.crosstab(df_mes[col_obito], df_mes["FLAG_GLOSA"])

        # Garantir formato 2x2
        contingency = contingency.reindex(index=[0,1], columns=[0,1], fill_value=0)

        # Teste qui-quadrado
        chi2, p_value, _, _ = chi2_contingency(contingency)

        # Proporções importantes
        total_obitos = df_mes[col_obito].sum()
        obitos_com_glosa = df_mes[(df_mes[col_obito] == 1) & (df_mes["FLAG_GLOSA"] == 1)].shape[0]

        prop_glosa_em_obitos = (
            obitos_com_glosa / total_obitos if total_obitos > 0 else 0
        )

        results[comp] = {
            "contingency": contingency,
            "p_value": p_value,
            "prop_glosa_em_obitos": prop_glosa_em_obitos
        }

        # Plot simples
        contingency.plot(kind="bar", stacked=True)
        plt.title(f"Óbito vs Glosa - {comp}")
        plt.xlabel("Óbito (0=Não, 1=Sim)")
        plt.ylabel("Quantidade")

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"obito_vs_glosa_{comp}.png"))
        plt.close()

    # Comparação direta
    comparison = pd.DataFrame({
        "mes": ["201902", "201910"],
        "prop_glosa_em_obitos": [
            results["201902"]["prop_glosa_em_obitos"],
            results["201910"]["prop_glosa_em_obitos"]
        ],
        "p_value": [
            results["201902"]["p_value"],
            results["201910"]["p_value"]
        ]
    })

    comparison.to_csv(os.path.join(output_dir, "comparacao_obito_glosa.csv"), index=False)

    return comparison