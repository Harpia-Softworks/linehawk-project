from linehawk.core.services.graphics.graphics_service import GraphicsService
from linehawk.core.services.warehouse.warehouse_service import WarehouseService
from linehawk.core.services.runtime.runtime_service import RuntimeService

class SharedCore:
    """Contains all the services."""

    runtime_service: RuntimeService
    graphics_service: GraphicsService
    warehouse_service: WarehouseService
    def __init__(self) -> None:
        self.runtime_service = RuntimeService()
        self.graphics_service = GraphicsService()
        self.warehouse_service = WarehouseService(self.graphics_service)
