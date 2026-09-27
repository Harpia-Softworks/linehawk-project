from linehawk.ui.ui_dim import UIDim
from linehawk.ui.ui_theme import UITheme
from linehawk.ui.ui_types import *

import typing
import pygame

class UIElementError(BaseException):
    message: str
    def __init__(self, message: str) -> None:
        super().__init__(message)

class UIElementNotFoundError(UIElementError):
    name: str
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f'Not found element: {self.name}')

class UIElementChildAlreadyPresentError(UIElementError):
    name: str
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f'Child already present: {self.name}')

class UIElement:
    """Base all the `UI` elements, even the `UIDisplay` itself."""

    class UIElementKwargs(typing.TypedDict):
        size: typing.NotRequired[UIDim]
        position: typing.NotRequired[UIDim]
        pivot: typing.NotRequired[pygame.Vector2]
        zindex: typing.NotRequired[int]
        use_theme: typing.NotRequired[str]
        visible: typing.NotRequired[bool]
        on_click: typing.NotRequired[typing.Callable[[UIElement], None]]

    # Information about the `UIElement` and the descendents:
    type: int
    _children: typing.Dict[str, 'UIElement']

    # Dimensions of the `UI` element:
    _size: UIDim
    _position: UIDim
    _pivot: pygame.Vector2
    _zindex: int
    _using_theme: str
    _visible: bool

    # Events:
    _on_click: typing.Optional[ typing.Callable[[UIElement], None] ]

    # NOTE: This allows for calculations of the size inside the `frame` or other
    # elements. Having an `base_surface` allows for this kind of properties.
    _parent: UIElement

    # Every element has a `box` (or surface) to draw contenif not namet. This uses more
    # memory, but, bear with me, text leaving the `box` is bad and
    # unpredicatable and we can optimize this on the future.
    _surface: pygame.Surface

    def __init__(
            self,
            type: int,
            parent: UIElement,
            **kwargs: typing.Unpack[UIElementKwargs]
    ) -> None:
        self._parent = parent

        # Continue by defining the types and more.
        self.type = type
        self._children = dict()

        # Extract from `kwargs`:
        self._size = kwargs.get("size", UIDim())
        self._position = kwargs.get("position", UIDim())
        self._zindex = kwargs.get("zindex", 0)
        self._pivot = kwargs.get("pivot", pygame.Vector2(0, 0))
        self._using_theme = kwargs.get("use_theme", "default")
        self._visible = kwargs.get("visible", True)
        self._on_click = kwargs.get("on_click", None)

        # ??
        self._surface = pygame.Surface((0, 0))

        # First Regeneration:
        self._internal_regeneration()

    # For bounding box:
    def get_absolute_position(self) -> pygame.Vector2:
        # What we do here is rather complicated, but, what we want is sum the
        # positions until we have arrived somewhere, from all the current local
        # spaces, we want to `increment` on the `surface`.
        local_position: pygame.Vector2 = self._position.calculate(
            self._parent.get_surface()
        )
        local_position.x -= (self.get_surface().get_width() * self._pivot.x)
        local_position.y -= (self.get_surface().get_height() * self._pivot.y)

        # NOTE: Consider the parent's position, the `UIDisplay` is already 
        # considered here anyways, it will always return (0, 0) which is the
        # default, as `UIDisplay` is always present on the entire screen.
        parent_pos = self._parent.get_absolute_position()
        return local_position + parent_pos

    def get_bounding_box(self) -> pygame.Rect:
        absolute_position: pygame.Vector2 = self.get_absolute_position()
        return pygame.Rect(
            absolute_position.x,
            absolute_position.y,
            self.get_surface().get_width(),
            self.get_surface().get_height()
        )

    # Cursor & Interaction:
    def get_collision(self, rect: pygame.Rect) -> typing.Optional[UIElement]:
        if not self._visible:
            return None
        
        base_rectangle: pygame.Rect = self.get_bounding_box()
        if not base_rectangle.colliderect(rect):
            return None

        # We need to order the elements:
        sorted_children = sorted(
            self._children.values(),
            key=lambda v: v.get_zindex(),
            reverse=True
        )

        for child in sorted_children:
            hit = child.get_collision(rect)
            if hit is not None:
                return hit
            
        return self

    # Various `get_` and `set_`:
    def get_size(self) -> UIDim:
        return self._size
    
    def set_size(self, new: UIDim) -> typing.Self:
        self._size = new
        self._internal_regeneration()
        return self

    def get_position(self) -> UIDim:
        return self._position

    def set_position(self, new: UIDim) -> typing.Self:
        self._position = new
        self._internal_regeneration()
        return self

    def get_zindex(self) -> int:
        return self._zindex

    def set_zindex(self, new: int) -> typing.Self:
        self._zindex = new
        self._internal_regeneration()
        return self

    def get_pivot(self) -> pygame.Vector2:
        return self._pivot

    def set_pivot(self, new: pygame.Vector2) -> typing.Self:
        self._pivot = new
        self._internal_regeneration()
        return self

    def get_using_theme(self) -> str:
        return self._using_theme

    def set_using_theme(self, new: str) -> typing.Self:
        self._using_theme = new
        self._internal_regeneration()
        return self

    # Regenerate:
    def _internal_regeneration(self) -> typing.Self:
        return self

    # Tick:
    def _internal_tick(self) -> typing.Self:
        """You must modify this."""
        return self

    def tick(self) -> UIElement:
        self._internal_tick()
        for key in self._children:
            self._children[key].tick()
        return self

    # Draw:
    def _internal_draw(self) -> typing.Self:
        render_at: pygame.Vector2 = self._position.calculate(
            self._parent.get_surface()
        )
        render_at.x -= (self._surface.get_width() * self._pivot.x)
        render_at.y -= (self._surface.get_height() * self._pivot.y)
        self._parent.get_surface().blit(self._surface, render_at)
        return self

    def draw(self) -> typing.Self:
        self._internal_draw()
        for key in self._children:
            self._children[key].draw()
        return self

    # Add & Management:
    def get_child(self, name: str) -> UIElement:
        if not name in self._children:
            raise UIElementNotFoundError(name)
        return self._children[name]

    def add_child(self, name: str, child: UIElement) -> typing.Self:
        if name in self._children:
            raise UIElementChildAlreadyPresentError(name)
        self._children[name] = child
        return self

    def get_surface(self) -> pygame.Surface:
        return self._surface

    def get_theme(self) -> UITheme:
        return self._parent.get_theme()

    def react_click(self) -> UIElement:
        if self._on_click is not None:
            self._on_click(self)
        return self