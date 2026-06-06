from kedro.pipeline import Node, Pipeline

from capstone_datasus.pipelines.pipe_03_concat.nodes import concat_parquets_low_mem
from .nodes import transform_df_model

nodes = []
def create_pipeline(**kwargs) -> Pipeline:
    nodes.append(
        Node(
            func=concat_parquets_low_mem,
            inputs=["params:filepaths_anomes", "params:Columns_model", "params:output_filepath_model_raw"],
            outputs="output_filepath_model_raw",
            name="concat_parquets_model",
        )
    )

    nodes.append(
        Node(
            func=transform_df_model,
            inputs=["PASP_df_model_raw"],
            outputs="PASP_df_model_transformed",
            name="transform_df_model",
        )
    )

    return Pipeline(nodes)