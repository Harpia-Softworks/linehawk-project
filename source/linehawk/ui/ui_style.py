import pygame
import typing

class UIStyle:
    class UIStyleKwargs(typing.TypedDict):
        background_color: typing.NotRequired[pygame.Color]
        foreground_color: typing.NotRequired[pygame.Color]
        font: typing.NotRequired[str]
        font_size: typing.NotRequired[int]

    """Contains information about the aspects of the element on the UI."""
    background_color: pygame.Color
    foreground_color: pygame.Color
    font: str
    font_size: int

    def __init__(self, **kwargs: typing.Unpack[UIStyleKwargs]) -> None:
        self.background_color = kwargs.get(
            "background_color",
            pygame.Color(0, 0, 0)
        )
        self.foreground_color = kwargs.get(
            "foreground_color",
            pygame.Color(255, 255, 255)
        )
        self.font = kwargs.get(
            "font",
            str("root:Fonts/System/Default.ttf")
        )
        self.font_size = kwargs.get(
            "font_size",
            12
        )
