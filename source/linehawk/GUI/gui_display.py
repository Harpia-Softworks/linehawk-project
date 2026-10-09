from linehawk.GUI.gui_element import GUIElement
from linehawk.GUI.gui_enums import *
from linehawk.GUI.gui_theme import GUITheme
import pygame
import typing

class GUIDisplay(GUIElement):
    __render_to: pygame.Surface
    __theme: GUITheme

    def __init__(
            self,
            render_to: pygame.Surface,
            theme: GUITheme
    ) -> None:
        # Important to define:
        self.__render_to = render_to
        self.__theme = theme

        # Initialize the `super().__init__()` class (aka. GUIElement):
        super().__init__(GUIElementType.DISPLAY, None)

    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # Replacements specific to `GUIDisplay`
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    def get_theme(self) -> GUITheme:
        """
        Return the `self.__theme` you provided on
        `__init__(..., theme: GUITheme)`.
        """
        return self.__theme

    def get_root(self) -> GUIElement:
        """
        In the `GUIDisplay` this function returns `self`.
        """
        return self

    def get_parent(self) -> GUIElement:
        """
        In the `GUIDisplay` this function returns `self`.
        """
        return self

    def get_surface(self) -> pygame.Surface:
        """
        In the `GUIDisplay` this function returns the `self.__render_to`, which
        is the `pygame.Surface` you desired the elements to be drawn to.
        """
        return self.__render_to

    def _deploy_to_parent_surface(self) -> typing.Self:
        """
        This function is replaced in `GUIDisplay` because, on `GUIDisplay`, the
        `pygame.Surface` on the top is already the `self.__render_to` surface,
        meaning it would make no sense to draw it.
        """
        return self