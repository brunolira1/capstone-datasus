from kedro.pipeline import Node, Pipeline

from .nodes import analyze_obit_vs_glosa, plot_obit_rate_monthly_stratified, plot_obits_rate_per_month


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        Node(
            func=plot_obits_rate_per_month,
            inputs=["PASP_df", "params:obits_rate_per_month_output_path"],
            outputs=None,
            name="analyze_obits_rate_per_month"

        )
    ]


    nodes.append(
        Node(
            func=plot_obit_rate_monthly_stratified,
            inputs=dict(
                df="PASP_df",
                output_dir="params:stratified.obit_rate_monthly_stratified.output_dir",
                col_mes="params:stratified.obit_rate_monthly_stratified.col_mes",
                col_obito="params:stratified.obit_rate_monthly_stratified.col_obito",
                strat_cols="params:stratified.obit_rate_monthly_stratified.strat_cols",
                min_samples="params:stratified.obit_rate_monthly_stratified.min_samples"
            ),
            outputs=None,
            name="analyze_obits_rate_monthly_stratified"
        )
    )

    nodes.append(
        Node(
            func=analyze_obit_vs_glosa, #para testar se a taxa de glosa influenciou nas mrotes em mês específico
            inputs=dict(
                df="PASP_df",
                output_dir="params:obit_vs_glosa_output_dir",
                estab_value="params:obit_vs_glosa_col_estab"
            ),
            outputs=None,
            name="comparison_obits_vs_glosa"
        )
    )

    return Pipeline(nodes)

