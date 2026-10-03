from linehawk.ui.ui_element import UIElement
from linehawk.ui.ui_types import *
from linehawk.ui.ui_theme import UITheme
from linehawk.core.services.warehouse.warehouse_promise import WarehousePromise

import pygame
import typing

class UITextElement(UIElement):
    def __init__(
            self,
            type: int,
            parent: UIElement,
            **kwargs: typing.Unpack[UIElement.UIElementKwargs]
    ) -> None:
        super().__init__(type, parent, **kwargs)

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

        self._surface = (
            pygame.Surface(
                self._size.calculate(self._parent.get_surface())
            )
            .convert_alpha()
        )

        # HACK: This fixes some problem with the `A` layer.
        self._surface.fill((0, 0, 0, 0))

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
                    maybe_font
                        .get()
                        .get_font()
                )

                # NOTE: Can we fit the `maybe_text` on the screen.
                takes_w, takes_h = font.size(maybe_text)

                if (
                    (takes_w <= self._surface.get_width()) and
                    (takes_h <= self._surface.get_height())
                ):
                    # Normal render:
                    font_render = font.render(
                        maybe_text,
                        False,
                        using_theme
                            .get(self._using_style)
                            .foreground_color
                    ).convert_alpha()
                    self._surface.blit(
                        font_render,
                        (
                            (
                                (self._surface.get_width() * 0.5) -
                                (font_render.get_width() * 0.5)
                            ),
                            (
                                (self._surface.get_height() * 0.5) -
                                (font_render.get_height() * 0.5)
                            )
                        )
                    )
                else:
                    # Split-Render.
                    words: typing.List[str] = maybe_text.split(' ')
                    rendered_text: typing.List[pygame.Surface] = list()
                    total_height: int = 0
                    for word in words:
                        rendered: pygame.Surface = (
                            font.render(
                                word,
                                False,
                                using_theme
                                    .get(self._using_style)
                                    .foreground_color
                            )
                            .convert_alpha()
                        )
                        total_height += rendered.get_height()
                        rendered_text.append(rendered)
                    for index, text_surface in enumerate(rendered_text):
                        self._surface.blit(
                            text_surface,
                            (
                                (
                                    (self._surface.get_width() * 0.5) -
                                    (text_surface.get_width() * 0.5)
                                ),
                                (
                                    (self._surface.get_height() * 0.5) -
                                    ((total_height * 0.5) ) +
                                    (
                                        (total_height / len(rendered_text)) *
                                        index
                                    )
                                )
                            )
                        )
                self._need_regeneration = False
            else:
                # Wait for the text to be there.
                self._need_regeneration = True
        else:
            # Wait for the content to be loaded.
            self._need_regeneration = True

        return self