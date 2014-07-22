 
import csv
from pandas import DataFrame

DATA_TYPE_TYPES = {
    "float64": float,
    "int64":  int,
    "object" : object,
}


def get_data_frame(read_csv):
    pd = DataFrame()
    pd = pd.from_csv(read_csv, infer_datetime_format=True,index_col=None)
    return pd



def rename_column(df, position, new_name):
    pass


def change_column_type(df, column_id, new_type):
    previous_column_name = df.dtypes.keys()[column_id]

    df[[previous_column_name,]]= df[[previous_column_name,]].astype(DATA_TYPE_TYPES[new_type])

    print df.dtypes