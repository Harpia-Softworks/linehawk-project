from linehawk.core.shared_core import SharedCore
from linehawk.scene.scene_mode import SceneMode

import pygame
import os

class Engine:
    shared_core: SharedCore
    scene_mode: SceneMode

    def __init__(self) -> None:
        self.shared_core = SharedCore()
        # TODO: This is a hardcoded way to get `.root`, which is not nice.
        (
            self
                .shared_core
                .warehouse_service
                .register_package(
                    "root",
                    os.path.abspath("./root") + os.sep
                )
        )
        self.scene_mode = SceneMode(self.shared_core)

    def tick(self) -> Engine:
        self.scene_mode.tick()
        self.shared_core.runtime_service.inc_tick_counter()
        return self

    def draw(self) -> Engine:
        self.scene_mode.draw()
        self.shared_core.runtime_service.inc_draw_counter()
        return self

    def loop(self) -> None:
        # NOTE: initialize `pygame`
        pygame.init()

        frame_clock: pygame.Clock = pygame.Clock()
        while self.shared_core.runtime_service.running:
            self.tick()
            self.draw()
            frame_clock.tick(self.shared_core.runtime_service.tick_rate)

        # And close:
        pygame.quit()