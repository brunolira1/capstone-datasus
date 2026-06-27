import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
#from scipy.stats import chi2_contingency


def analyze_mndif_vs_death(
    df: pd.DataFrame,
    output_path: str,
    col_mndif: str = "PA_MNDIF",
    col_obito: str = "PA_OBITO"
) -> pd.DataFrame:
    breakpoint()
    """
    Analisa se pacientes de outro município (PA_MNDIF) têm maior taxa de óbito.

    Salva:
    - Gráfico de taxa de óbito por grupo
    - Retorna dataframe com métricas + p-value

    Args:
        df: DataFrame com dados do datasus
        output_path: caminho para salvar gráfico
        col_mndif: coluna binária (0 = mesmo município, 1 = diferente)
        col_obito: coluna binária de óbito (1 = morreu)

    Returns:
        DataFrame com taxa de óbito por grupo e p-value
    """

    df = df[df["PA_DOCORIG"] != 'C']

    # Remove nulos
    df = df.dropna(subset=[col_mndif, col_obito])

    # Garante binário
    df = df[df[col_mndif].isin(['0', '1'])]
    df = df[df[col_obito].isin([0, 1])]

    # -------------------------
    # Cálculo das métricas
    # -------------------------
    summary = (
        df.groupby(col_mndif)[col_obito]
        .agg(['sum', 'count'])
        .rename(columns={'sum': 'obitos', 'count': 'total'})
    )

    summary['taxa_obito'] = summary['obitos'] / summary['total']

    # -------------------------
    # Teste estatístico (Qui-quadrado)
    # -------------------------
    contingency = pd.crosstab(df[col_mndif], df[col_obito])

    #chi2, p_value, _, _ = chi2_contingency(contingency)

    #summary['p_value'] = p_value
    #print(p_value)

    # -------------------------
    # Plot
    # -------------------------
    os.makedirs(output_path, exist_ok=True)

    plt.figure(figsize=(8, 5))

    labels = ['Mesmo município', 'Município diferente']
    taxas = summary['taxa_obito'].values

    plt.bar(labels, taxas)

    plt.title('Taxa de óbito por origem do paciente (PA_MNDIF)')
    plt.ylabel('Taxa de óbito')
    plt.xlabel('Grupo')

    # Mostrar valores
    for i, v in enumerate(taxas):
        plt.text(i, v, f"{v:.2%}", ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'mndif_vs_obito.png'))
    plt.close()

    return None



def plot_complexity_by_mndif(
    df: pd.DataFrame,
    output_path: str,
    col_mndif: str = "PA_MNDIF",
    col_nivcpl: str = "PA_NIVCPL",
    figsize: tuple = (10, 6)
) -> None:
    """
    Gera um gráfico de barras agrupadas onde:
    
    - eixo X = PA_MNDIF (0 e 1)
    - barras = percentual de cada PA_NIVCPL dentro de cada PA_MNDIF
    """

    # Filtra apenas PA_MNDIF = 0 ou 1
    plot_df = df[
        df[col_mndif].isin([0, 1, "0", "1"])
    ][[col_mndif, col_nivcpl]].dropna().copy()

    # Padroniza para inteiro
    plot_df[col_mndif] = plot_df[col_mndif].astype(int)

    # Contagem
    grouped = (
        plot_df
        .groupby([col_mndif, col_nivcpl])
        .size()
        .reset_index(name="count")
    )

    # Percentual dentro de cada PA_MNDIF
    grouped["percent"] = (
        grouped.groupby(col_mndif)["count"]
        .transform(lambda x: 100 * x / x.sum())
    )

    # Pivot:
    # index = PA_MNDIF (eixo x)
    # columns = PA_NIVCPL (uma barra para cada valor)
    pivot_df = grouped.pivot(
        index=col_mndif,
        columns=col_nivcpl,
        values="percent"
    ).fillna(0)

    # Ordena
    pivot_df = pivot_df.sort_index()

    # Plot
    ax = pivot_df.plot(
        kind="bar",
        figsize=figsize
    )

    # Adiciona labels nas barras
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.1f%%",
            padding=3,
            fontsize=9
        )


    plt.title(
        "Distribuição Percentual do Nível de Complexidade por PA_MNDIF",
        fontsize=14
    )

    plt.xlabel("PA_MNDIF")
    plt.ylabel("Percentual (%)")

    plt.legend(
        title="PA_NIVCPL",
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )

    plt.xticks(rotation=0)

    plt.tight_layout()

    # Cria diretório
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Salva imagem
    plt.savefig(output_path, dpi=300)
    plt.close()


