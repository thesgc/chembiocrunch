 
import csv
from pandas import DataFrame, ExcelFile, Series
import re
import numpy as np
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

def get_excel_data_frame(read_excel, skiprows=0, header=None):
    data = ExcelFile(read_excel)
    df = data.parse(data.sheet_names[0], header=header,index_col=None, skiprows=skiprows, )
    return df


def rename_column(df, position, new_name):
    pass


def change_column_type(df, column_id, new_type):
    '''Changes the data type of a column in a dataframe by casting all members'''
    previous_column_name = df.dtypes.keys()[column_id]

    df[[previous_column_name,]]= df[[previous_column_name,]].astype(DATA_TYPE_TYPES[new_type])
    return df


def get_ic50_data_columns(series):
    full_ref = (series[0].split(':')[1]).strip()
    match = re.match(r"([a-z]+)([0-9]+)", full_ref, re.I)
    if match:
        items = match.groups()
        return Series(np.array([ series[0],full_ref, series[1]] + list(items)), index=[ 'fullname', 'full_ref', 'figure', 'well_letter', 'well_number'])
    return None

#['fullname', 'figure', 'full_ref', 'well_letter', 'well_number']



def get_ic50_config_columns(series):
    series["fullname"] = "%s: %s" % (series["Destination Plate Name"], series["Destination Well"])
    return series



def change_all_columns(df, steps_json):
    '''Using the form from the data mappings view we change the data type of all of the fields'''
    for form in steps_json:
        if "dtype" in form["changed_data"]:
            df = change_column_type(df, form["cleaned_data"]["column_id"] ,form["cleaned_data"]["dtype"])
        if "name" in form["changed_data"]:
            previous_column_name = df.dtypes.keys()[form["cleaned_data"]["column_id"]]
            df = df.rename(columns={previous_column_name : form["cleaned_data"]["name"]})
    return df


def get_plate_wells_with_sample_ids(series):
    if str(series["Sample ID"]).startswith("BVD"):
        return (series["Destination Well"], True)
    return (series["Destination Well"], False)
