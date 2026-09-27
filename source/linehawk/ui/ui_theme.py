from linehawk.ui.ui_style import UIStyle
from linehawk.core.services.warehouse.warehouse_service import WarehouseService
from linehawk.core.services.language.language_service import LanguageService

import typing

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

    def add(self, key: str, style: UIStyle) -> typing.Self:
        if key in self._data:
            raise UIThemeAlreadyDefinedStyleError(key)
        self._data[key] = style
        return self

    def get(self, key: str) -> UIStyle:
        if not key in self._data:
            raise UIThemeStyleNotFoundError(key)
        return self._data[key]