
from pathlib import Path

import click

from .utils import json_to_csv
from .ui.cataloger import run_cataloger


@click.group()
def ptoolkit():
    ...

@ptoolkit.command()
def cataloger():
    run_cataloger()


@ptoolkit.group()
def data():
    ...

@data.command('es-to-csv')
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.argument('output_path', type=click.Path(writable=True, path_type=Path))
def es_to_csv(input_path, output_path):
    json_to_csv(input_path, output_path)
