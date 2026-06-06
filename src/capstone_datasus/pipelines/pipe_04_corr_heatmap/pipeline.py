from kedro.pipeline import Node, Pipeline
from capstone_datasus.module.constants import bases
from .nodes import correlation_heatmap

nodes = []
def create_pipeline(**kwargs) -> Pipeline:

    for base in bases:
        nodes.append(
            Node(
                func=correlation_heatmap,
                inputs = dict(
                    df = f"sampled_{base}",
                    columns_to_include = "params:Columns_corr_heatmap",
                    output_path = f"params:{base}_corr_heatmap_path"
                    ),
                outputs=None,
                name=f"{base}_correlation_heatmap"
            )
        )

    return Pipeline(nodes)