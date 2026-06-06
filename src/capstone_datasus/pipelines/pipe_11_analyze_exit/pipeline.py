from kedro.pipeline import Node, Pipeline
from .nodes import plot_percentual_altas_tempo, plot_percentual_permanencias_tempo, plot_razao_altas_permanencias

nodes = []
def create_pipeline(**kwargs) -> Pipeline:

    nodes.append(
            Node(
                func=plot_percentual_altas_tempo,
                inputs=dict(
                df="PASP_df",
                output_path="params:plot_percentual_altas_tempo_output_path",
            ),
                outputs=None,
                name="plot_percentual_altas_tempo"
            )
        )

    nodes.append(
            Node(
                func=plot_percentual_permanencias_tempo,
                inputs=dict(
                df="PASP_df",
                output_path="params:plot_percentual_permanencias_tempo_output_path",
            ),
                outputs=None,
                name="plot_percentual_permanencias_tempo"
            )
        )
    
    nodes.append(
            Node(
                func=plot_razao_altas_permanencias,
                inputs=dict(
                df="PASP_df",
                output_path="params:plot_razao_altas_permanencias_output_path",
            ),
                outputs=None,
                name="plot_razao_altas_permanencias"
            )
        )
    return Pipeline(nodes)