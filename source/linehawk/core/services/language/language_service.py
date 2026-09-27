from linehawk.core.services.base_service import BaseService
from linehawk.core.services.warehouse.warehouse_service import WarehouseService
import typing

class LanguageService(BaseService):
    """Contains everything related to `language` and the global key system."""
    __warehouse_service: WarehouseService
    __current_language: str

    def __init__(self, warehouse_service: WarehouseService):
        self.__warehouse_service = warehouse_service
        self.__current_language = "Default"

    def format(self, text: str) -> typing.Optional[str]:
        accumulator: str = str()
        index: int = 0
        while index < len(text): 
            current_char: str = text[index]
            if current_char == '§':
                subindex: int = index + 1
                key: str = str()
                while subindex < len(text):
                    s_current_char: str = text[subindex]
                    subindex += 1
                    if s_current_char == '§':
                        break
                    key += s_current_char
                key_content: typing.Optional[str] = self.__get_key(key)
                if key_content:
                    accumulator += key_content
                else:
                    # NOTE: we are NOT ready:
                    return None
                index = subindex
            else:
                accumulator += current_char
                index += 1
        return accumulator
    
    def __get_key(self, key: str) -> typing.Optional[str]:
        maybe_data = (
            self
                .__warehouse_service
                .get_json(
                    ("root:Language/" + self.__current_language + ".json")
                )
        )
        if maybe_data.is_present():
            data = maybe_data.get().get_json()
            data_section = data.get("data", None)
            if data_section:
                return data_section.get(key, "???")
        else:
            # NOTE: in this, the implication is that the file is still loading.
            return None
        return "???"