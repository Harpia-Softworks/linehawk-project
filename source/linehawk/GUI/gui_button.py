from .gui_element import *
from .gui_enums import *
from .gui_text_element import GUITextElement
import typing

class GUIButton(GUITextElement):
    def __init__(
            self,
            type: GUIElementType,
            parent: GUIElement,
            **kwargs: typing.Unpack[GUIElementValidKeywords]
    ) -> None:
        super().__init__(type, parent, **kwargs)