from linehawk.core.services.base_service import BaseService
class RuntimeService(BaseService):
    """Contains `tick` and `draw` counters."""
    running: bool
    tick_counter: int
    tick_rate: int
    draw_counter: int
    draw_rate: int

    def __init__(self) -> None:
        super().__init__("RuntimeService")

        # Initialize the content:
        self.running = True
        self.tick_counter = 0
        self.tick_rate = 60
        self.draw_counter = 0
        self.draw_rate = 60

    def inc_tick_counter(self) -> RuntimeService:
        self.tick_counter += 1
        return self

    def inc_draw_counter(self) -> RuntimeService:
        self.draw_counter += 1
        return self