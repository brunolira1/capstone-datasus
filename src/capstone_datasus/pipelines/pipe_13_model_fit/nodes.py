import pandas as pd
import lightgbm as lgb
import matplotlib.pyplot as plt
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    precision_recall_curve,
    roc_curve,
    roc_auc_score,
)


def model_fit(
    df: pd.DataFrame,
    model_params: dict,
    target_col: str = "PA_OBITO",
    train_flag_col: str = "is_train",
):

    """
    Treina um LightGBM e gera probabilidades para o conjunto de teste.
    """

    for col in df.columns:
        if df[col].dtype == "object" or df[col].dtype == "str":
            df[col] = df[col].astype("category")

    # Separação treino/teste
    train_df = df[df[train_flag_col] == 1].copy()
    test_df = df[df[train_flag_col] == 0].copy()

    # Features
    feature_cols = [
        col
        for col in df.columns
        if col not in [target_col, train_flag_col]
    ]


    X_train = train_df[feature_cols]
    y_train = train_df[target_col]

    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    # Modelo
    model = lgb.LGBMClassifier(**model_params)

    model.fit(
        X_train,
        y_train,
    )

    # Probabilidade da classe positiva
    test_df["pred_proba"] = model.predict_proba(X_test)[:, 1]

    # Métrica
    auc = roc_auc_score(y_test, test_df["pred_proba"])
    gini = 2 * auc - 1

    print(f"AUC Teste: {auc:.4f}")
    print(f"Gini Teste: {gini:.4f}")

    df_feat_imp = pd.DataFrame(
            {
                "feature": feature_cols,
                "importance": model.feature_importances_,
            }
        ).sort_values("importance", ascending=False)

    dict_performance = {
        "auc": auc,
        "gini": gini,
    }

    return model, test_df, df_feat_imp, dict_performance



def plot_model_metrics(
    y_true: pd.DataFrame,
    y_pred_proba: pd.DataFrame,
    precision_recall_output_path=None,
    confusion_matrix_output_path=None,
    roc_output_path=None,
):

    """
    Plota:
    - Curva Precision-Recall
    - Matriz de confusão
    - Curva ROC

    Parameters
    ----------
    y_true : array-like
        Valores reais.
    y_pred : array-like
        Classes previstas (0 ou 1).
    y_pred_proba : array-like
        Probabilidade prevista da classe positiva.
    """

    y_test = y_true[y_true["is_train"] == 0 ]

    precision, recall, thresholds = precision_recall_curve(
    y_test["PA_OBITO"],
    y_pred_proba["pred_proba"]
    )
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision)

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.grid(True)

    if precision_recall_output_path:
        plt.savefig(precision_recall_output_path, dpi=300)

    plt.show()

    # ======================
    # MATRIZ DE CONFUSÃO
    # ======================
    cm = confusion_matrix(y_test["PA_OBITO"], y_pred_proba["pred_proba"] >= 0.5)

    fig, ax = plt.subplots(figsize=(6, 5))

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Não Óbito", "Óbito"],
    )

    disp.plot(
    ax=ax,
    cmap="Blues",
    colorbar=False,
    values_format="d"
)

    plt.title("Matriz de Confusão")
    plt.tight_layout()

    if confusion_matrix_output_path:
        plt.savefig(confusion_matrix_output_path, dpi=300)

    plt.show()

    # ======================
    # CURVA ROC
    # ======================
    fpr, tpr, _ = roc_curve(y_test["PA_OBITO"], y_pred_proba["pred_proba"])

    auc = roc_auc_score(y_test["PA_OBITO"], y_pred_proba["pred_proba"])

    pr_auc = average_precision_score(
        y_test["PA_OBITO"],
        y_pred_proba["pred_proba"]
    )
    print(f"PR-AUC = {pr_auc:.4f}")

    plt.figure(figsize=(7, 5))

    plt.plot(
        fpr,
        tpr,
        label=f"ROC AUC = {auc:.4f}",
        linewidth=2,
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        linewidth=1,
    )

    plt.xlabel("Taxa de Falsos Positivos")
    plt.ylabel("Taxa de Verdadeiros Positivos")
    plt.title("Curva ROC")
    plt.legend()
    plt.grid(alpha=0.3)

    if roc_output_path:
        plt.savefig(roc_output_path, dpi=300)

    plt.show()


def plot_feature_importance_percent(
    df: pd.DataFrame,
    output_path: str = None,
):
    """
    Lê um CSV contendo colunas:
        feature, importance

    Calcula a participação percentual de cada importance
    em relação ao total e gera um gráfico de barras.
    """

    # Calcular porcentagem
    total_importance = df["importance"].sum()

    df["importance_pct"] = (
        df["importance"] / total_importance * 100
    )

    # Ordenar do maior para o menor
    df = df.sort_values(
        "importance_pct",
        ascending=False
    )

    # Gráfico
    plt.figure(figsize=(14, 6))

    bars = plt.bar(
        df["feature"],
        df["importance_pct"]
    )

    # Mostrar valor acima de cada barra
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.title("Importância Relativa das Features")
    plt.xlabel("Feature")
    plt.ylabel("Importância (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    plt.show()


def predicted_examples(df: pd.DataFrame, n: int = 50) -> pd.DataFrame:
    """
    Retorna os n exemplos com maior e menor probabilidade prevista de óbito.
    """

    top = df.sort_values("pred_proba", ascending=False).head(n)

    bottom = df.sort_values("pred_proba", ascending=True).head(n)

    return top, bottom