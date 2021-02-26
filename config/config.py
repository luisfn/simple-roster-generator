import json
import os
import re


def get(path):
    config = {}
    keys = path.split('.')

    for file in search_config_files():
        with open(file, "r") as json_file:
            config = config | json.load(json_file)

    for key in keys:
        config = config.get(key)

    return config


def search_config_files():
    files_found = []

    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in [file for file in filenames if re.search('.*.json', file)]:
            files_found.append(os.path.join(dirpath, filename))

    return files_found
