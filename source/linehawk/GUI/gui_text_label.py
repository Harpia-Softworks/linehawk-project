from linehawk.GUI.gui_element import *
from linehawk.GUI.gui_enums import *
import typing

class GUITextLabel(GUIElement):
    """
    `GUITextElement` contains basic methods for `GUITextButton` and
    `GUITextLabel` and more elements.
    """
    _rendered_text: pygame.Surface
    
    def __init__(
            self,
            type: GUIElementType,
            parent: GUIElement,
            **kwargs: typing.Unpack[GUIElementValidKeywords]
    ) -> None:
        super().__init__(type, parent, **kwargs)

    def _update_rendered_text(self):
        """
        Update the `self._rendered_text` to contain new text.
        """
        pass