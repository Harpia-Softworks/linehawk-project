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
    GUIObjectValidKeywords,
    _GUIElementValidKeywordsHalf
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

    # Public:
    name:               typing.Optional[str]

    # Restricted:
    __surface: pygame.Surface
    __root: GUIElement
    __parent: GUIElement
    __children: typing.Dict[str, GUIElement]

    def __init__(
            self,
            type: GUIElementType,
            parent: typing.Optional[GUIElement],
            **kwargs: typing.Unpack[GUIElementValidKeywords]
    ) -> None:
        # Initialize the Super-Class (GUIObject):
        super().__init__(type, **kwargs)

        # Initialize Variables:
        self.__children = dict()

        # `GUIElement` properties:
        self.name = kwargs.get("name")

        if parent:
            self.__parent = parent
            self.__root = self.get_parent().get_root()

            # Initialize the `Surface` here:
            self.__surface = pygame.Surface(
                self
                    .size
                    .calculate(
                        self
                            .get_parent()
                            .get_surface()
                    ),
                flags=pygame.SRCALPHA
            )
        else:
            # Skip the initialization, because we don't have a parent to be
            # referenced to.
            pass

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

    def get_child(self, name: str) -> GUIElement:
        """
        In this element, get an `child` from it.
        ---
        @note You should **NOT** overwrite this function.
        """
        if name in self.__children:
            return self.__children[name]
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

    def get_surface(self) -> pygame.Surface:
        """
        Return the `pygame.Surface` used by the `GUIElement`.
        """
        return self.__surface

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
        self.unmark_redraw()
        return self

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
        for child in self.__children.values():
            child.tick()
        return self

    # xxxxxxxxxxxxxxxx
    # == Draw Epoch ==
    # xxxxxxxxxxxxxxxx

    def _specific_draw(self) -> typing.Self:
        return self

    def __clean_surface(self) -> typing.Self:
        """
        Clean the surface to draw the other elements.
        """
        self.get_surface().fill(
            self
                .get_root()
                .get_theme()
                .get(self.use_style)
                .background_color
        )
        return self

    def _deploy_to_parent_surface(self) -> typing.Self:
        """
        To deploy to parent surface is, to take the `self.__surface` and blit
        on the `self.__parent().get_surface().blit(self.__surface, __position)`
        this is, in last, to transfer the element to the parent. This is done,
        of course after **ALL** the child elements have draw on `this` surface.

        @note You might replace this `method` on `GUIDisplay`.
        """
        final_position: pygame.Vector2 = (
            self
                .position
                .calculate(
                    self
                        .get_surface()
                )
        )
        final_position.x -= (self.get_surface().get_width() * self.pivot.x)
        final_position.y -= (self.get_surface().get_height() * self.pivot.y)

        # NOTE: Here is why this function needs to be removed from the
        # `GUIDisplay`, because `self.get_parent()` in `GUIDisplay` already 
        # return itself, and chained with `self.get_surface()`, it will return
        # the `self.__render_to` `pygame.Surface`, but you see,
        # `self.get_surface()` already returns the `self.__render_to` surface,
        # so it is like, we are drawing `X` on `X`, which makes no sense! So,
        # this function can be replaced on `GUIDisplay`, where
        # `self.get_surface()` and `self.get_parent().get_surface()` is equal.
        (
            self
                .get_parent()
                .get_surface()
                .blit(
                    self.get_surface(),
                    final_position
                )
        )
        return self

    def draw(self) -> typing.Self:
        """
        Draw the internal elements of the `GUIElement`.
        ---

        * @warning DO NOT replace this function, just like `tick()`, you have 
        the *protected* method called `_specific_draw()` you can overwrite to 
        perform specific actions!
        """
        # Start by cleaning the surface:
        self.__clean_surface()
        self._specific_draw()
        
        for child in self.__children.values():
            child.draw()

        # Finish by `deploying` to parent surface:
        self._deploy_to_parent_surface()
        return self