REPLACE_DICT_TPUPS = {
    "43": "Farmácia",
    "36": "Clínica",
    "04": "Policlinica",
    "05": "Hospital Geral",
    "07": "Hospital Especializado",
    "39": "SADT",
    "62": "Hospital Dia"
}

def plot_percentual_mndif_por_tpups(
    df: pd.DataFrame,
    output_path: str,
    col_tpups: str = "PA_TPUPS",
    col_mndif: str = "PA_MNDIF"
) -> pd.DataFrame:
    """
    Calcula, para cada tipo de estabelecimento (PA_TPUPS),
    o percentual de registros onde PA_MNDIF = 1.

    Gera um gráfico de barras ordenado do maior percentual
    para o menor e salva a imagem no caminho informado.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    output_path : str
        Caminho completo onde a imagem será salva.
    col_tpups : str
        Coluna do tipo de estabelecimento.
    col_mndif : str
        Coluna binária PA_MNDIF.

    Returns
    -------
    pd.DataFrame
        DataFrame com os percentuais calculados.
    """
    
    df = df[df["PA_DOCORIG"] != 'C']

    #transformar para inteiro
    df[col_mndif] = df[col_mndif].astype(int)
    # Filtra apenas valores 0 e 1

    df_filtrado = df[df[col_mndif].isin([0, 1])].copy()

    # Remove nulos importantes
    df_filtrado = df_filtrado.dropna(
        subset=[col_tpups, col_mndif]
    )

    #Substitui códigos por nomes e remove registros sem correspondência
    df_filtrado[col_tpups] = df_filtrado[col_tpups].map(REPLACE_DICT_TPUPS).fillna("drop")
    df_filtrado = df_filtrado[df_filtrado[col_tpups] != "drop"]

    # Calcula percentual de PA_MNDIF = 1
    resultado = (
        df_filtrado
        .groupby(col_tpups)[col_mndif]
        .mean()
        .mul(100)
        .reset_index(name="percentual_mndif_1")
        .sort_values(
            by="percentual_mndif_1",
            ascending=False
        )
    )

    # Cria diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Plot
    plt.figure(figsize=(14, 7))

    bars = plt.bar(
        resultado[col_tpups].astype(str),
        resultado["percentual_mndif_1"]
    )

    # Labels acima das barras
    for bar in bars:
        altura = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            altura + 0.5,
            f"{altura:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.title(
        "Percentual de PA_MNDIF = 1 por Tipo de Estabelecimento"
    )
    plt.xlabel("Tipo de Estabelecimento (PA_TPUPS)")
    plt.ylabel("Percentual (%)")

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Salva imagem
    plt.savefig(output_path, dpi=300)
    plt.close()

    return None


MUNICIPIOS_MAP = {
    "355030": "São Paulo",
    "355220": "Sorocaba",
    "354340": "Ribeirão Preto",
    "354980": "São José do Rio Preto",
    "350750": "Botucatu",
    "355410": "Taubaté",
    "355710": "Votuporanga",
    "350550": "Barretos",
    "354140": "Presidente Prudente",
    "350760": "Bragança Paulista",
    "350950": "Campinas",
    "354780": "Santo André",
    "354850": "Santos",
    "354870": "São Bernardo do Campo",
    "351500": "Embu das Artes",
    "353440": "Osasco",
    "351880": "Guarulhos",
    "351380": "Diadema",
    "352940": "Mauá",
    "351060": "Carapicuíba",
    "355280": "Taboão da Serra",
    "355100": "São Vicente"
    }

