 
import csv
from pandas import DataFrame

def parse_data_objects(workflow):
    base_id = 1
    objects = []
    total_files = 0
    for document_link in workflow.source_data_files.all():
        objects = parse_file(document_link.source_data_file.file.file, objects, base_id)
        total_files += 1
    return {"files_info": {"total_files": total_files, "total_objects" : len(objects)}, "objects" :objects}



def parse_file(csv_file, objects, base_id):
    reader = csv.DictReader(csv_file)
    for line in reader:
        line["_id"] = base_id
        objects.append(line)
        base_id += 1
    return objects




def get_data_frame(read_csv):
    pd = DataFrame()
    pd = pd.from_csv(read_csv, infer_datetime_format=True,index_col=None)
    return pd