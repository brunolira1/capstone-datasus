from kedro.io import AbstractDataset
from dbfread import DBF
import pandas as pd

class DBFDataset(AbstractDataset):
    def __init__(self, filepath):
        self._filepath = filepath

    def _load(self):
        table = DBF(self._filepath, load=True)
        return pd.DataFrame(iter(table))

    def _save(self, data):
        raise NotImplementedError("Save não implementado")

    def _describe(self):
        return {"filepath": self._filepath}