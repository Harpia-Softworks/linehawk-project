from .gui_element import *
from .gui_enums import *
from .gui_button import GUIButton
import typing

class GUITextButton(GUIButton):
    def __init__(
            self,
            parent: GUIElement,
            **kwargs: typing.Unpack[GUIElementValidKeywords]
    ) -> None:
        super().__init__(
            GUIElementType.TEXT_BUTTON,
            parent,
            **kwargs
        )