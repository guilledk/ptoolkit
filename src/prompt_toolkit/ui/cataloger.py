import json

from tkinter import END, DISABLED
from pathlib import Path
from collections import OrderedDict

from . import _set_text, TkAppContext
from ..utils import get_home_path, csv_to_list, list_to_csv


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
        source: str,
        target: str
    ):
        self.source = Path(source)
        self.target = Path(target)

        self._source = csv_to_list(source)
        self._target = []

        if self.target.is_file():
            self._target = [
                [float(nsfw_val), int(mi_val)]
                for _id, prompt, nsfw_val, mi_val in csv_to_list(target)
            ]

        self._current_index = len(self._target)

        for i in range(self._current_index, len(self._source)):
            self._target.append([-1, -1])

    def get_values(self) -> list[float, float]:
        return self._target[self._current_index]

    def get_prompt(self) -> str:
        return self._source[self._current_index]

    def set_value(self, index: int, value) -> None:
        self._target[self._current_index][index] = value

    def save_target(self) -> None:
        final = []
        for i, values in enumerate(self._target[:self._current_index + 1]):
            _id, ts, prompt, block_num, block_id, trx_id = self._source[i]
            final.append((
                _id, prompt, *values))

        list_to_csv(self.target, final)

    def prev_prompt(self) -> None:
        self.save_target()
        if self._current_index > 0:
            self._values_changed = False
            self._current_index -= 1

    def next_prompt(self) -> None:
        self.save_target()
        if self._current_index < (len(self._source) - 1):
            self._values_changed = False
            self._current_index += 1


_nsfw_help = (
    'The Not Safe For Work (NSFW) factor is a percentage that '
    'measures if a given prompt could yield content that is not'
    ' appropriate for minors without supervision or in some '
    'cases not at all.\n'
    'Guidelines for this factor follow the Movie Ratings Assosiation system but applied to prompts.\n'
    '0 - G - All ages admitted. Nothing that would offend parents for viewing by children.\n'
    '25 - PG - Some material may not be suitable for children. Parents urged to give \"parental'
    ' guidance\". May contain some material parents might not like for their young children.\n'
    '50 - PG-13 - Some material may be inappropriate for children under 13. Parents are urged '
    'to be cautious. Some material may be inappropriate for pre-teenagers.\n'
    '75 - R - Under 17 requires accompanying parent or adult guardian. Contains some adult '
    'material. Parents are urged to learn more about the film before taking their young '
    'children with them.\n'
    '100 - NC-17 - No one 17 and under admitted. Clearly adult. Children are not admitted.\n'
)

_nsfw_help_es = (
    'El factor No Apto Para el Trabajo (NSFW por sus siglas en inglés) es un porcentaje que '
    'mide si un comando dado podría generar contenido que no es apropiado para menores sin '
    'supervisión o en algunos casos no lo es en absoluto.\n'
    'Las pautas para este factor siguen el sistema de Calificaciones de Películas de la '
    'Asociación de Cine pero aplicado a comandos.\n'
    '0 - G - Apto para todos los públicos. Nada que pueda ofender a los padres por ser visto por niños.\n'
    '25 - PG - Algunos materiales pueden no ser adecuados para niños. Se insta a los padres a dar "orientación '
    'parental". Puede contener material que algunos padres podrían no considerar adecuado para sus hijos pequeños.\n'
    '50 - PG-13 - Algunos materiales pueden ser inapropiados para menores de 13 años. Se insta a los padres '
    'a ser cautelosos. Algunos materiales pueden ser inapropiados para preadolescentes.\n'
    '75 - R - Menores de 17 años requieren acompañamiento de un padre o tutor adulto. Contiene '
    'material para adultos. Se insta a los padres a informarse más sobre la película antes de llevar '
    'a sus hijos pequeños con ellos.\n'
    '100 - NC-17 - No se admiten menores de 17 años. Claramente para adultos. No se admite a niños.\n'
)


