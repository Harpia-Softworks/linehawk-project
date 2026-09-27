import pygame
import typing

#
# Basic(S)
#

class Window:
    surface: pygame.Surface

    def __init__(self) -> None:
        self.surface = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Line Hawk")

# 
# Service(S)
#

class BaseService:
    _name: str

    def __init__(self, name: str) -> None:
        self._name = name

    def tick(self) -> None:
        pass

    def draw(self) -> None:
        pass

class RuntimeService(BaseService):
    """Contains `tick` and `draw` counters."""
    running: bool
    tick_counter: int
    tick_rate: int
    draw_counter: int
    draw_rate: int

    def __init__(self) -> None:
        super().__init__("RuntimeService")

        # Initialize the content:
        self.running = True
        self.tick_counter = 0
        self.tick_rate = 60
        self.draw_counter = 0
        self.draw_rate = 60

    def inc_tick_counter(self) -> RuntimeService:
        self.tick_counter += 1
        return self

    def inc_draw_counter(self) -> RuntimeService:
        self.draw_counter += 1
        return self

class GraphicsService(BaseService):
    """Contains the window and more graphics content."""

    window: Window

    def __init__(self) -> None:
        super().__init__("GraphicsService")

        # Initialize the content:
        self.window = Window()

class WarehouseService(BaseService):
    """Contains loaded surfaces and more."""

    graphics_service: GraphicsService

    def __init__(self, graphics_service: GraphicsService) -> None:
        super().__init__("WarehouseService")

        # Initialize the content:
        self.graphics_service = graphics_service

#
# Shared Core:
#

class SharedCore:
    """Contains all the services."""

    runtime_service: RuntimeService
    graphics_service: GraphicsService
    warehouse_service: WarehouseService

    def __init__(self) -> None:
        self.runtime_service = RuntimeService()
        self.graphics_service = GraphicsService()
        self.warehouse_service = WarehouseService(self.graphics_service)

#
# UI(s)
#

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

class UIThemeError(BaseException):
    message: str
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class UIThemeAlreadyDefinedStyleError(UIThemeError):
    bad_key: str
    def __init__(self, key: str) -> None:
        self.bad_key = key
        super().__init__(f'Already defined theme: {self.bad_key}')

class UIThemeStyleNotFoundError(UIThemeError):
    bad_key: str
    def __init__(self, key: str) -> None:
        self.bad_key = key
        super().__init__(f'Style not found theme: {self.bad_key}')

class UITheme:
    """Contains an variety of `UIStyle` one can choose."""
    _data: typing.Dict[str, 'UIStyle']
    
    def __init__(self) -> None:
        self._data = dict()

    def add(self, key: str, style: UIStyle) -> typing.Self:
        if key in self._data:
            raise UIThemeAlreadyDefinedStyleError(key)
        self._data[key] = style
        return self

    def get(self, key: str) -> UIStyle:
        if not key in self._data:
            raise UIThemeStyleNotFoundError(key)
        return self._data[key]

class UIDim:
    x_scale: float
    x_offset: int
    y_scale: float
    y_offset: int

    def __init__(
            self,
            x_scale: float = 0.0,
            x_offset: int = 0,
            y_scale: float = 0.0,
            y_offset: int = 0
    ) -> None:
        self.x_scale = x_scale
        self.x_offset = x_offset
        self.y_scale = y_scale
        self.y_offset = y_offset

    def calculate(
            self,
            surface: pygame.Surface
    ) -> pygame.Vector2:
        return pygame.Vector2(
            (surface.get_width() * self.x_scale) + self.x_offset,
            (surface.get_height() * self.y_scale) + self.y_offset
        )

UI_TYPE_FRAME: int                                                          = 0
UI_TYPE_TEXT_LABEL: int                                                     = 1
UI_TYPE_IMAGE_LABEL: int                                                    = 2
UI_TYPE_TEXT_BUTTON: int                                                    = 3
UI_TYPE_IMAGE_BUTTON: int                                                   = 4
UI_TYPE_DISPLAY: int                                                        = 99

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

