from kedro.pipeline import Node, Pipeline
from .nodes import model_fit, plot_feature_importance_percent, plot_model_metrics, predicted_examples

nodes = []
def create_pipeline(**kwargs) -> Pipeline:
    nodes.append(
        Node(
            func=model_fit,
            inputs=["PASP_df_model_transformed", "params:model_params"],
            outputs=["pasp_model", "pasp_test_df", "pasp_df_feat_imp", "pasp_dict_performance"],
            name="model_fit_node",
        )
    )

    nodes.append(
        Node(
            func=plot_model_metrics,
            inputs=["PASP_df_model_transformed", 
                    "pasp_test_df",
                    "params:precision_recall_output_path",
                    "params:confusion_matrix_output_path", 
                    "params:roc_output_path"
                    ],
            outputs=None,
            name="plot_model_metrics_node",
            tags = ["evaluation"]
        )
    )

    nodes.append(
        Node(
            func=plot_feature_importance_percent,
            inputs=["pasp_df_feat_imp", "params:feature_importance_output_path"],
            outputs=None,
            name="plot_feature_importance_node",
            tags = ["evaluation"]
        )
    )

    nodes.append(
        Node(
            func=predicted_examples,
            inputs=["pasp_test_df"],
            outputs=["predicted_top_examples", "predicted_bottom_examples"],
            name="predicted_examples_node",
        )
    )

    return Pipeline(nodes)
