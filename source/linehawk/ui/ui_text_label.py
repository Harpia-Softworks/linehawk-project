from linehawk.ui.ui_element import UIElement
from linehawk.ui.ui_types import *
from linehawk.ui.ui_theme import UITheme
from linehawk.core.services.warehouse.warehouse_promise import WarehousePromise

import pygame
import typing

class UITextLabel(UIElement): 
    _text: str

    def __init__(
            self,
            parent: UIElement,
            **kwargs: typing.Unpack[UIElement.UIElementKwargs]
    ) -> None:
        super().__init__(UI_TYPE_TEXT_LABEL, parent, **kwargs)
        self._text = ""

    # set and get:
    def set_text(self, new: str) -> typing.Self:
        self._need_regeneration = True
        self._text = new
        return self

    def get_text(self) -> str:
        return self._text

    def _internal_regeneration(self) -> typing.Self:
        # Load the `UITheme`:
        using_theme: UITheme = self.get_theme()

        self._surface = pygame.Surface(
            self._size.calculate(self._parent.get_surface())
        )

        # NOTE: Acquire the font:
        maybe_font: WarehousePromise = (
            using_theme
                .get_warehouse_service()
                .get_font(
                    using_theme
                        .get(self._using_theme)
                        .font,
                    using_theme
                        .get(self._using_theme)
                        .font_size
                )
        )

        if maybe_font.is_present():
            self._surface.fill(
                using_theme
                    .get(self._using_theme)
                    .background_color
            )
            font: pygame.font.Font = (
                maybe_font.get().get_font()
            )
            font_render = font.render(
                self._text,
                False,
                using_theme
                    .get(self._using_theme)
                    .foreground_color
            )
            self._surface.blit(font_render, (0, 0))
            self._need_regeneration = False
        else:
            # Wait for the content to be loaded.
            self._need_regeneration = True

        return self