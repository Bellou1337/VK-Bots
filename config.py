import os
import json
from datetime import datetime

from modules.Configure import Configure

config = Configure(
    default_config={
        "VK": {
            "token": ""
        }
    }
)

TOKEN = config["VK"]["token"]

groups_data_file = "./groups.json"
if not (os.path.exists(groups_data_file)):
    default_data = {
        "groups": {
            "000000000": {
                "start_from": "05.11.2024",
                "promts": [
                    "anime nekomimi",
                    "gym party",
                    "your own promt"
                ]
            }
        }
    }

    with open(groups_data_file, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(default_data, indent=4))

with open(groups_data_file, "r", encoding='utf-8') as f:
    groups_data_file_conf = dict(json.load(f))
    GROUPS_DATA = groups_data_file_conf['groups']


def update_start_time(group_id: str, date: datetime):
    GROUPS_DATA[str(group_id)]["start_from"] = date.strftime("%d.%m.%Y")
    groups_data_file_conf['groups'] = GROUPS_DATA

    with open(groups_data_file, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(groups_data_file_conf, indent=4))
