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

class UIElementInvalidPathError(UIElementError):
    """
    @note Used by `UIElement.get()` method.
    """
    path: str
    at_element: str
    index: int
    def __init__(self, path: str, at_element: str, index: int) -> None:
        self.path = path
        self.at_element = at_element
        self.index = index
        super().__init__(f'On query: {path}, failed to get element: {at_element} (INDEX: {index})')

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
        use_style: typing.NotRequired[str]
        visible: typing.NotRequired[bool]
        on_click: typing.NotRequired[typing.Callable[[UIElement], None]]
        text: typing.NotRequired[str]

    # Information about the `UIElement` and the descendents:
    type: int
    _children: typing.Dict[str, 'UIElement']

    # Properties:
    _text: str

    # Dimensions of the `UI` element:
    _size: UIDim
    _position: UIDim
    _pivot: pygame.Vector2
    _zindex: int
    _using_theme: str
    _visible: bool
    _need_regeneration: bool

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
        self._using_style = kwargs.get("use_style", "default")
        self._visible = kwargs.get("visible", True)
        self._on_click = kwargs.get("on_click", None)

        # Data:
        self._text = kwargs.get("text", "...")

        # ??
        self._surface = (
            pygame
                .Surface((0, 0))
                .convert_alpha()
        )
        self._need_regeneration = True

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
        if not self._visible: return None

        # Calculate an `bounding_box()` so we can test for possible cursor
        # collisions by the way.
        base_rectangle: pygame.Rect = self.get_bounding_box()

        # Not any collisions, then we don't even return anything.
        if not base_rectangle.colliderect(rect): return None

        # To prevent errors such as click racing, we do this.
        sorted_children = sorted(
            self._children.values(),
            key=lambda v: v.get_zindex(),
            reverse=True
        )

        # By the Sorted Elements, we get the collision from them.
        for child in sorted_children:
            hit = child.get_collision(rect)
            if hit is not None:
                return hit

        # NOTE: We only return an item that supports mouse.
        return self

    def on_mouse_event(self) -> UIElement:
        if self._on_click is not None:
            self._on_click(self)
        return self

    # Various `get_` and `set_`:
    def get_size(self) -> UIDim:
        return self._size
    
    def set_size(self, new: UIDim) -> typing.Self:
        self._size = new
        self._need_regeneration = True
        return self

    def get_position(self) -> UIDim:
        return self._position

    def set_position(self, new: UIDim) -> typing.Self:
        self._position = new
        self._need_regeneration = True
        return self

    def get_zindex(self) -> int:
        return self._zindex

    def set_zindex(self, new: int) -> typing.Self:
        self._zindex = new
        self._need_regeneration = True
        return self

    def get_pivot(self) -> pygame.Vector2:
        return self._pivot

    def set_pivot(self, new: pygame.Vector2) -> typing.Self:
        self._pivot = new
        self._need_regeneration = True
        return self

    def get_using_theme(self) -> str:
        return self._using_style

    def set_using_theme(self, new: str) -> typing.Self:
        self._using_style = new
        self._need_regeneration = True
        return self

    def set_on_click(
            self,
            new: typing.Callable[[UIElement], None]
    ) -> typing.Self:
        self._on_click = new        
        return self

    # Regenerate:
    def _internal_regeneration(self) -> typing.Self:
        return self

    # Tick:
    def _internal_tick(self) -> typing.Self:
        """You must modify this."""
        return self

    def tick(self) -> UIElement:
        # NOTE: Do we need to `regenerate the item?`
        if self._need_regeneration:
            self._internal_regeneration()
        self._internal_tick()
        for key in self._children:
            self._children[key].tick()
        return self

    # Draw:
    def _internal_draw(self) -> typing.Self:
        render_at: pygame.Vector2 = self._position.calculate(
            self
                ._parent
                .get_surface()
        )
        render_at.x -= (self._surface.get_width() * self._pivot.x)
        render_at.y -= (self._surface.get_height() * self._pivot.y)
        (
            self
                ._parent
                .get_surface()
                .blit(self._surface, render_at)
        )
        return self

    def draw(self) -> typing.Self:
        self._internal_draw()
        for key in self._children:
            self._children[key].draw()
        return self

    # Get

    def query(
            self,
            path: str,
            separator: str = '.'
    ) -> UIElement:
        current_element: UIElement = self
        path_split: typing.List[str] = path.split(separator)
        for index, key in enumerate(path_split):
            if key in current_element._children:
                current_element = current_element._children[key]
            else:
                raise UIElementInvalidPathError(path, key, index)
        return current_element

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

    def reload(self) -> None:
        self._need_regeneration = True
        for child in self._children:
            self._children[child].reload()