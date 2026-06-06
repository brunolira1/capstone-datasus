import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_taxa_glosa_per_month(
        df: pd.DataFrame, 
        output_path: str,
        col_mes: str = "PA_MVM",
        col_valpro: str = "PA_VALPRO",
        col_valapr: str = "PA_VALAPR"
        ) -> None:
    """
    Calcula a taxa de glosa por mês (PA_MVM) e salva um gráfico de linha.

    Args:
        df (pd.DataFrame): DataFrame com colunas PA_VALPRO, PA_VALAPR e PA_MVM
        output_path (str): Caminho onde a imagem será salva
        col_mes (str): Nome da coluna que contém o mês
        col_valpro (str): Nome da coluna que contém o valor produzido
        col_valapr (str): Nome da coluna que contém o valor aprovado
    """

    # Garantir tipo string (caso venha como int tipo 201601)
    df[col_mes] = df[col_mes].astype(str)

    # Filtrar para evitar divisão por zero
    df = df[df[col_valpro] > 0].copy()

    # Agrupamento mensal
    agg_df = (
        df.groupby(col_mes)
        .agg(
            total_produzido=(col_valpro, "sum"),
            total_aprovado=(col_valapr, "sum")
        )
        .reset_index()
    )

    # Taxa de glosa
    agg_df["taxa_glosa"] = (
        (agg_df["total_produzido"] - agg_df["total_aprovado"])
        / agg_df["total_produzido"]
    )
    #breakpoint()
    # Ordenar cronologicamente
    agg_df = agg_df.sort_values(col_mes)

    # Converter para datetime (melhora o gráfico)
    agg_df[col_mes] = pd.to_datetime(agg_df[col_mes], format="%Y%m")

    # Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Linha da taxa de glosa
    ax1.plot(agg_df[col_mes], agg_df["taxa_glosa"], marker="o")
    ax1.set_ylabel("Taxa de Glosa")
    ax1.set_xlabel("Mês")
    ax1.axhline(0, linestyle="--")

    #agg_df["mm_3"] = agg_df["taxa_glosa"].rolling(3).mean()
    #ax1.plot(agg_df[col_mes], agg_df["mm_3"], linestyle=":")

    # Eixo secundário (volume)
    ax2 = ax1.twinx()
    ax2.plot(agg_df[col_mes], agg_df["total_produzido"] / 1e6, linestyle="--", color="orange")
    ax2.set_ylabel("Volume Produzido (milhões)")

    # Título
    plt.title("Taxa de Glosa e Volume Produzido ao Longo do Tempo")

    # Rotação eixo X
    plt.xticks(rotation=45)

    plt.tight_layout()

    # Criar diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Salvar
    plt.savefig(output_path)
    plt.close()



def impacto_pico_glosa_per_tpups(
    df: pd.DataFrame,
    output_path: str,
    col_mes: str = "PA_MVM",
    col_valpro: str = "PA_VALPRO",
    col_valapr: str = "PA_VALAPR",
    col_tpups: str = "PA_TPUPS"
) -> pd.DataFrame:
    """
    Identifica quais tipos de estabelecimento (PA_TPUPS)
    foram responsáveis pelo pico de glosa em um mês específico.

    Salva um CSV com os principais responsáveis.

    Args:
        df (pd.DataFrame): DataFrame com PA_VALPRO, PA_VALAPR, PA_MVM, PA_TPUPS
        output_path (str): Caminho para salvar o resultado
    """

    df = df.copy()
    df[col_mes] = df[col_mes].astype(str)

    # Evitar divisão por zero
    df = df[df[col_valpro] > 0]

    # ---------------------------
    # 1. Encontrar mês do pico
    # ---------------------------
    agg_mes = (
        df.groupby(col_mes)
        .agg(
            total_produzido=(col_valpro, "sum"),
            total_aprovado=(col_valapr, "sum")
        )
        .reset_index()
    )

    agg_mes["taxa_glosa"] = (
        (agg_mes["total_produzido"] - agg_mes["total_aprovado"])
        / agg_mes["total_produzido"]
    )

    mes_pico = agg_mes.loc[agg_mes["taxa_glosa"].idxmax(), col_mes]

    # ---------------------------
    # 2. Glosa por TPUPS no mês do pico
    # ---------------------------
    df_pico = df[df[col_mes] == mes_pico]

    agg_tpups_pico = (
        df_pico.groupby(col_tpups)
        .agg(
            produzido_pico=(col_valpro, "sum"),
            aprovado_pico=(col_valapr, "sum")
        )
        .reset_index()
    )

    agg_tpups_pico["taxa_glosa_pico"] = (
        (agg_tpups_pico["produzido_pico"] - agg_tpups_pico["aprovado_pico"])
        / agg_tpups_pico["produzido_pico"]
    )

    # ---------------------------
    # 3. Glosa média histórica por TPUPS
    # ---------------------------
    agg_tpups_hist = (
        df.groupby(col_tpups)
        .agg(
            produzido_hist=(col_valpro, "sum"),
            aprovado_hist=(col_valapr, "sum")
        )
        .reset_index()
    )

    agg_tpups_hist["taxa_glosa_hist"] = (
        (agg_tpups_hist["produzido_hist"] - agg_tpups_hist["aprovado_hist"])
        / agg_tpups_hist["produzido_hist"]
    )

    # ---------------------------
    # 4. Juntar e calcular impacto
    # ---------------------------
    result = agg_tpups_pico.merge(
        agg_tpups_hist[[col_tpups, "taxa_glosa_hist"]],
        on=col_tpups,
        how="left"
    )

    # Desvio em relação ao normal
    result["delta_glosa"] = (
        result["taxa_glosa_pico"] - result["taxa_glosa_hist"]
    )

    # Peso no mês (impacto real)
    total_mes = result["produzido_pico"].sum()
    result["peso_mes"] = result["produzido_pico"] / total_mes

    # Contribuição para o pico
    result["impacto"] = result["delta_glosa"] * result["peso_mes"]

    # Ordenar pelos maiores responsáveis
    result = result.sort_values("impacto", ascending=False)

    # ---------------------------
    # 5. Salvar resultado
    # ---------------------------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.to_csv(output_path, index=False)

    print(f"Mês de pico identificado: {mes_pico}")

    return result