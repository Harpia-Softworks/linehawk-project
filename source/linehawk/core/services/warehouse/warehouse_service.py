from linehawk.core.services.graphics.graphics_service import GraphicsService
from linehawk.core.services.base_service import BaseService

class WarehouseService(BaseService):
    """Contains loaded surfaces and more."""

    graphics_service: GraphicsService
    def __init__(self, graphics_service: GraphicsService) -> None:
        super().__init__("WarehouseService")

        # Initialize the content:
        self.graphics_service = graphics_service
