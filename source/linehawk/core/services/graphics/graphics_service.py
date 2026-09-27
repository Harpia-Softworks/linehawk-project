from linehawk.graphics.window import Window
from linehawk.core.services.base_service import BaseService

class GraphicsService(BaseService):
    """Contains the window and more graphics content."""
    window: Window
    def __init__(self) -> None:
        super().__init__("GraphicsService")

        # Initialize the content:
        self.window = Window()