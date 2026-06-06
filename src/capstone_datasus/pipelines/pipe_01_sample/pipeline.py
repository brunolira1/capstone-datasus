from kedro.pipeline import Node, Pipeline

from .nodes import sample_preserve_obits
from capstone_datasus.module.constants import bases

nodes = []
def create_pipeline(**kwargs) -> Pipeline:

    for base in bases:
        nodes.append(
            Node(
                func=sample_preserve_obits,
                inputs=[base, "params:column_preserved"],
                outputs=f"sampled_{base}",
                name=f"{base}_sample_preserve_obits",
            )
        )

    return Pipeline(nodes)