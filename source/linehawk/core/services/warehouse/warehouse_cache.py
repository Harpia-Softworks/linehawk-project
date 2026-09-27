WAREHOUSE_CACHE_TYPE_EMPTY: int                                             = 0
WAREHOUSE_CACHE_TYPE_FONT: int                                              = 1
WAREHOUSE_CACHE_TYPE_IMAGE: int                                             = 2


from linehawk.linehawk_error import LineHawkError
import enum
import typing
import pygame

class WarehouseCacheType(enum.IntEnum):
    EMPTY = 0
    FONT = 1
    IMAGE = 2

class WarehouseCacheError(LineHawkError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class WarehouseCacheImpossibleConvertToError(WarehouseCacheError):
    wanted: WarehouseCacheType
    but_is: WarehouseCacheType
    def __init__(
            self,
            wanted: WarehouseCacheType,
            but_is: WarehouseCacheType
    ) -> None:
        self.wanted = wanted
        self.but_is = but_is
        super().__init__(f'Wanted to be: {self.wanted}, but is: {self.but_is}')

class WarehouseCache:
    __type: WarehouseCacheType
    __holding: object

    def __init__(self, type: WarehouseCacheType, content: object) -> None:
        self.__type = type
        self.__holding = content

    def get_tag(self) -> str:
        tag: str
        match self.__type:
            case WarehouseCacheType.EMPTY:
                tag = "empty"
            case WarehouseCacheType.FONT:
                tag = "font"
            case WarehouseCacheType.IMAGE:
                tag = "image"
        return tag

    def get_type(self) -> WarehouseCacheType:
        return self.__type

    def get_font(self) -> pygame.font.Font:
        if self.__type == WarehouseCacheType.FONT:
            return typing.cast(pygame.font.Font, self.__holding)
        else:
            raise WarehouseCacheImpossibleConvertToError(
                WarehouseCacheType.FONT,
                self.__type
            )

    def get_image(self) -> pygame.Surface:
        if self.__type == WarehouseCacheType.IMAGE:
            return typing.cast(pygame.Surface, self.__holding)
        else:
            raise WarehouseCacheImpossibleConvertToError(
                WarehouseCacheType.IMAGE,
                self.__type
            )