import json
import os
from pathlib import Path
from typing import List, Dict, Union


def load_json_dict(file_name: Union[str, Path], default=None) -> Dict:
    if os.path.isfile(file_name):
        with open(file_name) as json_file:
            data = json.load(json_file)
    else:
        data = default

    return data


def save_json_dict(path: Union[str, Path], data):
    with open(path, 'w') as fp:
        json.dump(data, fp, indent="\t")


def get_local_file_list(path: Union[str, Path]) -> List:
    filelist = []

    for root, dirs, files in os.walk(path):
        for file in files:
            # append the file name to the list
            filelist.append(os.path.join(root, file))
    return filelist