is_mouse_down: bool = False

class UIFrame(UIElement):
    # Each `UIFrame` has a `container_surface` that represents the surface that
    # can be drawn elements inside.

    def __init__(
            self,
            parent: UIElement,
            **kwargs: typing.Unpack[UIElement.UIElementKwargs]
    ) -> None:
        super().__init__(UI_TYPE_FRAME, parent, **kwargs)

    def _internal_regeneration(self) -> typing.Self:
        self._surface = pygame.Surface(
            self._size.calculate(self._parent.get_surface())
        )
        # Paint:
        self._surface.fill(
            self.get_theme()
                .get(self._using_theme)
                .background_color
        )
        return self

    # This is overwriten to _draw() our `UIFrame`:
    def _internal_draw(self) -> typing.Self:
        render_at: pygame.Vector2 = self._position.calculate(
            self._parent.get_surface()
        )
        render_at.x -= (self._surface.get_width() * self._pivot.x)
        render_at.y -= (self._surface.get_height() * self._pivot.y)
        self._parent.get_surface().blit(self._surface, render_at)
        return self

class UICursor:
    __rectangle: pygame.Rect
    __size: pygame.Vector2
    __display_surface: pygame.Surface
    __surface: pygame.Surface

    def __init__(
            self,
            display_surface: pygame.Surface,
            size: pygame.Vector2 = pygame.Vector2(16, 16)
    ) -> None:
        self.__size = size
        self.__rectangle = pygame.Rect(size, (0, 0))
        self.__display_surface = display_surface

        # TODO: on the future, load some custom cursor.
        self.__surface = pygame.Surface(self.__size)
        self.__surface.fill((255, 255, 255))

    def tick(self) -> typing.Self:
        mouse_at_x, mouse_at_y = pygame.mouse.get_pos()
        self.__rectangle.update((mouse_at_x, mouse_at_y), self.__size)
        return self

    def draw(self) -> typing.Self:
        self.__display_surface.blit(self.__surface, self.__rectangle)
        return self

    def get_rectangle(self) -> pygame.Rect:
        return self.__rectangle
    
class UIDisplay(UIElement):
    # All the `UIDisplay` has a `root` content.
    _root: UIFrame
    __display_surface: pygame.Surface
    __theme: UITheme
    __cursor: UICursor

    def __init__(self, display_surface: pygame.Surface, theme: UITheme) -> None:
        super().__init__(UI_TYPE_DISPLAY, self)
        self.__display_surface = display_surface
        self.__theme = theme
        self.__cursor = UICursor(self.__display_surface)

        # NOTE: The `_root` base frame is always on window:
        self._root = UIFrame(self)
        self._root.set_size(UIDim(1, 0, 1, 0))
        self._root.set_position(UIDim(0, 0, 0, 0))
        self._root.set_pivot(pygame.Vector2(0, 0))

    # NOTE: we gotta modify this:
    def get_surface(self) -> pygame.Surface:
        return self.__display_surface

    # Bounding Box:
    def get_absolute_position(self) -> pygame.Vector2:
        # NOTE: For the display, we don't do this:
        return pygame.Vector2(0, 0)

    # Tick:
    def _internal_tick(self) -> typing.Self:
        # NOTE: Update the `cursor` position, the `cursor` is always the first
        # to be updated on the `UIDisplay`!
        self.__cursor.tick()
        self._root.tick()
        return self

    # Draw:

    def _internal_draw(self) -> typing.Self:
        self._root.draw()

        # NOTE: Draw the `cursor`, the `cursor` is always the LAST to be 
        # drawn, so nothing stays in the way of the cursor.
        self.__cursor.draw()
        return self

    def get_theme(self) -> UITheme:
        # Eventually, all roads must lead here.
        return self.__theme

    # Redirect to `root`:
    def add_child(self, name: str, child: UIElement) -> typing.Self:
        self._root.add_child(name, child)
        return self

    def get_child(self, name: str) -> UIElement:
        return self._root.get_child(name)

    # Base Iteractions:
    def mouse_down(self) -> None:
        hit: typing.Optional[UIElement] = self._root.get_collision(
            self.__cursor.get_rectangle()
        )
        if hit is not None:
            hit.react_click()

    def mouse_up(self) -> None:
        # TODO: implement this.
        return

