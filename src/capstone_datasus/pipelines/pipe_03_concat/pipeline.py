from kedro.pipeline import Node, Pipeline

from .nodes import concat_parquets_low_mem

def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=concat_parquets_low_mem,
            inputs=["params:filepaths_anomes", "params:Columns_to_concat", "params:output_filepath"],
            outputs="output_filepath",
            name="concat_parquets_low_mem",
        )
    ]

    return Pipeline(nodes)