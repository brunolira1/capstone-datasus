from kedro.pipeline import Node, Pipeline

from .nodes import (obits_per_age_barplot, obits_per_complexity_barplot, obits_rate_per_age_barplot, 
                    plot_obit_rate_stratified)


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=obits_per_age_barplot,
            inputs=["PASP_df", "params:obits_per_age_barplot_output_path"],
            outputs=None,
            name="analyze_obits_per_age_barplot",
        )
    ]
    nodes.append(
            Node(
            func=obits_per_complexity_barplot,
            inputs=["PASP_df", "params:obits_per_complexity_barplot_output_path"],
            outputs=None,
            name="analyze_obits_per_complexity_barplot",
        )
    )

    nodes.append(
        Node(
            func=obits_rate_per_age_barplot,
            inputs=["PASP_df", "params:obits_rate_per_age_barplot_output_path"],
            outputs=None,
            name="analyze_obits_rate_per_age_barplot",
            )
    )

    nodes.append(
        Node(
            func=plot_obit_rate_stratified,
            inputs=dict(
                df="PASP_df",
                col_idade="params:stratified.col_idade",
                col_obito="params:stratified.col_obito",
                strat_cols="params:stratified.strat_cols",
                min_samples="params:stratified.min_samples",
                output_dir="params:stratified.obit_rate_stratified_output_dir"
            ),
            outputs=None,
            name="analyze_obit_rate_stratified"
        )
    )


    return Pipeline(nodes)