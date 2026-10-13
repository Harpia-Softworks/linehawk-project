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
    __until: int = 1000000
    __counter: int = 0
    __threshold: int = 60 * 2

    # This is put to the simulation:
    __collisions: int = 0
    __line_length: int 
    __line_half: float
    __parallel_slots: int

    def __init__(
            self,
            shared_core: SharedCore,
            ui_controller: UIController
    ) -> None:
        self.__collisions = 0
        self.__line_length = 128
        self.__line_half = self.__line_length / 2
        self.__parallel_slots = 5
        
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

    # NOTE: This is important wrapper!
    def __get_random(self) -> float:
        return random.random()

    def start(self) -> typing.Self:
        self.__output_surface.fill((0, 0, 0, 0))
        self.__state = SimulatorState.RUNNING
        self.__counter = 0
        self.__collisions = 0
        return self

    def __idle(self) -> None:
        # Not much to do when idle.
        pass

    def __generate_line(self) -> None:
        # Contains the `selected_angle', we use `2*self.__get_random()-1`
        # because remember that, the `0<=self.__get_random()<=1`, so we double
        # the amount of numbers and then, remove one, this makes our $x$ be 
        # around: $-1<=x<=1$ allowing for backwards rotation.
        angle: float = (2 * self.__get_random() - 1) * (math.pi / 2)
        base: float = math.cos(angle)

        # The distance between the tip to the top:
        distance: float = self.__get_random()

        # Collision is when this happens:
        color: typing.Tuple[int, int, int]
        if base >= distance:
            color = (255, 0, 0)
            self.__collisions += 1
        else:
            color = (255, 255, 255)

        # Select an LINE to draw:
        
        # HACK: I am lazy to fix this, but consider that the center is unique:
        line_side: int = -1 if self.__get_random() >= 0.5 else 1
        select_line: int = math.floor(self.__get_random() * (self.__parallel_slots) ) * line_side
        height: int = math.floor(self.__get_random() * self.__output_surface.get_height() )

        BASE_DRAW: float = (
            (self.__output_surface.get_width() / 2) +
            (select_line * self.__line_length)
        )
        side: int = -1 if self.__get_random() >= 0.5 else 1

        # Fix the `Camera`:
        cam_x: float = BASE_DRAW + (distance * self.__line_half * side)
        cam_y: float = height
        dis_x: float = base * self.__line_half
        dis_y: float = math.sin(angle) * self.__line_half

        # Finally, draw:
        pygame.draw.line(
            self.__output_surface,
            color,
            (
                cam_x - dis_x,
                cam_y - dis_y
            ),
            (
                cam_x + dis_x,
                cam_y + dis_y
            )
        )

    def __running(self) -> None:
        if (self.__counter >= self.__until):
            self.__state = SimulatorState.IDLE
            return
        
        if (self.__counter % self.__threshold) == 0:
            # DO the blending (fade-out display):
            (
                self
                    .__output_surface
                    .blit(self.__blending_surface)
            )

            # Draw the line we are simulating:
            pygame.draw.line(
                self.__output_surface,
                (255, 0, 255),
                (
                    (self.__output_surface.get_width() / 2), 0
                ),
                (
                    (self.__output_surface.get_width() / 2),
                    self.__output_surface.get_height()
                )
            )
            for index in range(1, self.__parallel_slots):
                pygame.draw.line( 
                    self.__output_surface,
                    (255, 255, 255),
                    (
                        (self.__output_surface.get_width() / 2) - (index * self.__line_length),
                        0
                    ),
                    (
                        (self.__output_surface.get_width() / 2) - (index * self.__line_length),
                        self.__output_surface.get_height()
                    )
                )
                pygame.draw.line( 
                    self.__output_surface,
                    (255, 255, 255),
                    (
                        (self.__output_surface.get_width() / 2) + (index * self.__line_length),
                        0
                    ),
                    (
                        (self.__output_surface.get_width() / 2) + (index * self.__line_length),
                        self.__output_surface.get_height()
                    )
                )
        # Generate ONE line.
        self.__generate_line()

        # Update the Text:
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