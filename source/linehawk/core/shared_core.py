from linehawk.core.services.graphics.graphics_service import GraphicsService
from linehawk.core.services.warehouse.warehouse_service import WarehouseService
from linehawk.core.services.runtime.runtime_service import RuntimeService
from linehawk.core.services.language.language_service import LanguageService
class SharedCore:
    """Contains all the services."""

    runtime_service: RuntimeService
    graphics_service: GraphicsService
    warehouse_service: WarehouseService
    language_service: LanguageService
    def __init__(self) -> None:
        self.runtime_service = RuntimeService()
        self.graphics_service = GraphicsService()
        self.warehouse_service = WarehouseService(self.graphics_service)
        self.language_service = LanguageService(self.warehouse_service)
