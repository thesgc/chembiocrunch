 
import csv
from pandas import DataFrame


DATA_TYPE_TYPES = {
    "float64": float,
    "int64":  int,
    "object" : object,
}


def get_data_frame(read_csv):
    '''Returns a dataframe from a csv buffer'''
    pd = DataFrame()
    pd = pd.from_csv(read_csv, infer_datetime_format=True,index_col=None)
    return pd



def rename_column(df, position, new_name):
    pass


def change_column_type(df, column_id, new_type):
    '''Changes the data type of a column in a dataframe by casting all members'''
    previous_column_name = df.dtypes.keys()[column_id]

    df[[previous_column_name,]]= df[[previous_column_name,]].astype(DATA_TYPE_TYPES[new_type])
    return df




def change_all_columns(df, steps_json):
    '''Using the form from the data mappings view we change the data type of all of the fields'''
    for form in steps_json:
        if "dtype" in form["changed_data"]:
            df = change_column_type(df, form["cleaned_data"]["column_id"] ,form["cleaned_data"]["dtype"])
        if "name" in form["changed_data"]:
            previous_column_name = df.dtypes.keys()[form["cleaned_data"]["column_id"]]
            df = df.rename(columns={previous_column_name : form["cleaned_data"]["name"]})
    return df


