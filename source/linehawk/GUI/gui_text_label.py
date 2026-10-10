from .gui_element import *
from .gui_enums import *
from .gui_text_element import GUITextElement
import typing

class GUITextLabel(GUITextElement):
    def __init__(
            self,
            parent: GUIElement,
            **kwargs: typing.Unpack[GUIElementValidKeywords]
    ) -> None:
        super().__init__(GUIElementType.TEXT_LABEL, parent, **kwargs)