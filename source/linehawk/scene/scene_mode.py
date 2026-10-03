from linehawk.scene.jobs.prepare_ui import *
from linehawk.scene.controllers.ui_controller import UIController
from linehawk.scene.controllers.job_scheduler.scheduler import Scheduler
from linehawk.core.shared_core import SharedCore

import pygame
import typing

class SceneMode:
    shared_core: SharedCore
    __scheduler: Scheduler
    __ui_controller: UIController

    def __init__(self, shared_core: SharedCore) -> None:
        self.shared_core = shared_core
        self.__ui_controller = UIController(self.shared_core)

        # Construct the `Scheduler`
        self.__scheduler = Scheduler()
        (
            self.__scheduler.get(
                "LineHawkInternalPrepareUI", 
                PREPARE_UI_TABLE,
                PrepareUI(self.__ui_controller, self.shared_core)
            )
        )

    def perform_event(self, event: pygame.Event) -> None:
        match event.type:
            case pygame.QUIT:
                self.shared_core.runtime_service.running = False
            case pygame.VIDEORESIZE:
                (
                    self
                        .shared_core
                        .graphics_service
                        .window
                        .at_resize(event.size)
                )
                (
                    self
                        .__ui_controller
                        .game_viewport_resize(pygame.Vector2(event.size))
                )
            # NOTE: Those are `UI events`.
            case pygame.MOUSEBUTTONDOWN:
                (
                    self
                        .__ui_controller
                        .mouse_down()
                )
            case pygame.MOUSEBUTTONUP:
                pass
            case _:
                pass

    def tick(self) -> SceneMode:
        # Tick the Services:
        self.shared_core.runtime_service.tick()
        self.shared_core.graphics_service.tick()
        self.shared_core.warehouse_service.tick()
        
        # The event system:
        grabbed_events: typing.List[pygame.Event] = pygame.event.get()
        for event in grabbed_events:
            self.perform_event(event)

        # Update the UI:
        self.__scheduler.tick()
        self.__ui_controller.tick()
        return self

    def draw(self) -> SceneMode:
        self.shared_core.graphics_service.window.surface.fill((0, 0, 0))

        # Draw the UI:
        self.__ui_controller.draw()

        # Draw the Services:
        self.shared_core.runtime_service.draw()
        self.shared_core.graphics_service.draw()
        self.shared_core.warehouse_service.draw()

        pygame.display.update()
        return self