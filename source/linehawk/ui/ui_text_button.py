from linehawk.ui.ui_element import UIElement
from linehawk.ui.ui_text_element import UITextElement
from linehawk.ui.ui_types import *
import typing

class UITextButton(UITextElement):
    def __init__(
            self,
            parent: UIElement,
            **kwargs: typing.Unpack[UIElement.UIElementKwargs]
    ) -> None:
        super().__init__(UI_TYPE_TEXT_BUTTON, parent, **kwargs)