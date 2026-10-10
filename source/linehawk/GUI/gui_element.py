from linehawk.GUI.gui_object import *
from linehawk.GUI.gui_error import GUIError
from linehawk.GUI.gui_enums import *
from linehawk.GUI.gui_theme import GUITheme

import typing
import pygame

# Typing Hint:
class _GUIElementValidKeywordsHalf(typing.TypedDict):
    name: typing.NotRequired[str]

class GUIElementValidKeywords(
    GUIObjectValidKeywords, _GUIElementValidKeywordsHalf
): pass

class ChildNotFoundError(GUIError):
    name: str
    full_path: str
    def __init__(self, name: str) -> None:
        self.name = name
        (
            super()
            .__init__(
                f'Child not found: {name}'
            )
        )

class GUIElement(GUIObject):
    """
    Base for all the `GUI` element(s)
    ---

    This is the base for all the GUI elements, like GUITextLabel, GUITextButton
    and even GUIFrame, which contains other elements inside. Every `GUIElement`
    can contain other elements inside, even `GUITextLabel`.
    """
    name:               typing.Optional[str]
    __root:             GUIElement
    __parent:           GUIElement
    _children:          typing.Dict[str, GUIElement]

    def __init__(
            self,
            type: GUIElementType,
            parent: GUIElement,
            **kwargs: typing.Unpack[GUIElementValidKeywords]
    ) -> None:
        super().__init__(type, **kwargs)
        self._children     = dict()
        self.name           = kwargs.get("name")
        self.__parent       = parent
        self.__root         = self.get_parent().get_root()

    def query(self, path: str, sep: str = '.') -> GUIElement:
        """
        Given an path, find an element.
        ---

        @note With an path like, `x.y.z`, find the `z` element, if it doesn't
        exist, then `ChildNotFoundError` might happen.
        """
        path_split: typing.List[str] = path.split(sep)
        current_element: GUIElement = self
        for child_name in path_split:
            current_element = current_element.get_child(child_name)
        return current_element

    def add_child(self, name: str, child: GUIElement) -> typing.Self:
        self._children[name] = child
        return self

    def get_child(self, name: str) -> GUIElement:
        """
        In this element, get an `child` from it.
        ---
        @note You should **NOT** overwrite this function.
        """
        if name in self._children:
            return self._children[name]
        else:
            raise ChildNotFoundError(name)

    def get_theme(self) -> GUITheme:
        """
        Get, from a `GUIDisplay`, the `GUITheme`, but this, should only be 
        implemented by `GUIDisplay`, any other element will trigger an 
        `NotImplementedError` exception, which is fair and good, because
        `this.get_root()` must always return `GUIDisplay` and, if not, then
        some weird bug probably have happened.
        """
        raise NotImplementedError(
            "This function should have been implemented by GUIDisplay"
        )
        
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # root, parent and surface (drawing) and logistics
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    def get_root(self) -> GUIElement:
        """
        Return the `root` of the `GUIElement` (aka. the display).
        ---
        * @note This function `can be` overwriten.
        """
        return self.__root

    def get_parent(self) -> GUIElement:
        """
        Return the `parent` of the `GUIElement`
        ---

        * @note This function `can be` overwriten. `GUIDisplay` for example,
        will not return itself because it is the *TOP* of the hierachy.
        """
        return self.__parent

    # xxxxxxxxxxxx
    # == Redraw ==
    # xxxxxxxxxxxx

    def mark_redraw(self) -> typing.Self:
        """
        Set the `self._need_redraw` as `True` and the GUIElement will redraw next tick.
        ---

        @note This function `SHOULD NOT` be overwriten.
        """
        self._need_redraw = True
        return self

    def unmark_redraw(self) -> typing.Self:
        """
        Set the `self._need_redraw` as `False`, this controls the internal
        `need_redraw` register. As for it, `self._need_redraw` is continuous and
        presistent.
        """
        self._need_redraw = False
        return self

    def _redraw(self) -> typing.Self:
        """
        Redraw the element.
        ---
        To avoid having to render over and over again an mere static text, this
        functions exists to aliviate the `consumption`.

        * @note This function `can be` (or `must be`) overwriten.
        * @note The default implementation of this function is a simple
        `self.unmark_redraw()` and nothing else. This is good for things like
        `GUIDisplay` and `GUIFrame`, because `GUIFrame` is always drawing and
        cleaning, what is called `busy element`.
        """
        return self.unmark_redraw()

    # xxxxxxxxxxxxxxxx
    # == Tick Epoch ==
    # xxxxxxxxxxxxxxxx

    def _specific_tick(self) -> typing.Self:
        return self

    def tick(self) -> typing.Self:
        """
        Tick the internal elements of the `GUIElement`.
        ---
        
        * @warning DO NOT replace this function, instead, replace the protected
        method called `_specific_tick()`, the `tick()` method will handle the 
        most generic things like `_redraw()` and more.
        """
        self._specific_tick()
        if self._need_redraw:
            self._redraw()
        # After _redraw(), do the tick:
        for child in self._children.values():
            child.tick()
        return self

    # xxxxxxxxxxxxxxxx
    # == Draw Epoch ==
    # xxxxxxxxxxxxxxxx

    def _specific_draw(
            self,
            surface: pygame.Surface,
            box: pygame.Rect,
            depth: int
    ) -> typing.Self:
        return self
    
    def draw(
            self,
            surface: pygame.Surface,
            box: pygame.Rect,
            depth: int = 0
    ) -> typing.Self:
        # Can we draw?
        if not self._visible:
            return self
        
        # Calculate the Initial Position on the Screen:
        reference_position: pygame.Vector2 = pygame.Vector2(
            box.x + box.w * self._position.x_scale + self._position.x_offset,
            box.y + box.h * self._position.y_scale + self._position.y_offset
        )

        # Calculate the Size of the Object:
        object_size: pygame.Vector2 = pygame.Vector2(
            box.w * self._size.x_scale + self._size.x_offset,
            box.h * self._size.y_scale + self._size.y_offset
        )

        # Finally, merge the position and the pivot point.
        object_position: pygame.Vector2 = pygame.Vector2(
            reference_position.x - (object_size.x * self._pivot.x),
            reference_position.y - (object_size.y * self._pivot.y)
        )

        # Create `This` object box.
        object_box: pygame.Rect = pygame.Rect(object_position, object_size)
        self._specific_draw(surface, object_box, depth)
        
        # Draw the child inside this box.
        for child in self._children.values():
            child.draw(surface, object_box, depth=depth + 1)
        return self