_mi_help = (
    'The Minor Involvment (MI) factor is a true or false value that indicates '
    'if a given prompt could lead to generate content with minors on it, be it '
    'animated or on any art stlye.\n'
    'Any prompt that could generate a picture with a minor on it counts, doesn\'t'
    'have to be a nefarious prompt can be a simple picture of a kid playing with a ball.'
)

_mi_help_es = (
    'El factor de Involucramiento de Menores (MI por sus siglas en inglés) es un valor verdadero o falso que indica '
    'si un comando dado podría llevar a generar contenido con menores en él, ya sea '
    'animado o en cualquier estilo de arte.\n'
    'Cualquier comando que pueda generar una imagen con un menor en ella cuenta, no tiene '
    'que ser un comando nefasto, puede ser una simple imagen de un niño jugando con una pelota.'
)

def run_cataloger():
    from tkinter import (
        Tk, Frame, Label, Button, Scale, BooleanVar,
        filedialog, messagebox,
        BOTH, HORIZONTAL, TOP, LEFT, RIGHT
    )

    app = TkAppContext(
        resources={
            'color': {
                'darker': '#070707',
                'dark': '#141414',
                'lighter': '#e5e5e5',
                'light': '#d1d1d1',

                'bad': '#c44c4a',
                'bad_dark': '#943533',
                'good': '#386b2a',
                'good_dark': '#204d14'
            },
            'text': {
                'en': {
                    'title': 'Prompt Cataloger 3000 - ACME',

                    'loading': 'Loading...',
                    'no_file_selected': 'No file selected.',
                    'file_not_found': 'File not found!',

                    'select_file_error': 'Error while selecting file!',
                    'select_source_header': 'SOURCE: ',
                    'select_target_header': 'TARGET: ',
                    'select_file_button': 'Select...',
                    'select_source_file': 'Select source file...',
                    'select_target_file': 'Select target file...',

                    'source_file_load_error': 'Could not load source dataset!',

                    'prev_prompt': '<',
                    'next_prompt': '>',

                    'nsfw_label': 'NSFW: ',
                    'nsfw_help_title': 'NSFW factor help',
                    'nsfw_help': _nsfw_help,
                    'mi_label': 'Minor Involvment',
                    'mi_help_title': 'MI factor help',
                    'mi_help': _mi_help
                },
                'es': {
                    'title': 'Catalogador de Prompts - ACME',

                    'loading': 'Cargando...',
                    'no_file_selected': 'Ningun archivo seleccionado.',
                    'file_not_found': 'Archivo no encontrado!',

                    'select_file_error': 'Error al seleccionar archivo!',
                    'select_source_header': 'FUENTE: ',
                    'select_target_header': 'OBJETIVO: ',
                    'select_file_button': 'Seleccionar...',
                    'select_source_file': 'Seleccionar fuente...',
                    'select_target_file': 'Seleccionar objetivo...',

                    'source_file_load_error': 'No se pudo cargar la fuente de datos!',

                    'prev_prompt': '<',
                    'next_prompt': '>',

                    'nsfw_label': 'NSFW: ',
                    'nsfw_help_title': 'Ayuda factor NSFW',
                    'nsfw_help': _nsfw_help_es,
                    'mi_label': 'Involucra Menores',
                    'mi_help_title': 'Ayuda factor MI',
                    'mi_help': _mi_help_es
                }
            }
        }
    )

    def select_file(
        initial_dir: str = str(Path()),
        title: str = 'Select file',
        ftypes: list[tuple[str, str]] = [('csv files', '*.csv'), ('all files', '*.*')],
        error_msg: str = app.get_text('file_not_found'),
    ) -> Path :
        file = None
        while not file:
            file = filedialog.askopenfilename(
                initialdir=initial_dir, title=title, filetypes=ftypes)

            if not (file and Path(file).resolve().is_file()):
                messagebox.showerror(
                    title=app.get_text('select_file_error'),
                    message=str(file) + ': ' + error_msg)
                file = None

        return Path(file).resolve()

    def select_path(
        initial_dir: str = str(Path()),
        title: str = 'Select file',
        ftypes: list[tuple[str, str]] = [('csv files', '*.csv'), ('all files', '*.*')],
        error_msg: str = app.get_text('file_not_found'),
    ) -> Path:
        file = None
        while not file:
            file = filedialog.asksaveasfilename(
                initialdir=initial_dir, title=title, filetypes=ftypes)

            if not file:
                messagebox.showerror(
                    title=app.get_text('select_file_error'),
                    message=str(file) + ': ' + error_msg)

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
        'source_select',
        pack_kwargs={'side': TOP, 'fill': 'x', 'padx': 10, 'pady': 5}
    )
    app.init_frame(
        'target_select', pack_kwargs={'side': TOP, 'fill': 'x', 'padx': 10, 'pady': 5})
    app.init_frame(
        'status_display', pack_kwargs={'side': TOP, 'fill': 'x', 'padx': 10, 'pady': 5})
    app.init_frame(
        'prompt_display', pack_kwargs={'side': TOP, 'fill': 'x', 'padx': 10, 'pady': 5})
    app.init_frame(
        'user_input_top', pack_kwargs={'side': TOP, 'fill': 'x', 'padx': 10, 'pady': 5})
    app.init_frame(
        'user_input_bottom', pack_kwargs={'side': TOP, 'fill': 'x', 'padx': 10, 'pady': 5})

    app.init_label(
        'source_path_header',
        text_resource='select_source_header',
        init_kwargs={'font': ('Arial', 18), 'width': 10},
        pack_kwargs={'side': LEFT},
        parent_name='source_select'
    )
    app.init_label(
        'source_path',
        text_resource='loading',
        init_kwargs={'anchor': 'w', 'bg': 'black', 'fg': 'white'},
        pack_kwargs={'side': LEFT, 'fill': 'x', 'expand': True},
        parent_name='source_select'
    )
    app.init_button(
        'source_path',
        text_resource='select_file_button',
        init_kwargs={'command': select_source},
        pack_kwargs={'side': RIGHT, 'padx': 20},
        parent_name='source_select'
    )

    app.init_label(
        'target_path_header',
        text_resource='select_target_header',
        init_kwargs={'font': ('Arial', 18), 'width': 10},
        pack_kwargs={'side': LEFT},
        parent_name='target_select'
    )
    app.init_label(
        'target_path',
        text_resource='loading',
        init_kwargs={'anchor': 'w', 'bg': 'black', 'fg': 'white'},
        pack_kwargs={'side': LEFT, 'fill': 'x', 'expand': True},
        parent_name='target_select'
    )
    app.init_button(
        'target_path',
        text_resource='select_file_button',
        init_kwargs={'command': select_target},
        pack_kwargs={'side': RIGHT, 'padx': 20},
        parent_name='target_select'
    )

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

    last_lang = settings.get('last_lang')
    lang: str = (
        last_lang if last_lang
        else 'en'
    )
    app.set_language(lang)

    # store latest selected settings
    settings['last_source'] = source
    settings['last_target'] = target
    save_settings(settings)

    storage = PromptStorage(source, target)

    mi_var = BooleanVar()
    mi_theme = None

    def update_value_display() -> None:
        nsfw_val, mi_val = storage.get_values()

        if nsfw_val < 0:
            nsfw_val = 0

        display_val = int(nsfw_val * 100)
        app.scale.nsfw_value.set(display_val)

        display_val = False
        match mi_val:
            case -1:
                mi_theme = None

            case 0:
                mi_theme = {
                    'fg': 'lighter', 'bg': 'good',
                    'active_fg': 'light', 'active_bg': 'good_dark'
                }

            case 1:
                display_val = True
                mi_theme = {
                    'fg': 'lighter', 'bg': 'bad',
                    'active_fg': 'light', 'active_bg': 'bad_dark'
                }

        mi_var.set(display_val)
        app.set_theme(app.checkbutton.mi_value, theme=mi_theme)

    def display_prompt() -> None:
        app.label.source_path.config(text=source)
        app.label.target_path.config(text=target)

        source_prompt = storage.get_prompt()

        _id, ts, prompt, block_num, block_id, trx_id = source_prompt

        update_value_display()

        app.label.prompt_index.config(text=f'{storage._current_index + 1}/{len(storage._source)}')

        _set_text(app.text.prompt, prompt)

    def show_help(topic: str):
        key = topic + '_help'
        messagebox.showinfo(
            title=app.get_text(key + '_title'),
            message=app.get_text(key))

    def change_prompt(forward: bool = True):
        if forward:
            storage.next_prompt()
        else:
            storage.prev_prompt()

        display_prompt()

    def set_language(lang: str):
        settings = load_settings()
        settings['last_lang'] = lang
        save_settings(settings)
        app.set_language(lang)
        display_prompt()

    app.init_menu('menu_bar')
    app.init_menu(
        'langs', init_kwargs={'tearoff': 0}, parent_wtype='menu', parent_name='menu_bar')

    app.menu.langs.add_command(label='English', command=lambda: set_language('en'))
    app.menu.langs.add_command(label='Español', command=lambda: set_language('es'))

    app.menu.menu_bar.add_cascade(label='Language/Lenguaje', menu=app.menu.langs)
    app.frame.root.config(menu=app.menu.menu_bar)

    # status display
    app.init_button(
        'prompt_prev', text_resource='prev_prompt',
        init_kwargs={
            'font': ('Arial', 24),
            'command': lambda: change_prompt(forward=False)
        },
        pack_kwargs={'side': LEFT, 'padx': 20},
        parent_name='status_display'
    )
    app.init_label(
        'prompt_index', text_resource='loading',
        init_kwargs={'font': ('Arial', 24)},
        pack_kwargs={'side': LEFT, 'fill': 'x', 'expand': True},
        parent_name='status_display'
    )
    app.init_button(
        'prompt_next', text_resource='next_prompt',
        init_kwargs={
            'font': ('Arial', 24),
            'command': change_prompt
        },
        pack_kwargs={'side': RIGHT, 'padx': 20},
        parent_name='status_display'
    )

    # main prompt display
    app.init_text(
        'prompt', text_resource='loading',
        init_kwargs={'font': ('Arial', 24), 'width': 80, 'height': 10},
        pack_kwargs={'fill': BOTH, 'expand': True},
        parent_name='prompt_display'
    )
    app.text.prompt.config(state=DISABLED)

    app.init_label(
        'nsfw_value',
        text_resource='nsfw_label',
        init_kwargs={'font': ('Arial', 18), 'width': 10},
        pack_kwargs={'side': LEFT},
        parent_name='user_input_top'
    )

    # user input
    def _handle_nsfw_user_update(event):
        storage.set_value(0, app.scale.nsfw_value.get() / 100)
        update_value_display()

    app.init_scale(
        'nsfw_value',
        init_kwargs={
            'from_': 0, 'to': 100,
            'orient': HORIZONTAL,
            'command': _handle_nsfw_user_update
        },
        pack_kwargs={'side': LEFT, 'fill': 'x', 'expand': True},
        parent_name='user_input_top'
    )
    app.init_button(
        'nsfw_value',
        init_kwargs={'text': '?', 'command': lambda: show_help('nsfw')},
        pack_kwargs={'side': RIGHT, 'padx': 20},
        parent_name='user_input_top'
    )

    def _handle_mi_user_update():
        storage.set_value(1, int(mi_var.get()))
        update_value_display()

    app.init_checkbutton(
        'mi_value',
        text_resource='mi_label',
        init_kwargs={
            'variable': mi_var,
            'font': ('Arial', 18),
            'command': _handle_mi_user_update
        },
        pack_kwargs={'side': LEFT, 'fill': 'x', 'expand': True},
        parent_name='user_input_bottom'
    )
    app.init_button(
        'mi_value',
        init_kwargs={'text': '?', 'command': lambda: show_help('mi')},
        pack_kwargs={'side': RIGHT, 'padx': 20},
        parent_name='user_input_bottom'
    )

    display_prompt()

    app.pack()

    app.frame.root.bind('<space>', lambda event: _next_prompt())
    # app.frame.root.bind('<Configure>', lambda event: app.label.prompt.config(wraplength=event.width))

    app.frame.root.mainloop()
