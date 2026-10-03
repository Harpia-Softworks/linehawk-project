# 2026 Line Hawk Project by Harpia Softworks & Contribuitors.
# Project is under the license `BSD v2`, read `LICENSE.md` for more information.
import pygame
import typing

class Window:
    surface: pygame.Surface

    def __init__(self) -> None:
        #self.surface = pygame.display.set_mode((640, 480))
        self.surface = pygame.display.set_mode((800, 640))
        pygame.display.set_caption("Line Hawk")

    def at_resize(self, size: typing.Tuple[int, int]) -> typing.Self:
        self.surface = pygame.display.set_mode(size)
        return self