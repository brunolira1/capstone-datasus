from kedro.pipeline import Node, Pipeline

from .nodes import plot_mean_median_per_age, plot_boxplot_per_age


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=plot_mean_median_per_age,
            inputs=["PASP_df", "params:mean_median_per_age_output_path"],
            outputs=None,
            name="plot_mean_median_per_age",
        )
    ]
    
    nodes.append(
        Node(
            func=plot_boxplot_per_age,
            inputs=["PASP_df", "params:boxplot_per_age_output_path"],
            outputs=None,
            name="plot_boxplot_per_age",
        )
    )

    return Pipeline(nodes)