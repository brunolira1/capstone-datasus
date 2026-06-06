from kedro.pipeline import Node, Pipeline

from .nodes import (analyze_specific_unit_and_tpfin, plot_cost_per_unit_tpups, plot_obits_per_unit_tpups, 
                    plot_glosa_per_unit_tpups)



def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=plot_cost_per_unit_tpups,
            inputs=["PASP_df", "params:cost_per_unit_tpups_output_path"],
            outputs=None,
            name="plot_cost_per_unit_tpups",
        )
    ]

    nodes.append(
        Node(
            func=plot_obits_per_unit_tpups,
            inputs=["PASP_df", "params:obits_per_unit_tpups_output_path"],
            outputs=None,
            name="plot_obits_per_unit_tpups",
        )
    )

    nodes.append(
        Node(
            func=plot_glosa_per_unit_tpups,
            inputs=["PASP_df", "params:glosa_per_unit_tpups_output_path"],
            outputs=None,
            name="plot_glosa_per_unit_tpups"
        )
    )

    nodes.append(
        Node(
            func=analyze_specific_unit_and_tpfin,
            inputs="PASP_df",
            outputs=None,
            name="analyze_specific_unit_and_tpfin"
        )
    )

    return Pipeline(nodes)