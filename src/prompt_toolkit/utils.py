
import csv
import json

from pathlib import Path
from collections import OrderedDict


def get_home_path() -> Path:
    config_dir = Path.home() / '.ptoolkit'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def json_to_csv(source: Path, target: Path):
    with open(source, 'r') as file:
        data = json.load(file)

    with open(target, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Timestamp', 'Prompt', 'Block Number', 'Block ID', 'Transaction ID'])

        for idx, _source in enumerate(data, start=1):
            try:
                timestamp = _source['@timestamp']
                act_data = json.loads(_source['act']['data']['request_body'])

                prompt = act_data['params']['prompt']
                block_num = _source['block_num']
                block_id = _source['block_id']
                trx_id = _source['trx_id']

                id_str = f"{idx:010d}"

                writer.writerow([id_str, timestamp, prompt, block_num, block_id, trx_id])

            except (json.decoder.JSONDecodeError, KeyError):
                continue


def csv_to_dict(source: Path) -> OrderedDict:
    data_dict = OrderedDict()

    with open(source, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            key = row['ID']
            value = tuple(row[column] for column in reader.fieldnames if column != 'ID')
            data_dict[key] = value

    return data_dict
