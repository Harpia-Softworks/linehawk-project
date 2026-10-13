# 2026 Line Hawk Project by Harpia Softworks & Contribuitors.
# Project is under the license `BSD v2`, read `LICENSE.md` for more information.
import pygame
import typing

class Window:
    __window_surface: pygame.Surface
    __surface: pygame.Surface

    def __init__(self) -> None:
        #self.surface = pygame.display.set_mode((640, 480))
        #self.__window_surface = pygame.display.set_mode((800, 640))
        self.__window_surface = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Line Hawk")

        # Initialize the Final:
        self.__surface = pygame.Surface(
            self.__window_surface.get_size(),
            flags=pygame.SRCALPHA
        )

    def get_surface(self) -> pygame.Surface:
        return self.__surface

    def deploy_surface(self) -> typing.Self:
        """
        Using the `self.__surface`, deploy on the window the surface used.
        """
        self.__window_surface.blit(self.__surface, (0, 0))
        pygame.display.update()
        return self