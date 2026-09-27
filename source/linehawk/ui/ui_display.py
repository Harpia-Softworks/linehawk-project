from linehawk.ui.ui_element import UIElement
from linehawk.ui.ui_frame import UIFrame
from linehawk.ui.ui_dim import UIDim
from linehawk.ui.ui_theme import UITheme
from linehawk.ui.ui_types import *

import pygame
import typing

class UICursor:
    __rectangle: pygame.Rect
    __size: pygame.Vector2
    __display_surface: pygame.Surface
    __surface: pygame.Surface

    def __init__(
            self,
            display_surface: pygame.Surface,
            size: pygame.Vector2 = pygame.Vector2(16, 16)
    ) -> None:
        self.__size = size
        self.__rectangle = pygame.Rect(size, (0, 0))
        self.__display_surface = display_surface

        # TODO: on the future, load some custom cursor.
        self.__surface = pygame.Surface(self.__size)
        self.__surface.fill((255, 255, 255))

    def tick(self) -> typing.Self:
        mouse_at_x, mouse_at_y = pygame.mouse.get_pos()
        self.__rectangle.update((mouse_at_x, mouse_at_y), self.__size)
        return self

    def draw(self) -> typing.Self:
        self.__display_surface.blit(self.__surface, self.__rectangle)
        return self

    def get_rectangle(self) -> pygame.Rect:
        return self.__rectangle
    
class UIDisplay(UIElement):
    # All the `UIDisplay` has a `root` content.
    _root: UIFrame
    __display_surface: pygame.Surface
    __theme: UITheme
    __cursor: UICursor

    def __init__(self, display_surface: pygame.Surface, theme: UITheme) -> None:
        super().__init__(UI_TYPE_DISPLAY, self)
        self.__display_surface = display_surface
        self.__theme = theme
        self.__cursor = UICursor(self.__display_surface)

        # NOTE: The `_root` base frame is always on window:
        self._root = UIFrame(self)
        self._root.set_size(UIDim(1, 0, 1, 0))
        self._root.set_position(UIDim(0, 0, 0, 0))
        self._root.set_pivot(pygame.Vector2(0, 0))

    # NOTE: we gotta modify this:
    def get_surface(self) -> pygame.Surface:
        return self.__display_surface

    # Bounding Box:
    def get_absolute_position(self) -> pygame.Vector2:
        # NOTE: For the display, we don't do this:
        return pygame.Vector2(0, 0)

    # Tick:
    def _internal_tick(self) -> typing.Self:
        # NOTE: Update the `cursor` position, the `cursor` is always the first
        # to be updated on the `UIDisplay`!
        self.__cursor.tick()
        self._root.tick()
        return self

    # Draw:

    def _internal_draw(self) -> typing.Self:
        self._root.draw()

        # NOTE: Draw the `cursor`, the `cursor` is always the LAST to be 
        # drawn, so nothing stays in the way of the cursor.
        self.__cursor.draw()
        return self

    def get_theme(self) -> UITheme:
        # Eventually, all roads must lead here.
        return self.__theme

    # Redirect to `root`:
    def add_child(self, name: str, child: UIElement) -> typing.Self:
        self._root.add_child(name, child)
        return self

    def get_child(self, name: str) -> UIElement:
        return self._root.get_child(name)

    # Base Iteractions:
    def mouse_down(self) -> None:
        hit: typing.Optional[UIElement] = self._root.get_collision(
            self.__cursor.get_rectangle()
        )
        if hit is not None:
            hit.react_click()

    def mouse_up(self) -> None:
        # TODO: implement this.
        return