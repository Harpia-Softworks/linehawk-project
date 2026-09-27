from linehawk.ui.ui_element import UIElement
from linehawk.ui.ui_types import *
import pygame
import typing

class UIFrame(UIElement):
    # Each `UIFrame` has a `container_surface` that represents the surface that
    # can be drawn elements inside.

    def __init__(
            self,
            parent: UIElement,
            **kwargs: typing.Unpack[UIElement.UIElementKwargs]
    ) -> None:
        super().__init__(UI_TYPE_FRAME, parent, **kwargs)

    def _internal_regeneration(self) -> typing.Self:
        self._surface = pygame.Surface(
            self._size.calculate(self._parent.get_surface())
        )
        # Paint:
        self._surface.fill(
            self.get_theme()
                .get(self._using_theme)
                .background_color
        )
        return self