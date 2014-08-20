
import csv
from pandas import DataFrame, ExcelFile, Series
import re
import numpy as np
DATA_TYPE_TYPES = {
    "float64": float,
    "int64":  int,
    "object" : object,
}


def get_data_frame(read_csv, skiprows=0, header=0):
    '''Returns a dataframe from a csv buffer'''
    pd = DataFrame()
    pd = pd.from_csv(read_csv, infer_datetime_format=True,index_col=None, skiprows=skiprows, header=header)
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

def get_row_number(ref):
    multiple = len(ref.lower()) - 1
    return multiple * 26 + ord(ref[-1]) -96

def zero_pad_object_id(id):
    '''used to ensure data files appear in order of ID'''
    return ('%d' % id).zfill(11)



def get_ic50_data_columns(series):
    '''
    Split up plate well reference using regex
    '''
    refs = series[0].split(':')
    full_ref = refs[1].strip()
    plate_ref = get_plate_ref(refs[0].strip())
    match = re.match(r"([a-z]+)([0-9]+)", full_ref, re.I)
    if match:
        items = match.groups()
        row_number = get_row_number(items[0])
        return Series(np.array([ series[0],full_ref, plate_ref, series[1],] + list(items) + [row_number,]), index=[ 'fullname', 'full_ref','plate_ref', 'figure', 'well_letter', 'well_number', "row_number",])
    return None

#['fullname', 'figure', 'full_ref', 'well_letter', 'well_number']



def get_ic50_config_columns(series):
    '''
    Add plate well reference with same format as data file
    '''
    series["fullname"] = "%s: %s" % (series["Destination Plate Name"], series["Destination Well"])
    series["full_ref"] = series["Destination Well"]
    series["plate_ref"] = get_plate_ref(series["Destination Plate Name"])
    return series

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


def get_plate_wells_with_sample_ids(series):
    if str(series["Sample ID"]).startswith("BVD"):
        return series["full_ref"]




def get_config_columns(series, sample_codes, excludes_json):
    group = str(series["fullname"])
    if group in sample_codes.groups:
        conf = sample_codes.get_group(group)
        found = None
        for s in conf.iterrows():   
            if s[1]["Sample ID"]:
                #print s[1]["Destination Concentration"]
                if str(s[1]["Destination Concentration"]).lower() !="nan":
                    found = True
                    series["concentration"] = float(s[1]["Destination Concentration"]) * float(1000000)
                    series["global_compound_id"] = s[1]["Sample ID"]
                    series["plate_type"]  = s[1]["Destination Plate Type"]
                    
        if not found:
            series["concentration"] = -1
            series["global_compound_id"] = "NONE"
            series["plate_type"]  = "NONE"
        if excludes_json.get(series["full_ref"], None):
            series["status"] = "active"
        else:
            series["status"] = "inactive"
    else:
        series["status"] = "inactive"

    return series

