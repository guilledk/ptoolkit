import json

from pathlib import Path

from . import TkAppContext
from ..utils import get_home_path, csv_to_dict


def load_settings() -> dict:
    try:
        with open(get_home_path() / 'cataloger.json', 'r') as file:
            return json.load(file)

    except FileNotFoundError:
        return {}


def save_settings(settings: dict) -> None:
    with open(get_home_path() / 'cataloger.json', 'w') as file:
        file.write(json.dumps(settings, indent=4))


class PromptStorage:

    def __init__(
        self,
        source: Path,
        target: Path
    ):
        self.source = source
        self.target = target

        self._source = csv_to_dict(source)

        if target.is_file():
            self._target = csv_to_dict(target)

        else:
            self._target = OrderedDict()


def run_cataloger():
    from tkinter import (
        Tk, Frame, Label, Button, Scale,
        filedialog, messagebox,
        HORIZONTAL, TOP, LEFT
    )

    app = TkAppContext(
        resources={
            'text': {
                'en': {
                    'title': 'Prompt Cataloger 3000 - ACME',

                    'loading': 'Loading...',
                    'no_file_selected': 'No file selected.',
                    'file_not_found': 'File not found!',

                    'select_source_header': 'SOURCE: ',
                    'select_target_header': 'TARGET: ',
                    'select_file_button': 'Select...',
                    'select_source_file': 'Select source file...',
                    'select_target_file': 'Select target file...',

                    'source_file_load_error': 'Could not load source dataset!'
                }
            }
        }
    )

    def update_label(label: str, value: str):
        getattr(app.lable, label).config(text=value)

    def select_file(
        initial_dir: str = str(Path.home()),
        title: str = 'Select file',
        ftypes: list[tuple[str, str]] = [('csv files', '*.csv'), ('all files', '*.*')],
        error_msg: str = app.get_text('file_not_found'),
    ) -> Path :
        file = None
        while not file:
            file = filedialog.askopenfilename(
                initialdir=initial_dir, title=title, filetypes=ftypes)

            if not (file and Path(file).resolve().is_file()):
                messagebox.showerror(str(file) + ': ' + error_msg)
                file = None

        return Path(file).resolve()

    def select_path(
        initial_dir: str = str(Path.home()),
        title: str = 'Select file',
        ftypes: list[tuple[str, str]] = [('csv files', '*.csv'), ('all files', '*.*')]
    ) -> Path:
        file = filedialog.asksaveasfilename(
            initialdir=initial_dir, title=title, filetypes=ftypes)

        return Path(file).resolve()


    def select_source() -> Path:
        file = select_file(
            title=app.get_text('select_source_file'),
            error_msg=app.get_text('source_file_load_error'))

        app.label.source_path.config(text=file)

        return file

    def select_target() -> Path:
        file = select_path(
            title=app.get_text('select_target_file'))

        app.label.target_path.config(text=file)

        return file

    # source & target dataset selection
    app.init_frame(
        'source_select', pack_kwargs={'side': TOP, 'fill': 'x', 'padx': 10, 'pady': 5})
    app.init_frame(
        'target_select', pack_kwargs={'side': TOP, 'fill': 'x', 'padx': 10, 'pady': 5})

    app.init_label(
        'source_path_header',
        text_resource='select_source_header',
        init_kwargs={'font': ('Arial', 18)},
        pack_kwargs={'side': LEFT},
        parent_name='source_select'
    )
    app.init_label(
        'source_path',
        text_resource='loading',
        init_kwargs={'anchor': 'w', 'width': 50},
        pack_kwargs={'side': LEFT, 'fill': 'x'},
        parent_name='source_select'
    )
    app.init_button(
        'source_path',
        text_resource='select_file_button',
        init_kwargs={'command': select_source},
        pack_kwargs={'side': LEFT},
        parent_name='source_select'
    )

    app.init_label(
        'target_path_header',
        text_resource='select_target_header',
        init_kwargs={'font': ('Arial', 18)},
        pack_kwargs={'side': LEFT},
        parent_name='target_select'
    )
    app.init_label(
        'target_path',
        text_resource='loading',
        init_kwargs={'anchor': 'w', 'width': 50},
        pack_kwargs={'side': LEFT, 'fill': 'x'},
        parent_name='target_select'
    )
    app.init_button(
        'target_path',
        text_resource='select_file_button',
        init_kwargs={'command': select_target},
        pack_kwargs={'side': LEFT},
        parent_name='target_select'
    )

    # main input
    app.init_label(
        'prompt', text_resource='loading',
        init_kwargs={'font': ('Arial', 24)},
        pack_kwargs={'pady': 20}
    )

    app.init_label(
        'nsfw_value', text_resource='loading', init_kwargs={'font': ('Arial', 12)})
    app.init_label(
        'mi_value', text_resource='loading', init_kwargs={'font': ('Arial', 12)})

    app.init_scale(
        'nsfw_value', init_kwargs={
            'from_': 0, 'to': 100,
            'orient': HORIZONTAL,
            'command': lambda value: update_label('nsfw_value', value)
        })

    app.init_scale(
        'mi_value', init_kwargs={
            'from_': 0, 'to': 100,
            'orient': HORIZONTAL,
            'command': lambda value: update_label('mi_value', value)
        })

    # load settings
    settings = load_settings()

    last_source = settings.get('last_source')
    source: str = (
        last_source if last_source
        else str(select_source())
    )

    last_target = settings.get('last_target')
    target: str = (
        last_target if last_target
        else str(select_target())
    )

    storage = PromptStorage(source, target)

    # store latest selected settings
    settings['last_source'] = source
    settings['last_target'] = target
    save_settings(settings)

    app.label.source_path.config(text=source)
    app.label.target_path.config(text=target)

    app.pack()

    def on_space_press(event):
        print('Space bar pressed!')

    app.frame.root.bind('<space>', on_space_press)

    app.frame.root.mainloop()
