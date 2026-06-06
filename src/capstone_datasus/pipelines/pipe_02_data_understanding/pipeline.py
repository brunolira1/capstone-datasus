from kedro.pipeline import Node, Pipeline

from .nodes import visualize_sampled_data
from capstone_datasus.module.constants import bases

nodes = []
def create_pipeline(**kwargs) -> Pipeline:

    for base in bases:
        nodes.append(
            Node(
                func=visualize_sampled_data,
                inputs=f"sampled_{base}",
                outputs=f"dummy_output02_{base}",
                name=f"{base}_visualize_sampled_data",
            )
        )

    return Pipeline(nodes)