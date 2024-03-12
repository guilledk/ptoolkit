from types import SimpleNamespace

from tkinter import (
    Tk, Frame, Menu, Label, Text, Button, Scale, Checkbutton,
    filedialog, messagebox,
    END, HORIZONTAL, TOP, LEFT, NORMAL,
    TclError
)

widget_types: dict[str, type] = {
    'frame': Frame,
    'menu': Menu,
    'label': Label,
    'text': Text,
    'button': Button,
    'scale': Scale,
    'checkbutton': Checkbutton
}

widgets_with_text = (Menu, Label, Button, Checkbutton)
widgets_with_foreground = (Menu, Label, Text, Button, Scale, Checkbutton)
widgets_with_active = (Menu, Button, Checkbutton)
widgets_with_indicator = (Checkbutton,)


def _set_text(w, text: str, center: bool = True) -> None:
    post_state = w.cget('state')
    w.config(state=NORMAL)
    w.delete('1.0', END)
    w.insert(END, text)
    if center:
        w.tag_add('center', '1.0', END)
        w.tag_configure('center', justify='center')
    w.config(state=post_state)


class TkAppContext:

    def __init__(
        self,
        options: dict[str, any] = {'lang': 'en'},
        resources: dict[str, dict] = {
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
                    'title': 'TkAppContext root window'
                }
            }
        }
    ):
        self._options = options
        self._resources = resources

        for wtype, _ in widget_types.items():
            setattr(self, wtype, SimpleNamespace())

        self._root = Tk()
        self._root.title(self.get_text('title'))
        self.set_theme(self._root)
        self.frame.root = self._root

        self._pack_list: list[tuple[str, str, dict]] = []
        self._text_resource_list: list[tuple] = []

    def set_language(self, lang: str) -> None:
        self._options['lang'] = lang

        for widget, resource in self._text_resource_list:
            txt = self.get_text(resource)
            if isinstance(widget, Text):
                _set_text(widget, txt)

            else:
                widget.config(text=txt)

    @property
    def language(self) -> str:
        return self._options['lang']

    def get_text(self, key: str) -> str:
        texts = self._resources.get('text')
        if not texts:
            raise ValueError('No text resources registered')

        local_texts = texts.get(self.language)
        if not local_texts:
            raise ValueError(f'No text resources for lang {self.language}')

        text = local_texts.get(key)
        if not text:
            raise ValueError(f'No text resource named {key}')

        return text

    def get_color(self, key: str) -> str:
        colors = self._resources.get('color')
        if not colors:
            raise ValueError('No color resources registered')

        color = colors.get(key)
        if not color:
            raise ValueError(f'No color resource named {key}')

        return color

    def get_widget_type(self, wtype: str) -> type:
        if wtype not in widget_types:
            raise ValueError(f'No widget type \"{wtype}\"')

        return widget_types[wtype]

    def get_widget(self, wtype: str, name: str) -> any:
        self.get_widget_type(wtype)
        try:
            return getattr(getattr(self, wtype), name)

        except AttributeError:
            raise AttributeError(f'Could not get widget {wtype}.{name}')

    def get_frame(self, name: str) -> Frame:
        return self.get_widget('frame', name)

    def get_label(self, name: str) -> Label:
        return self.get_widget('label', name)

    def set_theme(self, widget, theme: dict|None = None) -> None:
        kwargs = {}
        has_fg = type(widget) in widgets_with_foreground
        has_active = type(widget) in widgets_with_active
        has_indicator = type(widget) in widgets_with_indicator

        if not theme:
            theme = {
                'fg': 'lighter', 'bg': 'dark',
                'active_fg': 'light', 'active_bg': 'darker',
                'select_color': 'darker'
            }

        if has_active:
            if has_fg and 'active_fg' in theme:
                kwargs['activeforeground'] = self.get_color(theme['active_fg'])

            if 'active_bg' in theme:
                kwargs['activebackground'] = self.get_color(theme['active_bg'])

        if has_indicator:
            if 'select_color' in theme:
                kwargs['selectcolor'] = self.get_color(theme['select_color'])

        if has_fg:
            kwargs['fg'] = self.get_color(theme['fg'])

        kwargs['bg'] = self.get_color(theme['bg'])

        # try:
        widget.config(**kwargs)

        # except TclError as e:
        #     breakpoint()
        #     raise e

    def init_widget(
        self,
        wtype: type,
        name: str,
        parent_wtype: str = 'frame',
        parent_name: str|None = None,
        init_kwargs: dict = {},
        pack_kwargs: dict = {},
        text_resource: str|None = None,
        theme: dict|None = None
    ) -> None:
        if not parent_name:
            parent_name = 'root'

        parent = self.get_widget(parent_wtype, parent_name)
        wclass = self.get_widget_type(wtype)

        has_text = text_resource and wclass in widgets_with_text

        if has_text:
            init_kwargs['text'] = self.get_text(text_resource)

        w = wclass(parent, **init_kwargs)
        self.set_theme(w, theme=theme)

        if wclass == Text and text_resource:
            _set_text(w, self.get_text(text_resource))
            self._text_resource_list.append((w, text_resource))

        setattr(getattr(self, wtype), name, w)
        self._pack_list.append((name, wtype, pack_kwargs))

        if has_text:
            self._text_resource_list.append((w, text_resource))

    def init_frame(self, name: str, **kwargs) -> None:
        self.init_widget('frame', name, **kwargs)

    def init_menu(self, name: str, **kwargs) -> None:
        self.init_widget('menu', name, **kwargs)

    def init_label(self, name: str, **kwargs) -> None:
        self.init_widget('label', name, **kwargs)

    def init_text(self, name: str, **kwargs) -> None:
        self.init_widget('text', name, **kwargs)

    def init_button(self, name: str, **kwargs) -> None:
        self.init_widget('button', name, **kwargs)

    def init_scale(self, name: str, **kwargs) -> None:
        self.init_widget('scale', name, **kwargs)

    def init_checkbutton(self, name: str, **kwargs) -> None:
        self.init_widget('checkbutton', name, **kwargs)

    def pack(self) -> None:
        for name, wtype, pargs in self._pack_list:
            if wtype in ['menu']:
                continue

            self.get_widget(wtype, name).pack(**pargs)
