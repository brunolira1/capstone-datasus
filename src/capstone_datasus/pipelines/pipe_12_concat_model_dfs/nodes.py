
import pandas as pd
import numpy as np

def transform_df_model(df: pd.DataFrame) -> pd.DataFrame:
    
    # tirando os dados do tipo Consolidado, pois não são dados individuais
    df = df[df["PA_DOCORIG"] != 'C']
    
    # retirando dados do CID Z525 por conta de alta probabilidade de vazamento de informação de óbitos
    df = df[df["PA_CIDPRI"] != "Z525"]

    # Converter colunas para tipos adequados
    df["PA_IDADE"] = pd.to_numeric(df["PA_IDADE"], errors="coerce")
    df["PA_NIVCPL"] = pd.to_numeric(df["PA_NIVCPL"], errors="coerce")

    # Coluna glosa
    df["PA_GLOSA"] = np.where(df["PA_VALAPR"] >= df["PA_VALPRO"], 0, 1)

    #flag de treino
    df["is_train"] = np.where(df["PA_MVM"] == "201901", 0, 1)

    df = df.drop(columns=["PA_MVM"])

    return df