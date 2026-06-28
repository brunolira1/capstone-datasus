from kedro.pipeline import Node, Pipeline

from .nodes import create_city_flow_table, plot_patient_flow

nodes = []
def create_pipeline(**kwargs) -> Pipeline:
    nodes.append(
        Node(
            func=create_city_flow_table,
            inputs=dict(
                df="PASP_df",
                df_coords="df_municipios",
            ),
            outputs=["df_fluxo_parquet", "df_fluxo_csv"],
            name="create_city_flow_table",
        )
    )

    nodes.append(
        Node(
            func=plot_patient_flow,
            inputs=dict(
                df_fluxo="df_fluxo_parquet",
                shp_path="params:sp_mapa_path",
                output_path="params:patient_flow_output_path",
            ),
            outputs=None,
            name="plot_patient_flow",
        )
    )

    return Pipeline(nodes)