from linehawk.ui.ui_display import UIDisplay
from linehawk.ui.ui_theme import UITheme
from linehawk.ui.ui_style import UIStyle
from linehawk.ui.ui_frame import UIFrame
from linehawk.ui.ui_dim import UIDim
from linehawk.ui.ui_text_label import UITextLabel

from linehawk.core.shared_core import SharedCore
import pygame
import typing

class SceneMode:
    shared_core: SharedCore
    ui_display: UIDisplay

    def __init__(self, shared_core: SharedCore) -> None:
        self.shared_core = shared_core

        # TODO: On the future, load this from `root:Theme.json` at
        # `WarehouseService` trigger.
        theme: UITheme = (
            UITheme(
                self.shared_core.warehouse_service,
                self.shared_core.language_service
            )
            .add(
                "default",
                UIStyle(
                    background_color=pygame.Color(0, 0, 0, 0)
                )
            )
            .add(
                "alternate",
                UIStyle(
                    background_color=pygame.Color(10, 20, 30)
                )
            )
            .add(
                "last",
                UIStyle(
                    background_color=pygame.Color(30, 40, 50)
                )
            )
        )

        self.ui_display = UIDisplay( 
            shared_core.graphics_service.window.surface,
            theme
        )
        
        box_0: UIFrame = UIFrame(
            self.ui_display,
            size=UIDim(0.5, 0, 0.5, 0),
            use_theme="last",
            on_click=lambda k: print("hey")
        )

        box_1: UIFrame = UIFrame( 
            box_0,
            size=UIDim(0.5, 0, 0.5, 0),
            position=UIDim(0.25, 0, 0.25, 0),
            use_theme="alternate",
            on_click=lambda k: print("nope")
        )
        text_0: UITextLabel = UITextLabel(
            box_0,
            size=UIDim(0.25, 0, 0.25, 0),
            position=UIDim(0.5, 0, 0.2, 0),
            use_theme="default"
        )
        text_0.set_text("§lh.internal.ui_design.main::container.text-main§")
        self.ui_display.add_child("box_0", box_0)
        box_0.add_child("box_1", box_1)
        box_0.add_child("text_0", text_0)

    def perform_event(self, event: pygame.Event) -> None:
        match event.type:
            case pygame.QUIT:
                self.shared_core.runtime_service.running = False
            # NOTE: Those are `UI events`.
            case pygame.MOUSEBUTTONDOWN:
                self.ui_display.mouse_down()
            case pygame.MOUSEBUTTONUP:
                self.ui_display.mouse_up()
            case _:
                print(f'Discarding event = {repr(event)}')

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
        self.ui_display.tick()
        return self

    def draw(self) -> SceneMode:
        self.shared_core.graphics_service.window.surface.fill((255, 255, 255))

        # Draw the UI:
        self.ui_display.draw()

        # Draw the Services:
        self.shared_core.runtime_service.draw()
        self.shared_core.graphics_service.draw()
        self.shared_core.warehouse_service.draw()

        pygame.display.update()
        return self