#
# Scene(s)
#

class SceneMode:
    shared_core: SharedCore
    ui_display: UIDisplay

    def __init__(self, shared_core: SharedCore) -> None:
        self.shared_core = shared_core

        # TODO: On the future, load this from `root:Theme.json` at
        # `WarehouseService` trigger.
        theme: UITheme = (
            UITheme()
            .add(
                "default",
                UIStyle(
                    background_color=pygame.Color(0, 0, 0, 0)
                )
            )
            .add(
                "alternate",
                UIStyle(
                    background_color=pygame.Color(10, 20, 30)
                )
            )
            .add(
                "last",
                UIStyle(
                    background_color=pygame.Color(30, 40, 50)
                )
            )
        )

        self.ui_display = UIDisplay( 
            shared_core.graphics_service.window.surface,
            theme
        )
        
        box_0: UIFrame = UIFrame(
            self.ui_display,
            size=UIDim(0.5, 0, 0.5, 0),
            use_theme="last",
            on_click=lambda k: print("hey")
        )

        box_1: UIFrame = UIFrame( 
            box_0,
            size=UIDim(0.5, 0, 0.5, 0),
            position=UIDim(0.25, 0, 0.25, 0),
            use_theme="alternate",
            on_click=lambda k: print("nope")
        )

        self.ui_display.add_child("box_0", box_0)
        box_0.add_child("box_1", box_1)

    def perform_event(self, event: pygame.Event) -> None:
        match event.type:
            case pygame.QUIT:
                self.shared_core.runtime_service.running = False
            # NOTE: Those are `UI events`.
            case pygame.MOUSEBUTTONDOWN:
                self.ui_display.mouse_down()
            case pygame.MOUSEBUTTONUP:
                self.ui_display.mouse_up()
            case _:
                print(f'Discarding event = {repr(event)}')

    def tick(self) -> SceneMode:
        # The event system:
        grabbed_events: typing.List[pygame.Event] = pygame.event.get()
        for event in grabbed_events:
            self.perform_event(event)

        # Update the UI:
        self.ui_display.tick()
        return self

    def draw(self) -> SceneMode:
        self.shared_core.graphics_service.window.surface.fill((255, 255, 255))

        # Draw the UI:
        self.ui_display.draw()

        pygame.display.update()
        return self

#
# Engine
#

class Engine:
    shared_core: SharedCore
    scene_mode: SceneMode

    def __init__(self) -> None:
        self.shared_core = SharedCore()
        self.scene_mode = SceneMode(self.shared_core)

    def tick(self) -> Engine:
        self.scene_mode.tick()
        self.shared_core.runtime_service.inc_tick_counter()
        return self

    def draw(self) -> Engine:
        self.scene_mode.draw()
        self.shared_core.runtime_service.inc_draw_counter()
        return self

    def loop(self) -> None:
        frame_clock: pygame.Clock = pygame.Clock()
        while self.shared_core.runtime_service.running:
            self.tick()
            self.draw()
            frame_clock.tick(self.shared_core.runtime_service.tick_rate)

class App:
    engine: Engine

    def __init__(self) -> None:
        self.engine = Engine()

    def run(self) -> App:
        self.engine.loop()
        return self

#
# Main
#

def main() -> int:
    a: App = App()
    a.run()
    return 0

if __name__ == '__main__':
    print(f"Executing as `Main`")
    exit( main() )