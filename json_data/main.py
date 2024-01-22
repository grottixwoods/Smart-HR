from space_controller import process_spaces_jsonl
from overlaping_сheck import сheck_overlaping
from overlaping_fix import fix_overlapping

json_path = 'json_data/jsons/all.jsonl' 

if __name__  == '__main__':
    process_spaces_jsonl(json_path)
    сheck_overlaping(json_path)
    fix_overlapping(json_path)
    