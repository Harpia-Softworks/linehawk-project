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

class GUIObject:
    # Control (internal):
    _need_redraw:       bool
    _surface:           pygame.Surface
    _type:              GUIElementType
    
    # Appearance:
    position:           GUIDim
    size:               GUIDim
    pivot:              pygame.Vector2
    use_style:          str

    # Specific GUIObject Properties:
    text:               str

    def __init__(
            self,
            type: GUIElementType,
            **kwargs: typing.Unpack[GUIObjectValidKeywords]
    ) -> None:
        # Define `root` types:
        self._type = type

        # Define the position, size and other elemental properties:
        self.position               = kwargs.get("position", GUIDim())
        self.size                   = kwargs.get("size", GUIDim())
        self.pivot                  = kwargs.get("pivot", pygame.Vector2(0, 0))
        self.use_style              = kwargs.get("use_style", str("default"))
        self.text                   = kwargs.get("text", str("N/A"))
        
        # All objects start with the need to redraw:
        self._need_redraw           = True
        self._surface               = pygame.Surface((0, 0))