from linehawk.GUI.gui_style import GUIStyle
from linehawk.core.services.warehouse.warehouse_service import WarehouseService
from linehawk.core.services.language.language_service import LanguageService

import typing

class GUIThemeError(BaseException):
    message: str
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class GUIThemeAlreadyDefinedStyleError(GUIThemeError):
    bad_key: str
    def __init__(self, key: str) -> None:
        self.bad_key = key
        super().__init__(f'Already defined theme: {self.bad_key}')

class GUIThemeStyleNotFoundError(GUIThemeError):
    bad_key: str
    def __init__(self, key: str) -> None:
        self.bad_key = key
        super().__init__(f'Style not found theme: {self.bad_key}')

class GUITheme:
    """Contains an variety of `UIStyle` one can choose."""
    _data: typing.Dict[str, 'GUIStyle']
    _warehouse_service: WarehouseService
    _language_service: LanguageService

    def __init__(
            self,
            warehouse_service: WarehouseService,
            language_service: LanguageService
    ) -> None:
        self._data = dict()
        self._warehouse_service = warehouse_service
        self._language_service = language_service

    def get_warehouse_service(self) -> WarehouseService:
        return self._warehouse_service

    def get_language_service(self) -> LanguageService:
        return self._language_service

    def add(self, key: str, style: GUIStyle) -> typing.Self:
        if key in self._data:
            raise GUIThemeAlreadyDefinedStyleError(key)
        self._data[key] = style
        return self

    def get(self, key: str) -> GUIStyle:
        if not key in self._data:
            raise GUIThemeStyleNotFoundError(key)
        return self._data[key]