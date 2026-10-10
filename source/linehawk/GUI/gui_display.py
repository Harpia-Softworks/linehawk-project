from linehawk.GUI.gui_element import GUIElement
from linehawk.GUI.gui_enums import *
from linehawk.GUI.gui_theme import GUITheme
import pygame
import typing

class GUIDisplay(GUIElement):
    __render_to:    pygame.Surface

    def __init__(
            self,
            render_to:  pygame.Surface,
            theme:      GUITheme
    ) -> None:
        super().__init__(GUIElementType.DISPLAY, self)
        self.__render_to    = render_to
        self.__theme        = theme

    # Soft Overwrites:
    # ---

    def get_root(self) -> GUIDisplay:
        return self

    def get_theme(self) -> GUITheme:
        return self.__theme

    # HARD Overwrites:
    # ---
    # Specially with the `draw` function, on GUIElement it takes surface, box
    # and depth, but here, it doesn't, why? Because the `GUIDisplay` behaves 
    # differently from the normal `GUIElement`, it is the first and main element
    # anyway. There will be a `pyright: ignore` on `self.draw()` because of this
    # reason.

    def draw(self) -> typing.Self:                                              # pyright: ignore
        self.__render_to.fill((0, 0, 0, 0))
        for child in self._children.values():
            child.draw(
                self.__render_to,
                pygame.Rect(
                    (0, 0),
                    self.__render_to.get_size()
                ),
                depth = 0
            )
        return self