def plot_top_municipios_mndif_origem(
    df: pd.DataFrame,
    output_path: str,
    col_mndif: str = "PA_MNDIF",
    col_municipio: str = "PA_MUNPCN",
    top_n: int = 10,
):
    """
    Gera um gráfico de barras com os municípios que mais recebem
    pacientes residentes de outros municípios.

    Regras:
    - Filtra apenas PA_MNDIF == 1
    - Conta os municípios da coluna PA_MUNPCN
    - Seleciona os top N municípios mais frequentes
    - Ordena do maior para o menor
    - Salva o gráfico no caminho informado

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    output_path : str
        Caminho completo da imagem de saída.
    col_mndif : str
        Coluna indicador de município diferente.
    col_municipio : str
        Coluna do município de processamento.
    top_n : int
        Quantidade de municípios a exibir.
    """

    # Filtra apenas pacientes de outros municípios
    df_filtrado = df[df[col_mndif] == "1"].copy()

    # Conta frequência dos municípios
    top_municipios = (
        df_filtrado[col_municipio]
        .value_counts()
        .head(top_n)
        .sort_values(ascending=False)
    )

    # Substitui códigos por nomes (apenas para os top municípios)
    top_municipios.index = top_municipios.index.map(MUNICIPIOS_MAP).fillna("city not found")

    # Cria figura
    plt.figure(figsize=(12, 6))

    bars = plt.bar(
        top_municipios.index.astype(str),
        top_municipios.values,
    )

    # Adiciona valores acima das barras
    for bar in bars:
        altura = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            altura,
            f"{int(altura):,}".replace(",", "."),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Configurações visuais
    plt.title(
        f"Top {top_n} municípios que mais exportam pacientes para outros municípios"
    )
    plt.xlabel("Município (PA_MUNPCN)")
    plt.ylabel("Quantidade de atendimentos")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Cria pasta caso não exista
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva imagem
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Fecha figura
    plt.close()

    print(f"Gráfico salvo em: {output_path}")



def plot_top_municipios_mndif_destino(
    df: pd.DataFrame,
    output_path: str,
    col_mndif: str = "PA_MNDIF",
    col_municipio: str = "PA_UFMUN",
    top_n: int = 10,
):
    """
    Gera um gráfico de barras com os municípios que mais recebem
    pacientes residentes de outros municípios.

    Regras:
    - Filtra apenas PA_MNDIF == 1
    - Conta os municípios da coluna PA_UFMUN
    - Seleciona os top N municípios mais frequentes
    - Ordena do maior para o menor
    - Salva o gráfico no caminho informado

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    output_path : str
        Caminho completo da imagem de saída.
    col_mndif : str
        Coluna indicador de município diferente.
    col_municipio : str
        Coluna do município de processamento.
    top_n : int
        Quantidade de municípios a exibir.
    """

    # Filtra apenas pacientes de outros municípios
    df_filtrado = df[df[col_mndif] == "1"].copy()

    # Conta frequência dos municípios
    top_municipios = (
        df_filtrado[col_municipio]
        .value_counts()
        .head(top_n)
        .sort_values(ascending=False)
    )

    # Substitui códigos por nomes (apenas para os top municípios)
    top_municipios.index = top_municipios.index.map(MUNICIPIOS_MAP).fillna("city not found")

    # Cria figura
    plt.figure(figsize=(12, 6))

    bars = plt.bar(
        top_municipios.index.astype(str),
        top_municipios.values,
    )

    # Adiciona valores acima das barras
    for bar in bars:
        altura = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            altura,
            f"{int(altura):,}".replace(",", "."),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Configurações visuais
    plt.title(
        f"Top {top_n} municípios que mais recebem pacientes de outros municípios"
    )
    plt.xlabel("Município (PA_UFMUN)")
    plt.ylabel("Quantidade de atendimentos")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Cria pasta caso não exista
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva imagem
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Fecha figura
    plt.close()

    print(f"Gráfico salvo em: {output_path}")



