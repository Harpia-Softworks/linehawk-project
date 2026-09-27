from linehawk.core.services.graphics.graphics_service import GraphicsService
from linehawk.core.services.base_service import BaseService
from linehawk.core.services.warehouse.warehouse_cache import *
from linehawk.core.services.warehouse.warehouse_promise import *

import typing
import json
import os

class WarehouseServiceError(BaseException):
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

class _WarehouseRequest:
    type: WarehouseCacheType
    site: str

    def __init__(self, type: WarehouseCacheType, site: str) -> None:
        self.type = type
        self.site = site

class _WarehouseRequestStatus:
    since_tick: int
    def __init__(self, current_tick: int) -> None:
        self.since_tick = current_tick

class WarehouseService(BaseService):
    """Contains loaded surfaces and more."""

    class WarehouseServiceKwargs(typing.TypedDict):
        load_quota: typing.NotRequired[int]

    __graphics_service: GraphicsService
    __package: typing.Dict[str, str]
    __cached: typing.Dict[str, WarehouseCache]

    __requested: typing.List[_WarehouseRequest]
    __quota: int
    __busy: typing.Dict[str, _WarehouseRequestStatus]

    def __init__(
            self,
            graphics_service: GraphicsService,
            **kwargs: typing.Unpack[WarehouseServiceKwargs]
    ) -> None:
        super().__init__("WarehouseService")
        # Reference to the `GraphicsService`
        self.__graphics_service = graphics_service

        # The Cache System:
        self.__package = dict()
        self.__cached = dict()

        # Request System:
        self.__requested = list()
        self.__quota = kwargs.get("load_quota", 5)
        self.__busy = dict()

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

    def get_font(
            self,
            key: str,
            size: int
    ) -> WarehousePromise:
        full_key: str = (key + "$" + str(size))
        key_name: str = full_key + "@font"
        if key_name in self.__cached:
            return WarehousePromise(True, full_key, self.__cached[key_name])
        else:
            if not key_name in self.__busy:
                # Push this content on the `self.__busy`:
                self.__busy[key_name] = _WarehouseRequestStatus(0)
                self.__requested.append(
                    _WarehouseRequest(WarehouseCacheType.FONT, full_key)
                )
            return WarehousePromise(False, full_key, None)

    def get_image(
            self,
            key: str
    ) -> WarehousePromise:
        key_name: str = key + "@image"
        if key_name in self.__cached:
            return WarehousePromise(True, key, self.__cached[key_name])
        else:
            if not key_name in self.__busy:
                self.__busy[key_name] = _WarehouseRequestStatus(0)
                self.__requested.append(
                    _WarehouseRequest(WarehouseCacheType.IMAGE, key)
                )
            return WarehousePromise(False, key, None)

    def get_json(
            self,
            key: str
    ) -> WarehousePromise:
        key_name: str = key + "@json"
        if key_name in self.__cached:
            return WarehousePromise(True, key, self.__cached[key_name])
        else:
            if not key_name in self.__busy:
                # TODO: add timing for the _WarehouseRequestStatus!
                self.__busy[key_name] = _WarehouseRequestStatus(0)
                self.__requested.append(
                    _WarehouseRequest(WarehouseCacheType.JSON, key)
                )
            return WarehousePromise(False, key, None)

    # Tick:
    def __process_font(self, site: str) -> WarehouseCache:
        # Expected Format:
        #   root:Path/To/Font.ttf$n, where n is the `size`
        site_split: typing.List[str] = site.split(":")
        if len(site_split) != 2:
            raise WarehouseServiceBadSiteError(site)

        # Anything, we continue loading:
        from_package: str = self.get_package(site_split[0])

        # DS: Direction (the file) and Size (The size of the font):
        ds: str = site_split[1]
        ds_split: typing.List[str] = ds.split("$")
        if len(ds_split) != 2:
            raise WarehouseServiceBadFontSiteError(site)
        
        direction: str = ds_split[0]
        size: int
        try:            size = int(ds_split[1])
        except:         raise WarehouseServiceBadFontSiteError(site)

        # Finally, load:
        font: pygame.font.Font = pygame.font.Font(
            (from_package + direction),
            size
        )
        return WarehouseCache(WarehouseCacheType.FONT, font)

    def __process_json(self, site: str) -> WarehouseCache:
        site_split: typing.List[str] = site.split(":")
        if len(site_split) != 2: 
            raise WarehouseServiceBadSiteError(site)
        from_package: str = self.get_package(site_split[0])
        direction: str = site_split[1]

        # TODO: Do better here, we can stall more.
        fp = open(from_package + direction, "rb")
        parsed_data = json.load(fp)
        fp.close()

        # Return the cache, finally...
        return WarehouseCache(WarehouseCacheType.JSON, parsed_data)

    def __process(self, request: _WarehouseRequest) -> None:
        cache: typing.Optional[WarehouseCache] = None
        match request.type:
            case WarehouseCacheType.EMPTY:
                return
            case WarehouseCacheType.FONT:
                cache = self.__process_font(request.site)
            case WarehouseCacheType.JSON:
                cache = self.__process_json(request.site)
            case _:
                pass
        # NOTE: Finish by adding it on the `cache`.
        if cache:
            self.__cached[request.site + "@" + cache.get_tag()] = cache

    def __step_assembly_line(self) -> None:
        for _ in range(0, self.__quota):
            if len(self.__requested) > 0:
                emerge: _WarehouseRequest = self.__requested.pop(0)
                self.__process(emerge)
            else:
                break

    def tick(self) -> None:
        self.__step_assembly_line()