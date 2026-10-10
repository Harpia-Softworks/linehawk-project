from pygame import Rect, Surface

from .gui_element import *
from .gui_enums import *
import typing

class GUITextElement(GUIElement):
    __cached_text: pygame.Surface

    def __init__(
            self,
            type: GUIElementType,
            parent: GUIElement,
            **kwargs: typing.Unpack[GUIElementValidKeywords]
    ) -> None:
        super().__init__(type, parent, **kwargs)
        # NOTE: This useless surface is not needed.
        self.__cached_text = (
            self
                .get_root()
                .get_theme()
                .get_warehouse_service()
                .get_placeholder_texture()
        )

    def _redraw(self) -> typing.Self:
        theme = (
            self
                .get_root()
                .get_theme()
        )
        grabbed_font: pygame.Font = (
            theme
                .get_warehouse_service()
                .get_font(
                    theme
                        .get(self._use_style)
                        .font,
                    theme
                        .get(self._use_style)
                        .font_size
                )
        )
        # NOTE: redirect to the language service:
        self.__cached_text = grabbed_font.render(
            self
                .get_root()
                .get_theme()
                .get_language_service()
                .format(self._text),
            True,
            theme
                .get(self._use_style)
                .foreground_color
        ).convert_alpha()
        return self.unmark_redraw()

    def _specific_draw(
            self,
            surface: Surface,
            box: Rect,
            depth: int
    ) -> typing.Self:
        # TODO: DO some REALLY fancy HACK to support alpha.
        pygame.draw.rect(
            surface,
            self
                .get_root()
                .get_theme()
                .get(self._use_style)
                .background_color,
            box
        )
        surface.blit(
            self.__cached_text,
            (
                box.x +
                ((box.w / 2) - (self.__cached_text.get_width() / 2))
                ,
                box.y +
                ((box.h / 2) - (self.__cached_text.get_height() / 2)),
            ),
            (0, 0, box.w, box.h)
        )
        return self