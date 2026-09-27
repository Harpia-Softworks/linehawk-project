import pygame

class UIDim:
    x_scale: float
    x_offset: int
    y_scale: float
    y_offset: int

    def __init__(
            self,
            x_scale: float = 0.0,
            x_offset: int = 0,
            y_scale: float = 0.0,
            y_offset: int = 0
    ) -> None:
        self.x_scale = x_scale
        self.x_offset = x_offset
        self.y_scale = y_scale
        self.y_offset = y_offset

    def calculate(
            self,
            surface: pygame.Surface
    ) -> pygame.Vector2:
        return pygame.Vector2(
            (surface.get_width() * self.x_scale) + self.x_offset,
            (surface.get_height() * self.y_scale) + self.y_offset
        )