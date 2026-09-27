from linehawk.core.services.warehouse.warehouse_cache import WarehouseCache
from source.linehawk.linehawk_error import LineHawkError
import typing

class WarehousePromiseError(LineHawkError):
    promise: WarehousePromise
    def __init__(self, promise: WarehousePromise, *args: object) -> None:
        self.promise = promise
        super().__init__(*args)

class WarehousePromiseExpectedToBePresentError(WarehousePromiseError):
    def __init__(self, promise: WarehousePromise) -> None:
        super().__init__(promise, f'Promise was expected to be ready')

T = typing.TypeVar('T')

class WarehousePromise:
    __cache: typing.Optional[WarehouseCache]
    __tag: str
    __present: bool
    def __init__(
            self,
            present: bool,
            tag: str,
            cache: typing.Optional[WarehouseCache] = None
    ) -> None:
        self.__present = present
        self.__tag = tag
        self.__cache = cache

    def get_tag(self) -> str:
        return self.__tag

    def expect(self) -> typing.Self:
        if not self.__present:
            raise WarehousePromiseExpectedToBePresentError(self)
        return self

    def with_cache(self, k: typing.Callable[[WarehouseCache], T]) -> T:
        if (not self.__present) or (self.__cache is None):
            raise WarehousePromiseExpectedToBePresentError(self)
        return k(self.__cache)

    def get(self) -> WarehouseCache:
        if (not self.__present) or (self.__cache is None):
            raise WarehousePromiseExpectedToBePresentError(self)
        return self.__cache

    def is_present(self) -> bool:
        return self.__present