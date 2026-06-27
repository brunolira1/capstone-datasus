from kedro.pipeline import Node, Pipeline

from .nodes import create_city_flow_table

def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=create_city_flow_table,
            inputs=dict(
                df="PASP_df",
                df_coords="df_municipios",
            ),
            outputs="df_fluxo",
            name="create_city_flow_table",
        )
    ]

    return Pipeline(nodes)