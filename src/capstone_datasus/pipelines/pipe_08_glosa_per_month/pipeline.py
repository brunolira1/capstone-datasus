from kedro.pipeline import Node, Pipeline

from .nodes import impacto_pico_glosa_per_tpups, plot_taxa_glosa_per_month


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=plot_taxa_glosa_per_month,
            inputs=["PASP_df", "params:rate_glosa_per_month_output_path"],
            outputs=None,
            name="plot_taxa_glosa_per_month",
        )
    ]
    nodes.append(
        Node(
            func=impacto_pico_glosa_per_tpups,
            inputs=["PASP_df", "params:impacto_pico_glosa_per_tpups_csv_path"],
            outputs=None,
            name="impacto_pico_glosa_per_tpups"
        )
    )
    return Pipeline(nodes)