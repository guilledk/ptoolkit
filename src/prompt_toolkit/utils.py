
import csv
import json

from pathlib import Path
from collections import OrderedDict


def get_home_path() -> Path:
    config_dir = Path.home() / '.ptoolkit'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def json_to_csv(source: Path, target: Path):
    # load raw data
    with open(source, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # filter repeated prompts and non expected formatted prompts
    udata = []
    seen_prompts = set()
    for _source in data:
        try:
            act_data = json.loads(_source['act']['data']['request_body'])
            prompt = act_data['params']['prompt']

            if prompt in seen_prompts:
                continue

            seen_prompts.add(prompt)
            udata.append(_source)

        except (json.decoder.JSONDecodeError, KeyError):
            continue

    # finally write to csv
    with open(target, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Timestamp', 'Prompt', 'Block Number', 'Block ID', 'Transaction ID'])

        for idx, _source in enumerate(udata, start=1):
            timestamp = _source['@timestamp']
            act_data = json.loads(_source['act']['data']['request_body'])

            prompt = act_data['params']['prompt']

            block_num = _source['block_num']
            block_id = _source['block_id']
            trx_id = _source['trx_id']

            id_str = f"{idx:010d}"

            writer.writerow([id_str, timestamp, prompt, block_num, block_id, trx_id])


def list_to_csv(target: Path, data: list):
    with open(target, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Prompt', 'NSFW', 'MI'])

        for row in data:
            writer.writerow(row)


def csv_to_list(source: Path) -> list:
    data = []
    with open(source, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(tuple(row[column] for column in reader.fieldnames))

    return data
