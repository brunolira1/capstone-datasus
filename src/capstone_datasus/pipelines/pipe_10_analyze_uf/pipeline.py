from kedro.pipeline import Node, Pipeline

from .nodes import (
    analyze_mndif_vs_death, plot_complexity_by_mndif, 
    plot_percentual_mndif_por_tpups, plot_top_municipios_mndif_destino, plot_top_municipios_mndif_origem, 
    plot_top_municipios_obits, plot_valor_aprovado_por_municipio
)


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=analyze_mndif_vs_death,
            inputs=["PASP_df", "params:obits_rate_per_mndif_output_path"],
            outputs=None,
            name="analyze_mndif_vs_death"

        )
    ]

    nodes.append(
        Node(
            func=plot_complexity_by_mndif,
            inputs=dict(
                df="PASP_df",
                output_path="params:complexity_by_mndif_output_path",
            ),
            outputs=None,
            name="plot_complexity_by_mndif"
        )
    )

    nodes.append(
        Node(
            func=plot_percentual_mndif_por_tpups,
                inputs=dict(
                df="PASP_df",
                output_path="params:percentual_mndif_por_tpups_output_path",
            ),
            outputs=None,
            name="plot_percentual_mndif_por_tpups"
        )
    )

    nodes.append(
        Node(
            func=plot_top_municipios_mndif_origem,
                inputs=dict(
                df="PASP_df",
                output_path="params:top_municipios_mndif_origem_output_path",
            ),
            outputs=None,
            name="plot_top_municipios_mndif_origem"
        )

    )

    nodes.append(
        Node(
            func=plot_top_municipios_mndif_destino,
                inputs=dict(
                df="PASP_df",
                output_path="params:top_municipios_mndif_destino_output_path",
            ),
            outputs=None,
            name="plot_top_municipios_mndif_destino"
        )

    )

    nodes.append(
        Node(
            func=plot_top_municipios_obits,
                inputs=dict(
                df="PASP_df",
                output_path="params:top_municipios_obits_output_path",
            ),
            outputs=None,
            name="plot_top_municipios_obits"
        )

    )

    nodes.append(
        Node(
            func=plot_valor_aprovado_por_municipio,
                inputs=dict(
                df="PASP_df",
                output_path="params:valor_aprovado_por_municipio_output_path",
            ),
            outputs=None,
            name="plot_valor_aprovado_por_municipio"
        )
    )

    return Pipeline(nodes)
