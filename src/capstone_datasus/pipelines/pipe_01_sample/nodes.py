import pandas as pd
import polars as pl

def sample_preserve_obits(df, col, frac=0.1, random_state=42):
    
    df[col] = df[col].astype(int)
    print(df[col].value_counts(dropna=False))
    # Todos os 1s (mantém 100%)
    df_ones = df[df[col] == 1]
    
    # Apenas os 0s
    df_zeros = df[df[col] == 0]
    
    # Quantos 0s precisamos pegar para completar 10% do total?
    n_total_sample = int(len(df) * frac)
    n_zeros_sample = n_total_sample - len(df_ones)
    
    if n_zeros_sample < 0:
        raise ValueError("Quantidade de '1' já é maior que o tamanho da amostra desejada.")
    
    # Amostra dos 0s
    df_zeros_sample = df_zeros.sample(n=n_zeros_sample, random_state=random_state)
    
    # Junta tudo
    df_sample = pd.concat([df_ones, df_zeros_sample])

    return df_sample.sample(frac=1, random_state=random_state)


#def sample_preserve_obits(filepath: str, col: str, frac=0.1, seed=42):
#
#    df = pl.scan_csv(filepath)
#
#    df = df.with_columns(pl.col(col).cast(pl.Int32))
#
#    df_ones = df.filter(pl.col(col) == 1)
#    df_zeros = df.filter(pl.col(col) == 0)
#
#    # Conta sem carregar tudo na memória
#    n_total = df.select(pl.count()).collect().item()
#    n_ones = df_ones.select(pl.count()).collect().item()
#
#    n_total_sample = int(n_total * frac)
#    n_zeros_sample = n_total_sample - n_ones
#
#    if n_zeros_sample < 0:
#        raise ValueError("Quantidade de '1' já é maior que a amostra desejada.")
#
#    df_zeros_sample = df_zeros.sample(n=n_zeros_sample, seed=seed)
#
#    df_sample = pl.concat([df_ones, df_zeros_sample])
#    breakpoint()
#    return df_sample.sample(fraction=1.0, seed=seed).collect()