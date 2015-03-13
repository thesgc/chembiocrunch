
import csv
from pandas import DataFrame, ExcelFile, Series
from pandas.io.parsers import read_csv as rc
from pandas.io.json import read_json
import re
import numpy as np
DATA_TYPE_TYPES = {
    "float64": float,
    "int64":  int,
    "object" : object,
}
import string
from itertools import product as cwr
stuff  = string.ascii_lowercase
# We generate a hexavigecimal alphabet which allows us to convert between base 26 letter codes and numbers
alphabet = ["".join(comb) for comb in cwr(stuff, repeat=1)]
alphabet += ["".join(comb) for comb in cwr(stuff, repeat=2)]
alphabet += ["".join(comb) for comb in cwr(stuff, repeat=3)]

def get_data_frame(read_csv, skiprows=0, header=None, names=None):
    '''Returns a dataframe from a csv buffer'''  
    pd = rc(read_csv, infer_datetime_format=True,index_col=None, header=header, skiprows=skiprows,names=names,)
    return pd

def get_excel_data_frame(read_excel, skiprows=0, header=None, names=None):
    data = ExcelFile(read_excel)
    df = data.parse(data.sheet_names[0], header=header,index_col=None, skiprows=skiprows,names=names, )
    return df


def rename_column(df, position, new_name):
    pass


def change_column_type(df, column_id, new_type):
    '''Changes the data type of a column in a dataframe by casting all members'''
    previous_column_name = df.dtypes.keys()[column_id]

    df[[previous_column_name,]]= df[[previous_column_name,]].astype(DATA_TYPE_TYPES[new_type])
    return df

def get_row_number(ref):
    return alphabet.index(ref.lower()) +1 




def zero_pad_object_id(id):
    '''used to ensure data files appear in order of ID'''
    return ('%d' % id).zfill(11)


def get_coords_as_numbers(full_ref):
    match = re.match(r"([a-z]+)([0-9]+)", full_ref, re.I)
    if match:
        items = match.groups()
        row_number = get_row_number(items[0])
        return [row_number, int(items[1])]


def cell_range(range_csv):
    list_of_cells = []
    split = [x.strip() for x in range_csv.split(",")]
    for cellrange in split:
        start_and_end = [y.strip() for y in cellrange.split(":")]
        if len(start_and_end) == 1:
            list_of_cells.append(start_and_end[0])
        else:
            list_of_cells += single_cell_range(start_and_end)
    return list_of_cells


def single_cell_range(start_and_end):
    numeric_start_coords = get_coords_as_numbers(start_and_end[0])
    numeric_end_coords = get_coords_as_numbers(start_and_end[1])
    letters = [alphabet[num - 1] for num in range(numeric_start_coords[0],numeric_end_coords[0] +1)]
    numbers = range(numeric_start_coords[1], numeric_end_coords[1] +1)
    all_coords = ["%s%d" % (letter.upper(), number) for letter in letters for number in numbers]
    return all_coords




def get_plate_ref(string):
    '''split out the square backets to give the plate reference'''
    split = str(string).split("[")
    if len(split) == 2:
        return split[1].split("]")[0]
    else:
        return ""




def change_all_columns(df, steps_json):
    '''Using the form from the data mappings view we change the data type of all of the fields'''
    for form in steps_json:
        if "dtype" in form["changed_data"]:
            df = change_column_type(df, form["cleaned_data"]["column_id"] ,form["cleaned_data"]["dtype"])
        if "name" in form["changed_data"]:
            previous_column_name = df.dtypes.keys()[form["cleaned_data"]["column_id"]]
            df = df.rename(columns={previous_column_name : form["cleaned_data"]["name"]})
    return df


