from linehawk.core.shared_core import SharedCore
from linehawk.scene.controllers.ui_controller import UIController

import pygame
import typing
import enum
import random
import math

class SimulatorState(enum.IntEnum):
    IDLE = 0
    RUNNING = 1

class Simulator:
    __ui_controller: UIController

    __output_surface: pygame.Surface
    __blending_surface: pygame.Surface
    __shared_core: SharedCore
    __state: SimulatorState
    __each_tick: int = 60
    __until: int = 100000
    __counter: int = 0
    __threshold: int = 60 * 2

    # This is put to the simulation:
    __needle_length: int = 1
    __collisions: int = 0

    def __init__(
            self,
            shared_core: SharedCore,
            ui_controller: UIController
    ) -> None:
        self.__ui_controller = ui_controller
        self.__shared_core = shared_core
        self.__state = SimulatorState.IDLE

        # The output surface is the final output of the game.
        self.__output_surface = pygame.Surface(
            shared_core
                .graphics_service
                .window
                .get_surface()
                .get_size()
        ).convert_alpha()
        self.__output_surface.fill((0, 0, 0, 0))

        # The `blending_surface` is just a fancy name for a big texture that
        # will be drawn on the top of the `__output_surface` every once a 
        # while to clean the screen.
        self.__blending_surface = pygame.Surface(
            self
                .__output_surface
                .get_size()
        ).convert_alpha()
        self.__blending_surface.fill((0, 0, 0, 50))

    def start(self) -> typing.Self:
        self.__output_surface.fill((0, 0, 0, 0)) 
        self.__state = SimulatorState.RUNNING
        self.__counter = 0
        self.__collisions = 0
        return self

    def __idle(self) -> None:
        # Not much to do when idle.
        pass

    def __running(self) -> None:
        if (self.__counter >= self.__until):
            self.__state = SimulatorState.IDLE
            return

        if (self.__counter % self.__threshold) == 0:
            self.__output_surface.blit(self.__blending_surface)

        # Simulate the Buffon-Laplace Problem Here:        

        # Draw an stick, our simulation requires this.
        pygame.draw.line(
            self.__output_surface,
            (
                int(random.random() * 255),
                int(random.random() * 255),
                int(random.random() * 255),
                255
            ),
            (
                random.random() * self.__output_surface.get_width(),
                random.random() * self.__output_surface.get_height()
            ),
            (
                random.random() * self.__output_surface.get_width(),
                random.random() * self.__output_surface.get_height()
            )
        )

        # update the text:
        maybe_main = self.__ui_controller.get("main")
        if maybe_main:
            (
                maybe_main
                    .query("container.LeftBar.CounterText")
                    .set_text("Counter: " + str(self.__counter))
            )

        self.__counter += 1

    def tick(self) -> None:
        match self.__state:
            case SimulatorState.IDLE:
                self.__idle()
            case SimulatorState.RUNNING:
                for _ in range(0, self.__each_tick):
                    self.__running()

    def draw(self) -> None:
        (
            self
                .__shared_core
                .graphics_service
                .window
                .get_surface()
                .blit(self.__output_surface)
        )