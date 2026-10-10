from linehawk.GUI.gui_enums import *
import pygame
import typing

class GUIStyle:
    class GUIStyleKwargs(typing.TypedDict):
        background_color: typing.NotRequired[pygame.Color]
        foreground_color: typing.NotRequired[pygame.Color]
        border_color: typing.NotRequired[pygame.Color]
        border_thickness: typing.NotRequired[int]

        font: typing.NotRequired[str]
        font_size: typing.NotRequired[int]
        text_valign: typing.NotRequired[GUITextVerticalAlignment]
        text_halign: typing.NotRequired[GUITextHorizontalAlignment]

    """Contains information about the aspects of the element on the UI."""
    background_color: pygame.Color
    foreground_color: pygame.Color
    font: str
    font_size: int
    border_color: pygame.Color
    border_thickness: int

    text_valign: GUITextVerticalAlignment
    text_halign: GUITextHorizontalAlignment

    def __init__(self, **kwargs: typing.Unpack[GUIStyleKwargs]) -> None:
        self.background_color   = kwargs.get("background_color", pygame.Color(0, 0, 0, 255))
        self.foreground_color   = kwargs.get("foreground_color", pygame.Color(255, 255, 255, 255))
        self.border_color       = kwargs.get("border_color", pygame.Color(255, 255, 255, 255))
        self.border_thickness   = kwargs.get("border_thickness", 5)
        self.font               = kwargs.get("font", str("root:Fonts/System/Default.ttf"))
        self.font_size          = kwargs.get("font_size", 12)
        self.text_valign        = kwargs.get("text_valign", GUITextVerticalAlignment.CENTER)
        self.text_halign        = kwargs.get("text_halign", GUITextHorizontalAlignment.CENTER)