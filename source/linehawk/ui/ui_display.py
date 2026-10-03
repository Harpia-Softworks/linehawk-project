from linehawk.ui.ui_element import UIElement
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
        self.__surface = (
            pygame
                .Surface(self.__size)
                .convert_alpha()
        )
        self.__surface.fill((255, 255, 255, 255))

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
    __display_surface: pygame.Surface
    __theme: UITheme
    __cursor: UICursor
    __regenerate_on: int

    def __init__(self, display_surface: pygame.Surface, theme: UITheme) -> None:
        super().__init__(UI_TYPE_DISPLAY, self)
        self.__display_surface = display_surface
        self.__theme = theme
        self.__cursor = UICursor(self.__display_surface)

    # NOTE: we gotta modify this:
    def get_surface(self) -> pygame.Surface:
        return self.__display_surface

    # Bounding Box:
    def get_absolute_position(self) -> pygame.Vector2:
        # NOTE: For the display, we don't do this:
        return pygame.Vector2(0, 0)

    # Mouse & Interaction:
    def handle_click(self) -> UIElement:
        for child in self._children:
            hit: typing.Optional[UIElement] = (
                self
                    ._children[child]
                    .get_collision(self.__cursor.get_rectangle())
            )
            if hit is not None:
                hit.on_mouse_event()
        return self

    # Tick:
    def _internal_tick(self) -> typing.Self:
        # NOTE: Update the `cursor` position, the `cursor` is always the first
        # to be updated on the `UIDisplay`!
        self.__cursor.tick()
        return self

    # Draw:
    def draw(self) -> typing.Self:
        for key in self._children:
            self._children[key].draw()
        self._internal_draw()
        return self

    def _internal_draw(self) -> typing.Self:
        # NOTE: Draw the `cursor`, the `cursor` is always the LAST to be 
        # drawn, so nothing stays in the way of the cursor.
        self.__cursor.draw()
        return self

    def get_theme(self) -> UITheme:
        # Eventually, all roads must lead here.
        return self.__theme

    def switch_display_surface(
            self,
            new_display: pygame.Surface
    ) -> typing.Self:
        self.__display_surface = new_display
        return self