from linehawk.ui.ui_display import UIDisplay
from linehawk.ui.ui_frame import UIFrame
from linehawk.ui.ui_text_label import UITextLabel
from linehawk.ui.ui_text_button import UITextButton
from linehawk.ui.ui_theme import UITheme
from linehawk.ui.ui_style import UIStyle
from linehawk.ui.ui_element import UIElement
from linehawk.ui.ui_dim import UIDim
from linehawk.core.shared_core import SharedCore
from linehawk.core.services.warehouse.warehouse_promise import WarehousePromise
from linehawk.linehawk_error import LineHawkError

import typing
import pygame

class _UIControllerLoadRequest:
    site: str
    name: str
    def __init__(self, site: str, name: str) -> None:
        self.site = site
        self.name = name

class UIControllerError(LineHawkError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UIControllerRecipeFileLacksThemeError(UIControllerError):
    site: str
    def __init__(self, site: str) -> None:
        self.site = site
        super().__init__(f'Missing /theme/ key in: {site}')

class UIControllerStyleRawConverterError(UIControllerError):
    raw: object
    def __init__(self, raw: object, message: str) -> None: 
        self.raw = raw
        super().__init__(message)

class UIControllerNoUIElementOfTypeError(UIControllerError):
    bad_type: str
    def __init__(self, bad_type: str) -> None:
        self.bad_type = bad_type
        super().__init__(f'No element of type: {self.bad_type}')

class UIControllerElementPropertyConverterError(UIControllerError):
    raw: object
    def __init__(self, raw: object, message: str) -> None: 
        self.raw = raw
        super().__init__(message)

class UIControllerNoDisplayFoundError(UIControllerError):
    bad_name: str
    def __init__(self, bad_name: str) -> None:
        self.bad_name = bad_name
        super().__init__(f'No display named: {self.bad_name}')

class UIController:
    __displays: typing.Dict[str, UIDisplay]
    __requests: typing.List[_UIControllerLoadRequest]
    __shared_core: SharedCore
    __output_surface: pygame.Surface

    # NOTE: This is the conversion table (loaded later).
    __style_field_conversion_table: typing.Dict[
        str,
        typing.Callable[[typing.Any], typing.Any]
    ]

    def __style_load_color3_4(
            self,
            raw: typing.Any
    ) -> pygame.Color:
        if isinstance(raw, list):
            raw = typing.cast(typing.List[int], raw)
            if len(raw) < 3 or len(raw) > 4:
                raise UIControllerStyleRawConverterError(
                    raw,
                    "Expected Color4/Color3"
                )
            else:
                return pygame.Color(raw[0], raw[1], raw[2], raw[3])
        else:
            raise UIControllerStyleRawConverterError(
                raw,
                "Expected Color4/Color3"
            )

    def __style_load_str(
            self,
            raw: typing.Any
    ) -> str:
        if isinstance(raw, str):
            return raw
        else:
            raise UIControllerStyleRawConverterError(
                raw,
                "Expected str"
            )

    def __style_load_int(
            self,
            raw: typing.Any
    ) -> int:
        if isinstance(raw, int):
            return raw
        else:
            raise UIControllerStyleRawConverterError(
                raw,
                "Expected int"
            )

    __element_property_conversion_table: typing.Dict[
        str,
        typing.Callable[[typing.Any], typing.Any]
    ]

    def __element_property_load_ui_dim(
            self,
            raw: typing.Any
    ) -> UIDim:
        if isinstance(raw, list):
            raw = typing.cast(typing.List[typing.Union[int, float]], raw)
            if len(raw) != 4:
                raise UIControllerElementPropertyConverterError(
                    raw,
                    "Expected UIDim"
                )
            else:
                return UIDim(raw[0], raw[1], raw[2], raw[3])
        else:
            raise UIControllerElementPropertyConverterError(
                raw,
                "Expected UIDim"
            )

    def __element_property_load_vec2(
            self,
            raw: typing.Any
    ) -> pygame.Vector2:
        if isinstance(raw, list):
            raw = typing.cast(typing.List[typing.Union[int, float]], raw)
            if len(raw) != 2:
                raise UIControllerElementPropertyConverterError(
                    raw,
                    "Expected Vector2"
                )
            else:
                return pygame.Vector2(raw[0], raw[1])
        else:
            raise UIControllerElementPropertyConverterError(
                raw,
                "Expected Vector2"
            )

    def __element_property_load_str(
            self,
            raw: typing.Any
    ) -> str:
        if isinstance(raw, str):
            return raw
        else:
            raise UIControllerElementPropertyConverterError(
                raw,
                "Expected str"
            )


    def __init__(self, shared_core: SharedCore) -> None:
        self.__displays = dict()
        self.__requests = list()
        self.__shared_core = shared_core

        # Generate the top surface:
        self.__output_surface = pygame.Surface(
            self
                .__shared_core
                .graphics_service
                .window
                .surface
                .get_size()
        ).convert_alpha()

        # Load Conversion Tables:
        self.__style_field_conversion_table = {
            'background_color': self.__style_load_color3_4,
            'foreground_color': self.__style_load_color3_4,
            'font': self.__style_load_str,
            'font_size': self.__style_load_int
        }
        self.__element_property_conversion_table = {
            'size': self.__element_property_load_ui_dim,
            'position': self.__element_property_load_ui_dim,
            'pivot': self.__element_property_load_vec2,
            'use_style': self.__element_property_load_str,
            'text': self.__element_property_load_str
        }

    def load(self, site: str, name: str) -> typing.Self:
        # Begin the construction, we first need the content:
        self.__requests.append(_UIControllerLoadRequest(site, name))
        return self

    def __build_style(
            self,
            field: typing.Dict[str, typing.Any]
    ) -> UIStyle:
        valid_entries: typing.Dict[str, typing.Any] = dict()
        for key in field:
            if key in self.__style_field_conversion_table:
                valid_entries[key] = (
                    self.__style_field_conversion_table[key](field[key])
                )
        return UIStyle(**valid_entries)

    def __build_theme(
            self,
            theme_site: str
    ) -> typing.Optional[UITheme]:
        # Again, either our theme will be already there on the cache or not,
        # since everything is a promise from the `warehouse`, we can't rely
        # on always getting things nicely.
        maybe_theme_recipe: WarehousePromise = (
            self.__shared_core.warehouse_service.get_json(theme_site)
        )
        if not maybe_theme_recipe.is_present():
            return None

        # When present, we unpack the content to the **kwargs:
        theme_recipe: typing.Dict[str, typing.Any] = (
            maybe_theme_recipe
                .get()
                .get_json()
        )

        generated_theme: UITheme = UITheme(
            self.__shared_core.warehouse_service,
            self.__shared_core.language_service
        )

        # TODO: Make nicer errors from here ;-)
        theme_data: typing.Dict[str, typing.Any] = theme_recipe["data"]
        for key in theme_data:
            field: typing.Dict[str, typing.Any] = theme_data[key]
            generated_theme.add(key, self.__build_style(field))
        return generated_theme

    def __construct(
            self,
            request: _UIControllerLoadRequest
    ) -> typing.Optional[UIDisplay]:
        maybe_recipe: WarehousePromise = (
            self
                .__shared_core
                .warehouse_service
                .get_json(request.site)
        )

        # Then, we can't really build the UI:
        if not maybe_recipe.is_present():
            return None

        # Recipe loaded, we can start to build the content:
        recipe = maybe_recipe.get().get_json()
        if not "theme" in recipe:
            raise UIControllerRecipeFileLacksThemeError(request.site)

        # Load the `Theme`:
        use_theme: str = recipe["theme"]
        maybe_theme: typing.Optional[UITheme] = self.__build_theme(use_theme)

        # Not loaded the theme? Can't have it.
        if not maybe_theme:
            return None

        # The construction is done using recursion, which is easy.
        def build(
                element_recipe: typing.Dict[str, typing.Any],
                parent: UIElement
        ) -> None:
            # Contains the type and the name:
            element_type: str = element_recipe["type"]
            element_name: str = element_recipe["name"]

            # This is where the properties are stored.
            element_properties: typing.Dict[str, typing.Any] = (
                element_recipe["properties"]
            )

            # Decode:
            valid_properties: typing.Dict[str, typing.Any] = dict()
            for property_name in element_properties:
                if property_name in self.__element_property_conversion_table:
                    valid_properties[property_name] = (
                        self.__element_property_conversion_table[property_name](
                            element_properties[property_name]
                        )
                    )

            # Construct the element:
            element: UIElement
            match element_type:
                case "frame":
                    element = UIFrame(parent, **valid_properties)
                case "text_label":
                    element = UITextLabel(parent, **valid_properties)
                case "text_button":
                    element = UITextButton(parent, **valid_properties)
                case _:
                    raise UIControllerNoUIElementOfTypeError(element_type)
            parent.add_child(element_name, element)

            # Start to build the `contains`:
            element_contains: typing.List[typing.Dict[str, typing.Any]] = (
                element_recipe["contains"]
            )
            for inside_recipe in element_contains:
                build(inside_recipe, element)

        # Build for the `display`:
        base_display: UIDisplay = UIDisplay(self.__output_surface, maybe_theme)
        build(typing.cast(typing.Dict[str, typing.Any], recipe["root"]), base_display)
        return base_display

    def get(self, name: str) -> typing.Optional[UIDisplay]:
        """
        The `.get` is used to test if the display is present, for direct error,
        you should try: `.with_display()`
        """
        return self.__displays.get(name)

    def with_display(self, name: str) -> UIDisplay:
        """
        This way of querying a display will result in a crash when the name
        is not found!
        """
        if name in self.__displays:
            return self.__displays[name]
        else:
            raise UIControllerNoDisplayFoundError(name)

    def tick(self) -> typing.Self:
        quota: int = len(self.__requests)
        for _ in range(0, quota):
            # Do we have something to build?
            if len(self.__requests) <= 0:
                break

            # Pop from the Queue:
            request: _UIControllerLoadRequest = self.__requests.pop(0)
            maybe_display: typing.Optional[UIDisplay] = self.__construct(
                request
            )

            # NOTE: Some scenarios, the loading might yield, so we don't do
            # anything.
            if maybe_display is None:
                self.__requests.append(request)
            else:
                self.__displays[request.name] = maybe_display

        # Post-Build:
        # TODO: sort the display(s) here:
        for name in self.__displays:
            self.__displays[name].tick()
        return self

    def draw(self) -> typing.Self:
        self.__output_surface.fill((0, 0, 0, 0))

        for name in self.__displays:
            self.__displays[name].draw()
        (
            self
                .__shared_core
                .graphics_service
                .window
                .surface
                .blit(self.__output_surface, (0, 0))
        )
        return self
    
    # Events:
    def game_viewport_resize(self, new_size: pygame.Vector2) -> None:
        # Sets everything to be spawned again.
        new_ui_viewport: pygame.Surface = (
            pygame
                .Surface(new_size)
                .convert_alpha()
        )
        for display in self.__displays:
            (
                self.__displays[display]
                .switch_display_surface(new_ui_viewport)
                .reload()
            )
        self.__output_surface = new_ui_viewport

    def mouse_down(self) -> None:
        # Pass forward:
        for display in self.__displays:
            (
                self.__displays[display]
                .handle_click()
            )