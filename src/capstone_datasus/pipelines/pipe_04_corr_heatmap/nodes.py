import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

def correlation_heatmap(df: pd.DataFrame, columns_to_include: list, output_path: str):
    #breakpoint()
    df_numeric = df[columns_to_include].apply(pd.to_numeric, errors="coerce")
    df_numeric = df_numeric.dropna(axis=1, how="all")
    df_numeric = df_numeric.fillna(df_numeric.mean())

    scaler = StandardScaler()
    df_scaled = pd.DataFrame(
        scaler.fit_transform(df_numeric),
        columns=df_numeric.columns
    )

    corr = df_scaled.corr()

    plt.figure(figsize=(12, 8))
    ax = sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", annot_kws={"size": 8})

    fig = ax.get_figure()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    return None