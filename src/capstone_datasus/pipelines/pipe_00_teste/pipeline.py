from kedro.pipeline import Node, Pipeline

from .nodes import visualize_data, count_data
from capstone_datasus.module.constants import bases


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=visualize_data,
            inputs=["df_dbf"],
            outputs="dbf_head100",
            name="visualize_data_test",
        )
    ]

    for base in bases:
        nodes.append(
            Node(
                func=count_data,
                inputs=[base],
                outputs=f"dummy_output_{base}",
                name=f"{base}_count_data_test",
            )
        )

    return Pipeline(nodes)