def plot_top_municipios_obits(
    df: pd.DataFrame,
    output_path: str,
    col_obits: str = "PA_OBITO",
    col_municipio: str = "PA_UFMUN",
    top_n: int = 10,
):
    """
    Gera um gráfico de barras com os municípios que mais recebem
    pacientes residentes de outros municípios.

    Regras:
    - Filtra apenas PA_OBITO == 1
    - Conta os municípios da coluna PA_OBITO
    - Seleciona os top N municípios mais frequentes
    - Ordena do maior para o menor
    - Salva o gráfico no caminho informado
    """

    df = df[df["PA_DOCORIG"] != 'C']

    # Filtra apenas pacientes de outros municípios
    df_filtrado = df[df[col_obits] == 1].copy()

    top_municipios = (
    df_filtrado[col_municipio]
    .value_counts(normalize=True)  # transforma em proporção
    .mul(100)                      # converte para percentual
    .head(top_n)
    .sort_values(ascending=False)
    )

    # Substitui códigos por nomes (apenas para os top municípios)
    top_municipios.index = top_municipios.index.map(MUNICIPIOS_MAP).fillna("city not found")

    # Cria figura
    plt.figure(figsize=(12, 6))

    bars = plt.bar(
        top_municipios.index.astype(str),
        top_municipios.values,
    )

    # Adiciona valores acima das barras
    for bar in bars:
        altura = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            altura,
            f"{altura:.2f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Configurações visuais
    plt.title(
        f"Distribuição de mortes entre municípios (PA_OBITO = 1)"
    )
    plt.xlabel("Município (PA_UFMUN)")
    plt.ylabel("Percentual de mortes")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Cria pasta caso não exista
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva imagem
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Fecha figura
    plt.close()

    print(f"Gráfico salvo em: {output_path}")


def plot_valor_aprovado_por_municipio(
    df: pd.DataFrame,
    output_path: str,
    col_municipio: str = "PA_UFMUN",
    col_valor: str = "PA_VALAPR",
):
    """
    Gera um gráfico de linha com os municípios que possuem
    maior valor total aprovado (PA_VALAPR).

    Regras:
    - Agrupa por município (PA_UFMUN)
    - Soma o valor aprovado (PA_VALAPR)
    - Seleciona os top N municípios
    - Ordena do maior para o menor
    - Exibe os valores acima de cada ponto
    - Salva o gráfico no caminho informado
    """

    # Filtrando apenas municípios presentes em outras visualizações
    df[col_municipio] = df[col_municipio].map(MUNICIPIOS_MAP).fillna("outros municípios")
    df = df[df[col_municipio] != "outros municípios"]

    # Agrupa e soma valores
    top_municipios = (
        df.groupby(col_municipio)[col_valor]
        .sum()
        .sort_values(ascending=False)
    )

    # Converte para milhões para melhor visualização
    top_municipios =top_municipios/1000000

    # Cria figura
    plt.figure(figsize=(14, 6))

    # Plota gráfico de linha
    plt.plot(
        top_municipios.index.astype(str),
        top_municipios.values,
        marker="o",
    )

    # Adiciona valores acima dos pontos
    #for x, y in zip(
    #    top_municipios.index.astype(str),
    #    top_municipios.values
    #):
        #plt.text(
        #    x,
        #    y,
        #    f"R$ {y:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        #    ha="center",
        #    va="bottom",
        #    fontsize=9,
        #)

    # Configurações visuais
    plt.title(
        f"Municípios por valor aprovado"
    )
    plt.xlabel("Município (PA_UFMUN)")
    plt.ylabel("Valor aprovado (R$) em milhões")
    plt.xticks(rotation=70)
    plt.tight_layout()

    # Cria pasta caso não exista
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva imagem
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Fecha figura
    plt.close()

    print(f"Gráfico salvo em: {output_path}")