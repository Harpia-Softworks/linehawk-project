from linehawk.ui.ui_element import UIElement
from linehawk.ui.ui_types import *
from linehawk.ui.ui_theme import UITheme
from linehawk.core.services.warehouse.warehouse_promise import WarehousePromise

import pygame
import typing

class UITextLabel(UIElement):     
    def __init__(
            self,
            parent: UIElement,
            **kwargs: typing.Unpack[UIElement.UIElementKwargs]
    ) -> None:
        super().__init__(UI_TYPE_TEXT_LABEL, parent, **kwargs)

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
                        .get(self._using_style)
                        .font,
                    using_theme
                        .get(self._using_style)
                        .font_size
                )
        )

        if maybe_font.is_present():
            # NOTE: Do we have the text?
            maybe_text: typing.Optional[str] = (
                using_theme
                    .get_language_service()
                    .format(self._text)
            )
            if maybe_text:
                self._surface.fill(
                    using_theme
                        .get(self._using_style)
                        .background_color
                )
                font: pygame.font.Font = (
                    maybe_font.get().get_font()
                )
                font_render = font.render(
                    maybe_text,
                    False,
                    using_theme
                        .get(self._using_style)
                        .foreground_color
                )
                self._surface.blit(font_render, (0, 0))
                self._need_regeneration = False
            else:
                # Wait for the text to be there.
                self._need_regeneration = True
        else:
            # Wait for the content to be loaded.
            self._need_regeneration = True

        return self