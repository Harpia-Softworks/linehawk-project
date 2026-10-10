from linehawk.GUI.gui_dim import GUIDim
from linehawk.GUI.gui_enums import *
import typing
import pygame

class GUIObjectValidKeywords(typing.TypedDict):
    position:       typing.NotRequired[GUIDim] 
    size:           typing.NotRequired[GUIDim]
    pivot:          typing.NotRequired[pygame.Vector2]
    use_style:      typing.NotRequired[str]
    text:           typing.NotRequired[str]
    visible:        typing.NotRequired[bool]

class GUIObject:
    # Control (internal):
    _need_redraw:       bool
    _type:              GUIElementType
    
    # Appearance:
    _position:          GUIDim
    _size:              GUIDim
    _pivot:             pygame.Vector2
    _use_style:         str
    _visible:           bool

    # Specific GUIObject Properties:
    _text:               str

    def __init__(
            self,
            type: GUIElementType,
            **kwargs: typing.Unpack[GUIObjectValidKeywords]
    ) -> None:
        # Define `root` types:
        self._type = type

        # Define the position, size and other elemental properties:
        self._position              = kwargs.get("position", GUIDim())
        self._size                  = kwargs.get("size", GUIDim())
        self._pivot                 = kwargs.get("pivot", pygame.Vector2(0, 0))
        self._use_style             = kwargs.get("use_style", str("default"))
        self._text                  = kwargs.get("text", str("N/A"))
        self._visible               = kwargs.get("visible", True)
        
        # All objects start with the need to redraw:
        self._need_redraw           = True

    def set_text(self, new: str) -> typing.Self:
        self._text = new
        self._need_redraw = True
        return self

    def get_text(self) -> str:
        return self._text