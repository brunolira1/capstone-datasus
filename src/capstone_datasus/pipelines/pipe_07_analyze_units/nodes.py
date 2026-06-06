import pandas as pd
import matplotlib.pyplot as plt
import os


REPLACE_DICT_TPUPS = {
    "43": "Farmácia",
    "36": "Clínica",
    "04": "Policlinica",
    "05": "Hospital Geral",
    "07": "Hospital Especializado",
    "39": "SADT",
    "62": "Hospital-Dia",
    "70": "CAPS",
    "80": "UPA",
    "67": "Lab Saúde Pública"
}

def plot_cost_per_unit_tpups(
    df: pd.DataFrame,
    output_path: str,
    col_tpups: str = "PA_TPUPS",
    col_val: str = "PA_VALAPR",
    col_qtd: str = "PA_QTDPRO"
) -> None:
    """
    Calcula o custo unitário (VALAPR / QTDPRO) agrupado por tipo de estabelecimento (TPUPS)
    e salva um gráfico no caminho especificado.

    Args:
        df: DataFrame de entrada
        output_path: Caminho onde a imagem será salva
        col_tpups: Coluna de agrupamento
        col_val: Coluna de valor aprovado
        col_qtd: Coluna de quantidade produzida
    """
    # Mantém apenas colunas necessárias
    df = df[[col_tpups, col_val, col_qtd]].copy()

    # Remove linhas inválidas (divisão por zero ou NaN)
    df = df[(df[col_qtd] > 0) & (df[col_val].notna())]

    # Substitui códigos por descrições
    df[col_tpups] = df[col_tpups].map(REPLACE_DICT_TPUPS)

    # Filtra apenas os tipos de estabelecimento desejados (acima de 20 mil registros)
    df = df[df[col_tpups].isin(REPLACE_DICT_TPUPS.values())]

    # Agregação correta
    grouped = (
        df.groupby(col_tpups)
        .agg(
            total_valor=(col_val, "sum"),
            total_qtd=(col_qtd, "sum")
        )
        .reset_index()
    )

    # Cálculo do custo unitário
    grouped["custo_unitario"] = grouped["total_valor"] / grouped["total_qtd"]

    # Ordena para melhorar visualização
    grouped = grouped.sort_values("custo_unitario", ascending=False)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.bar(grouped[col_tpups].astype(str), grouped["custo_unitario"])

    plt.title("Custo Unitário por Tipo de Estabelecimento (TPUPS)")
    plt.xlabel("Tipo de Estabelecimento (TPUPS)")
    plt.ylabel("Custo Unitário (R$)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Garante que o diretório existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Salva imagem
    plt.savefig(output_path)
    plt.close()


def plot_obits_per_unit_tpups(
    df: pd.DataFrame,
    output_path: str,
    col_tpups: str = "PA_TPUPS",
    col_obito: str = "PA_OBITO",
    col_idade: str = "PA_IDADE"
) -> None:
    """
    Calcula a taxa de óbitos (PA_OBITO == 1) por tipo de estabelecimento (TPUPS)
    e salva um gráfico no caminho especificado.

    Args:
        df: DataFrame de entrada
        output_path: Caminho onde a imagem será salva
        col_tpups: Coluna de agrupamento
        col_obito: Coluna de óbito
        col_idade: Coluna de idade
    """
    # Removendo registros do tipo Consolidado pois não são dados individuais
    df = df[df["PA_DOCORIG"] != 'C']

    # Tipos
    df[col_idade] = pd.to_numeric(df[col_idade], errors="coerce")
    df[col_obito] = pd.to_numeric(df[col_obito], errors="coerce")

    # Filtro idade
    df = df[(df[col_idade] >= 1) & (df[col_idade] <= 100)]

    # Mantém apenas colunas necessárias
    df = df[[col_tpups, col_obito]].copy()

    # Substitui códigos por descrições
    df[col_tpups] = df[col_tpups].map(REPLACE_DICT_TPUPS)

    # Filtra apenas os tipos de estabelecimento desejados (acima de 20 mil registros)
    df = df[df[col_tpups].isin(REPLACE_DICT_TPUPS.values())]

    # Agregação correta
    grouped = (
        df.groupby(col_tpups)
        .agg(
            total_obitos=(col_obito, "sum"),
            total_registros=(col_obito, "count")
        )
        .reset_index()
    )

    # Cálculo da taxa de óbitos
    grouped["taxa_obitos"] = grouped["total_obitos"] / grouped["total_registros"]

    # Ordena para melhorar visualização
    grouped = grouped.sort_values("taxa_obitos", ascending=False)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.bar(grouped[col_tpups].astype(str), grouped["taxa_obitos"])

    plt.title("Taxa de Óbitos por Tipo de Estabelecimento (TPUPS)")
    plt.xlabel("Tipo de Estabelecimento (TPUPS)")
    plt.ylabel("Taxa de Óbitos (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Garante que o diretório existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Salva imagem
    plt.savefig(output_path)
    plt.close()


def plot_glosa_per_unit_tpups(
        df: pd.DataFrame, 
        output_path: str,
        col_tpups: str = "PA_TPUPS",
        col_valpro: str = "PA_VALPRO",
        col_valapr: str = "PA_VALAPR"
        ) -> None:
    """
    Calcula a taxa de glosa por tipo de estabelecimento (PA_TPUPS)
    e salva um gráfico no caminho especificado.

    Args:
        df (pd.DataFrame): DataFrame com colunas PA_VALPRO, PA_VALAPR e PA_TPUPS
        output_path (str): Caminho onde a imagem será salva
    """
    breakpoint()
    # Evitar divisão por zero
    df = df[df[col_valpro] > 0].copy()

    # Substitui códigos por descrições
    df[col_tpups] = df[col_tpups].map(REPLACE_DICT_TPUPS)

    # Filtra apenas os tipos de estabelecimento desejados (acima de 20 mil registros)
    df = df[df[col_tpups].isin(REPLACE_DICT_TPUPS.values())]

    # Agrupamento
    agg_df = (
        df.groupby(col_tpups)
        .agg(
            total_produzido=(col_valpro, "sum"),
            total_aprovado=(col_valapr, "sum")
        )
        .reset_index()
    )

    # Cálculo da taxa de glosa
    agg_df["taxa_glosa"] = (
        (agg_df["total_produzido"] - agg_df["total_aprovado"])
        / agg_df["total_produzido"]
    )

    # Ordenar para melhor visualização
    agg_df = agg_df.sort_values("taxa_glosa", ascending=False)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.bar(agg_df[col_tpups].astype(str), agg_df["taxa_glosa"])

    plt.title("Taxa de Glosa por Tipo de Estabelecimento (PA_TPUPS)")
    plt.xlabel("Tipo de Estabelecimento")
    plt.ylabel("Taxa de Glosa")
    plt.xticks(rotation=45)

    # Linha de referência (opcional)
    #plt.axhline(0, linestyle="--")

    plt.tight_layout()

    # Criar pasta se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Salvar
    plt.savefig(output_path)
    plt.close()


def analyze_specific_unit_and_tpfin(
    df: pd.DataFrame,
    #output_path: str,
    col_tpfin: str = "PA_TPFIN",
    col_tpups: str = "PA_TPUPS",
    col_indica: str = "PA_INDICA",
    col_valpro: str = "PA_VALPRO",
    col_valapr: str = "PA_VALAPR",
    col_obits: str = "PA_OBITO"
    ) -> None:

    # Filtra por tipo de financiamento e tipo de estabelecimento
    df_filtered = df[(df[col_tpfin] == "04") & (df[col_tpups] == "07")]

    # Contagem de indicações
    print(df_filtered[col_indica].value_counts())

    agg_df = (
    df_filtered.groupby(col_tpups)
    .agg(
        total_produzido=(col_valpro, "sum"),
        total_aprovado=(col_valapr, "sum")
        )
        .reset_index()
    )

    # Cálculo da taxa de glosa
    agg_df["taxa_glosa"] = (
        (agg_df["total_produzido"] - agg_df["total_aprovado"])
        / agg_df["total_produzido"]
    )

    print(agg_df.sort_values("taxa_glosa"))
    #breakpoint()

    df_filtered_neg = df_filtered[(df_filtered[col_indica] == "0") & (df_filtered[col_valpro] >= 0)]
    df_filtered_pos = df_filtered[(df_filtered[col_indica] == "5") & (df_filtered[col_valpro] >= 0)]

    print("distribuição de óbitos - valores não aprovados:", df_filtered_neg[col_obits].value_counts())
    print("distribuição de óbitos - valores aprovados:", df_filtered_pos[col_obits].value_counts())

    return None
