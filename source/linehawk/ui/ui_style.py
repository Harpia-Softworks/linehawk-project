import pygame
import typing

class UIStyle:
    class UIStyleKwargs(typing.TypedDict):
        background_color: typing.NotRequired[pygame.Color]
        foreground_color: typing.NotRequired[pygame.Color]
        font: typing.NotRequired[str]

    """Contains information about the aspects of the element on the UI."""
    background_color: pygame.Color
    foreground_color: pygame.Color
    font: str

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
            str("default")
        )
