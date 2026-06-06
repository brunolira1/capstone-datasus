from itertools import count
import logging
import pandas as pd

def visualize_data(df_dbf: pd.DataFrame) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    logger.info("Dataframe has %d rows and %d columns.", df_dbf.shape[0], df_dbf.shape[1])
    return df_dbf.head(100)

def count_data(df_dbf: pd.DataFrame) -> int:
    logger = logging.getLogger(__name__)

    count_total = len(df_dbf)
    logger.info("Dataframe has %d rows.", count_total)

    count_obitos = df_dbf["PA_OBITO"].value_counts()
    print(count_obitos)

    count_alta = df_dbf["PA_ALTA"].value_counts()
    print(count_alta)

    return count_total