from linehawk.core.services.graphics.graphics_service import GraphicsService
from linehawk.core.services.base_service import BaseService
from linehawk.core.services.warehouse.warehouse_cache import *
from linehawk.linehawk_error import LineHawkError

import typing
import json
import enum

class WarehouseServiceError(LineHawkError):
    message: str
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

class WarehouseServiceAlreadyPresentPackageError(WarehouseServiceError):
    bad_key: str
    def __init__(self, bad_key: str) -> None:
        self.bad_key = bad_key
        super().__init__(f'Already present package: {self.bad_key}')

class WarehouseServiceBadSiteError(WarehouseServiceError):
    site: str
    def __init__(self, site: str) -> None:
        self.site = site
        super().__init__(f'Bad site: {self.site}')

class WarehouseServiceBadFontSiteError(WarehouseServiceError):
    site: str
    def __init__(self, site: str) -> None:
        self.site = site
        super().__init__(f'Invalid font site: {self.site}')

class WarehouseServiceNoPackageFoundError(WarehouseServiceError):
    name: str
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f'No package found: {self.name}')
class WarehouseService(BaseService):
    """Contains loaded surfaces and more."""

    __graphics_service: GraphicsService
    __package: typing.Dict[str, str]
    __cached: typing.Dict[str, WarehouseCache]
    __invalid_texture: pygame.Surface

    def __init__(
            self,
            graphics_service: GraphicsService
    ) -> None:
        super().__init__("WarehouseService")
        # Reference to the `GraphicsService`
        self.__graphics_service = graphics_service

        # The Cache System:
        self.__package = dict()
        self.__cached = dict()

        # This is a `fake texture` defined when the game failed to generate
        # an texture, or using as a mere placeholder.
        INVALID_TEXTURE_WIDTH: int                              = 1024
        INVALID_TEXTURE_HEIGHT: int                             = 1024
        INVALID_TEXTURE_SUBSECTIONS_WIDTH: int                  = 32
        INVALID_TEXTURE_SUBSECTIONS_HEIGHT: int                 = 32
        self.__invalid_texture = pygame.Surface(
            (INVALID_TEXTURE_WIDTH, INVALID_TEXTURE_HEIGHT),
            flags=pygame.SRCALPHA
        )
        self.__invalid_texture.fill((0, 0, 0))
        for yindex in range(
            0,
            (INVALID_TEXTURE_HEIGHT // INVALID_TEXTURE_SUBSECTIONS_HEIGHT) + 1
        ):
            for xindex in range(
                0,
                (INVALID_TEXTURE_WIDTH // INVALID_TEXTURE_SUBSECTIONS_WIDTH) + 1
            ):
                at: int = (
                    (yindex * ((INVALID_TEXTURE_WIDTH // INVALID_TEXTURE_SUBSECTIONS_WIDTH) + 1)) + 
                    xindex
                )
                if at % 2 == 0:
                    continue
                pygame.draw.rect(
                    self.__invalid_texture,
                    (255, 0, 255),
                    (
                        xindex * INVALID_TEXTURE_SUBSECTIONS_WIDTH,
                        yindex * INVALID_TEXTURE_SUBSECTIONS_HEIGHT,
                        INVALID_TEXTURE_SUBSECTIONS_WIDTH,
                        INVALID_TEXTURE_SUBSECTIONS_HEIGHT
                    )
                )

    # xxxxxxxxxxxxxxxx
    # Register Package
    # xxxxxxxxxxxxxxxx

    def register_package(
            self,
            name: str,
            where: str
    ) -> typing.Self:
        if name in self.__package:
            raise WarehouseServiceAlreadyPresentPackageError(name)
        self.__package[name] = where
        return self

    def get_package(self, name: str) -> str:
        if name not in self.__package:
            raise WarehouseServiceNoPackageFoundError(name)
        return self.__package[name]

    # xxxxxxxxx
    # Load Font
    # xxxxxxxxx

    def __load_font(
            self,
            site: str
    ) -> WarehouseCache:
        # Expected Format: root:Path/To/Font.ttf$n, where n is the `size`
        site_split: typing.List[str] = site.split(":")
        if len(site_split) != 2:
            raise WarehouseServiceBadSiteError(site)
        from_package: str = self.get_package(site_split[0])

        # DS: Direction (the file) and Size (The size of the font):
        ds: str = site_split[1]
        ds_split: typing.List[str] = ds.split("$")
        if len(ds_split) != 2:
            raise WarehouseServiceBadFontSiteError(site)
        direction: str = ds_split[0]
        font_size: int
        try:            font_size = int(ds_split[1])
        except:         raise WarehouseServiceBadFontSiteError(site)

        # Finally, load:
        font: pygame.font.Font = pygame.font.Font(
            (from_package + direction),
            font_size
        )
        return WarehouseCache(WarehouseCacheType.FONT, font)

    def get_font(
            self,
            site: str,
            size: int
    ) -> pygame.Font:
        cache_key: str = f'{site}${size}@font'
        if cache_key in self.__cached:
            return self.__cached[cache_key].get_font()
        else:
            acquired_cache: WarehouseCache = self.__load_font(f'{site}${size}')
            self.__cached[cache_key] = acquired_cache
            return acquired_cache.get_font()

    # xxxxxxxxxx
    # Load Image
    # xxxxxxxxxx

    def __load_image(
            self,
            site: str
    ) -> WarehouseCache:
        site_split: typing.List[str] = site.split(":")
        if len(site_split) != 2:
            raise WarehouseServiceBadSiteError(site)
        from_package: str = self.get_package(site_split[0])
        # NOTE: load the image.
        loaded_image: pygame.Surface = pygame.image.load(
            (from_package + site_split[1])
        )
        return WarehouseCache(WarehouseCacheType.IMAGE, loaded_image)

    def load_image(
            self,
            site: str
    ) -> pygame.Surface:
        cache_key: str = f'{site}@image'
        if cache_key in self.__cached:
            return self.__cached[cache_key].get_image()
        else:
            acquired_cache: WarehouseCache = self.__load_image(site)
            self.__cached[cache_key] = acquired_cache
            return acquired_cache.get_image()

    # xxxxxxxxx
    # Load JSON
    # xxxxxxxxx

    def __load_json(
            self,
            site: str
    ) -> WarehouseCache:
        site_split: typing.List[str] = site.split(":")
        if len(site_split) != 2: 
            raise WarehouseServiceBadSiteError(site)
        from_package: str = self.get_package(site_split[0])
        direction: str = site_split[1]

        # Open the File:
        fp = open(from_package + direction, "rb")
        parsed_data = json.load(fp)
        fp.close()

        # Return the cache, finally...
        return WarehouseCache(WarehouseCacheType.JSON, parsed_data)        

    def load_json(
            self,
            site: str
    ) -> typing.Dict[str, typing.Any]:
        cache_key: str = f'{site}@json'
        if cache_key in self.__cached:
            return self.__cached[cache_key].get_json()
        else:
            acquired_cache: WarehouseCache = self.__load_json(site)
            self.__cached[cache_key] = acquired_cache
            return acquired_cache.get_json()

    def get_placeholder_texture(
            self
    ) -> pygame.Surface:
        return self.__invalid_texture

    def tick(self) -> None:
        pass