from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def plot_percentual_altas_tempo(
    df: pd.DataFrame,
    output_path: str,
    col_motivo_saida: str = "PA_MOTSAI",
    col_mes: str = "PA_MVM",
):
    """
    Gera gráfico de percentual de altas ao longo do tempo.

    Altas consideradas:
    11, 12, 14, 15, 16, 18

    Parameters
    ----------
    df : pd.DataFrame
        Base de dados.
    output_path : str
        Caminho onde a imagem será salva.
    col_motivo_saida : str
        Coluna contendo o motivo de saída.
    col_mes : str
        Coluna ano/mês (ex.: 201901).
    """

    altas = {"11", "12", "14", "15", "16", "18"}

    dados = df.copy()

    # Garantir formato string
    dados[col_motivo_saida] = (
        dados[col_motivo_saida]
        .astype(str)
        .str.strip()
    )

    # Flag de alta
    dados["is_alta"] = dados[col_motivo_saida].isin(altas).astype(int)

    # Agrupamento mensal
    mensal = (
        dados.groupby(col_mes)["is_alta"]
        .mean()
        .mul(100)
        .reset_index(name="percentual_alta")
        .sort_values(col_mes)
    )

    # Converter para datetime para melhor visualização
    mensal["data"] = pd.to_datetime(
        mensal[col_mes].astype(str),
        format="%Y%m"
    )

    plt.figure(figsize=(16, 6))

    bars = plt.bar(
        mensal["data"].dt.strftime("%Y-%m"),
        mensal["percentual_alta"]
    )

    # Valores acima das barras
    for bar, valor in zip(bars, mensal["percentual_alta"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            valor,
            f"{valor:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.title("Percentual de Altas ao Longo do Tempo")
    plt.xlabel("Mês")
    plt.ylabel("Percentual de Altas (%)")

    plt.xticks(rotation=90)
    plt.tight_layout()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()



def plot_percentual_permanencias_tempo(
    df: pd.DataFrame,
    output_path: str,
    col_motivo_saida: str = "PA_MOTSAI",
    col_mes: str = "PA_MVM",
):
    """
    Gera gráfico de percentual de permanências ao longo do tempo.

    Permanências consideradas:
    21, 22, 23, 24, 25, 26, 27, 28

    Parameters
    ----------
    df : pd.DataFrame
        Base de dados.
    output_path : str
        Caminho onde a imagem será salva.
    col_motivo_saida : str
        Coluna contendo o motivo de saída.
    col_mes : str
        Coluna ano/mês (ex.: 201901).
    """

    permanencias = {"21", "22", "23", "24", "25", "26", "27", "28"}

    dados = df.copy()

    # Garantir formato string
    dados[col_motivo_saida] = (
        dados[col_motivo_saida]
        .astype(str)
        .str.strip()
    )

    # Flag de permanência
    dados["is_permanencia"] = dados[col_motivo_saida].isin(permanencias).astype(int)

    # Agrupamento mensal
    mensal = (
        dados.groupby(col_mes)["is_permanencia"]
        .mean()
        .mul(100)
        .reset_index(name="percentual_permanencia")
        .sort_values(col_mes)
    )

    # Converter para datetime para melhor visualização
    mensal["data"] = pd.to_datetime(
        mensal[col_mes].astype(str),
        format="%Y%m"
    )

    plt.figure(figsize=(16, 6))

    bars = plt.bar(
        mensal["data"].dt.strftime("%Y-%m"),
        mensal["percentual_permanencia"]
    )

    # Valores acima das barras
    for bar, valor in zip(bars, mensal["percentual_permanencia"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            valor,
            f"{valor:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.title("Percentual de Permanências ao Longo do Tempo")
    plt.xlabel("Mês")
    plt.ylabel("Percentual de Permanências (%)")

    plt.xticks(rotation=90)
    plt.tight_layout()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()



def plot_razao_altas_permanencias(
    df: pd.DataFrame,
    output_path: str,
    col_motivo_saida: str = "PA_MOTSAI",
    col_mes: str = "PA_MVM",
):
    """
    Plota a razão entre quantidade de altas e quantidade de permanências
    ao longo do tempo.

    Razão = n_altas / n_permanencias

    Altas:
        11, 12, 14, 15, 16, 18

    Permanências:
        21, 22, 23, 24, 25, 26, 27, 28
    """

    altas = {"11", "12", "14", "15", "16", "18"}
    permanencias = {"21", "22", "23", "24", "25", "26", "27", "28"}

    dados = df.copy()

    dados[col_motivo_saida] = (
        dados[col_motivo_saida]
        .astype(str)
        .str.strip()
    )

    mensal = []

    for mes, grupo in dados.groupby(col_mes):

        qtd_altas = grupo[col_motivo_saida].isin(altas).sum()
        qtd_permanencias = grupo[col_motivo_saida].isin(permanencias).sum()

        razao = (
            qtd_altas / qtd_permanencias
            if qtd_permanencias > 0
            else None
        )

        mensal.append(
            {
                "mes": mes,
                "altas": qtd_altas,
                "permanencias": qtd_permanencias,
                "razao": razao,
            }
        )

    mensal = (
        pd.DataFrame(mensal)
        .sort_values("mes")
    )

    mensal["data"] = pd.to_datetime(
        mensal["mes"].astype(str),
        format="%Y%m"
    )

    plt.figure(figsize=(16, 6))

    plt.plot(
        mensal["data"],
        mensal["razao"],
        marker="o",
    )

    for x, y in zip(mensal["data"], mensal["razao"]):
        if pd.notna(y):
            plt.text(
                x,
                y,
                f"{y:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.title("Razão entre Altas e Permanências por Mês")
    plt.xlabel("Mês")
    plt.ylabel("Altas / Permanências")
    plt.ylim(0, 0.1)
    plt.grid(True, alpha=0.3)

    plt.xticks(
        mensal["data"],
        mensal["data"].dt.strftime("%Y-%m"),
        rotation=90,
    )

    plt.tight_layout()

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()