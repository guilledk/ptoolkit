from types import SimpleNamespace

from tkinter import (
    Tk, Frame, Label, Button, Scale,
    filedialog, messagebox,
    HORIZONTAL, TOP, LEFT
)


class TkAppContext:

    def __init__(
        self,
        options: dict[str, any] = {'lang': 'en'},
        resources: dict[str, dict] = {
            'text': {
                'en': {
                    'title': 'TkAppContext root window'
                }
            }
        }
    ):
        self._options = options
        self._resources = resources

        self.frame = SimpleNamespace()
        self.label = SimpleNamespace()
        self.button = SimpleNamespace()
        self.scale = SimpleNamespace()

        self._root = Tk()
        self._root.title(self.get_text('title'))
        self.frame.root = self._root

        self._pack_list: list[tuple[str, str, dict]] = []

        self._widget_types: dict[str, type] = {
            'frame': Frame,
            'label': Label,
            'button': Button,
            'scale': Scale
        }

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

    def get_widget_type(self, wtype: str) -> type:
        if wtype not in self._widget_types:
            raise ValueError(f'No widget type \"{wtype}\"')

        return self._widget_types[wtype]

    def get_widget(self, wtype: str, name: str) -> any:
        self.get_widget_type(wtype)
        return getattr(getattr(self, wtype), name)

    def get_frame(self, name: str) -> Frame:
        return self.get_widget('frame', name)

    def get_label(self, name: str) -> Label:
        return self.get_widget('label', name)

    def init_widget(
        self,
        wtype: type,
        name: str,
        parent_wtype: str = 'frame',
        parent_name: str|None = None,
        init_kwargs: dict = {},
        pack_kwargs: dict = {}
    ) -> None:
        if not parent_name:
            parent_name = 'root'

        parent = self.get_widget(parent_wtype, parent_name)
        wclass = self.get_widget_type(wtype)

        w = wclass(parent, **init_kwargs)

        setattr(getattr(self, wtype), name, w)
        self._pack_list.append((name, wtype, pack_kwargs))

    def init_widget_text_resource(
        self,
        *args,
        text_resource: str|None = None,
        **kwargs
    ) -> None:
        if text_resource:
            if 'init_kwargs' not in kwargs:
                kwargs['init_kwargs'] = {}

            kwargs['init_kwargs']['text'] = self.get_text(text_resource)

        self.init_widget(*args, **kwargs)

    def init_frame(self, name: str, **kwargs) -> None:
        self.init_widget('frame', name, **kwargs)

    def init_label(self, name: str, **kwargs) -> None:
        self.init_widget_text_resource('label', name, **kwargs)

    def init_button(self, name: str, **kwargs) -> None:
        self.init_widget_text_resource('button', name, **kwargs)

    def init_scale(self, name: str, **kwargs) -> None:
        self.init_widget('scale', name, **kwargs)

    def pack(self) -> None:
        for name, wtype, pargs in self._pack_list:
            self.get_widget(wtype, name).pack(**pargs)
            print(f'{name} packed')
