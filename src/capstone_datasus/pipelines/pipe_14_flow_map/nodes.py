import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
import geopandas as gpd

from matplotlib.patches import FancyArrowPatch

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

def create_city_flow_table(
    df: pd.DataFrame,
    df_coords: pd.DataFrame,
) -> pd.DataFrame:
    """
    Cria uma tabela de fluxos entre municípios.

    Parameters
    ----------
    df : pd.DataFrame
        Base do DATASUS contendo as colunas PA_UFMUN e PA_MUNPCN.

    df_coords : pd.DataFrame
        DataFrame contendo:
            - cidade
            - latitude
            - longitude

    Returns
    -------
    pd.DataFrame
        Tabela contendo:

        PA_MUNPCN
        PA_UFMUN
        quantidade
        latitude_origem
        longitude_origem
        latitude_destino
        longitude_destino
    """
    #Removendo registros do tipo Consolidado pois não são dados individuais
    df = df[df["PA_DOCORIG"] != "C"]

    # Garantir que os códigos tenham 6 dígitos
    df["PA_UFMUN"] = (
        df["PA_UFMUN"]
        .astype(str)
        .str[:6]
    )

    df["PA_MUNPCN"] = (
        df["PA_MUNPCN"]
        .astype(str)
        .str[:6]
    )

    # Substituir códigos pelos nomes
    df["PA_UFMUN"] = df["PA_UFMUN"].map(MUNICIPIOS_MAP)
    df["PA_MUNPCN"] = df["PA_MUNPCN"].map(MUNICIPIOS_MAP)

    # Remover cidades não presentes no dicionário
    df = df.dropna(subset=["PA_UFMUN", "PA_MUNPCN"])

    # Remover origem = destino
    df = df[df["PA_UFMUN"] != df["PA_MUNPCN"]]

    # Contagem dos fluxos
    df_fluxo = (
        df.groupby(
            ["PA_MUNPCN", "PA_UFMUN"],
            as_index=False
        )
        .size()
        .rename(columns={"size": "quantidade"})
    )

    # Filtrando apenas municípios de São Paulo
    df_coords = df_coords[(df_coords["ddd"] >= 11) & (df_coords["ddd"] <= 19)]

    #Mantendo colunas necessárias do df_coords
    columns_to_keep = ["nome", "latitude", "longitude"]
    df_coords = df_coords[columns_to_keep]

    # Merge das coordenadas da origem
    origem = df_coords.rename(
        columns={
            "nome": "PA_MUNPCN",
            "latitude": "latitude_origem",
            "longitude": "longitude_origem",
        }
    )

    df_fluxo = df_fluxo.merge(
        origem,
        on="PA_MUNPCN",
        how="left",
    )

    # Merge das coordenadas do destino
    destino = df_coords.rename(
        columns={
            "nome": "PA_UFMUN",
            "latitude": "latitude_destino",
            "longitude": "longitude_destino",
        }
    )

    df_fluxo = df_fluxo.merge(
        destino,
        on="PA_UFMUN",
        how="left",
    )

    df_fluxo = df_fluxo.rename(columns={"PA_MUNPCN": "municipio_origem", "PA_UFMUN": "municipio_destino"})

    return df_fluxo


def plot_patient_flow(
    df_fluxo,
    shp_path: str,
    output_path: str,
    figsize=(12, 12),
    min_quantidade=0,
):
    
    #Ler o arquivo diretamente da pasta
    gdf_sp = gpd.read_file(shp_path)

    """
    Plota o fluxo de pacientes entre municípios do Estado de São Paulo.

    Parameters
    ----------
    df_fluxo : pd.DataFrame

    gdf_sp : geopandas.GeoDataFrame
        GeoDataFrame contendo os municípios do estado de São Paulo.

    output_path : str
        Caminho onde a imagem será salva.

    figsize : tuple, default=(12, 12)

    min_quantidade : int, default=0
        Fluxos com quantidade inferior a este valor são ignorados.
    """

    fluxo = df_fluxo.copy()

    fluxo = fluxo[fluxo["quantidade"] >= min_quantidade]

    fig, ax = plt.subplots(figsize=figsize)

    ####################################################################
    # Mapa
    ####################################################################

    gdf_sp.plot(
        ax=ax,
        color="#F4F4F4",
        edgecolor="gray",
        linewidth=0.3,
    )

    ####################################################################
    # Escala de cores
    ####################################################################

    cmap = plt.cm.YlOrRd

    norm = mpl.colors.Normalize(
        vmin=fluxo["quantidade"].min(),
        vmax=fluxo["quantidade"].max(),
    )

    ####################################################################
    # Escala de espessura
    ####################################################################

    q_min = fluxo["quantidade"].min()
    q_max = fluxo["quantidade"].max()

    for _, row in fluxo.iterrows():

        if q_max == q_min:
            lw = 2.5
        else:
            lw = 0.8 + 5 * (
                (row["quantidade"] - q_min)
                / (q_max - q_min)
            )

        cor = cmap(norm(row["quantidade"]))

        seta = FancyArrowPatch(
            (row["longitude_origem"], row["latitude_origem"]),
            (row["longitude_destino"], row["latitude_destino"]),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=lw,
            color=cor,
            alpha=0.75,
            connectionstyle="arc3,rad=0.12",
        )

        ax.add_patch(seta)

    ####################################################################
    # Barra de cores
    ####################################################################

    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=norm,
    )

    sm.set_array([])

    cbar = plt.colorbar(
        sm,
        ax=ax,
        shrink=0.75,
    )

    cbar.set_label("Número de pacientes")

    ####################################################################

    ax.set_title(
        "Fluxo de pacientes entre municípios do Estado de São Paulo",
        fontsize=16,
    )

    ax.set_axis_off()

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)