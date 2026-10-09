from linehawk.GUI.gui_element import *
from linehawk.GUI.gui_enums import *
import typing

class GUIFrame(GUIElement):
    """
    `GUIFrame` contains an background and holds elements.
    ---

    Makes divisions of the `GUIDisplay` and other hold objects.
    """

    def __init__(
            self,
            parent: GUIElement,
            **kwargs: typing.Unpack[GUIElementValidKeywords]
    ) -> None:
        super().__init__(GUIElementType.FRAME, parent, **kwargs)
