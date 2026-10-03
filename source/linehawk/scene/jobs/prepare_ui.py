from linehawk.scene.controllers.ui_controller import UIController
from linehawk.scene.controllers.job_scheduler.job import *
from linehawk.core.shared_core import SharedCore

class PrepareUI:
    ui_controller: UIController
    shared_core: SharedCore

    def __init__(
            self,
            ui_controller: UIController,
            shared_core: SharedCore
    ) -> None:
        self.ui_controller = ui_controller
        self.shared_core = shared_core

    @staticmethod
    def load_main(job: Job) -> None:
        (
            job
            .get_userdata(PrepareUI)
            .ui_controller
            .load("root:Resources/UIDesign/Main.json", "main")
        )
        job.advance()

    @staticmethod
    def wait_main_load(job: Job) -> None:
        job.wait(
            (
                job
                    .get_userdata(PrepareUI)
                    .ui_controller
                    .get("main") is not None
            ),
            lambda _: job.advance()
        )

    @staticmethod
    def register_components(job: Job) -> None:
        (
            job
                .get_userdata(PrepareUI)
                .ui_controller
                .with_display("main")
                .query("container.LeftBar.ActionBox.HideLeftBarButton")
                .set_on_click(
                    lambda _: PrepareUI.hide_left_bar_button_action(
                        job
                            .get_userdata(PrepareUI)
                            .ui_controller
                    )
                )
        )
        (
            job
                .get_userdata(PrepareUI)
                .ui_controller
                .with_display("main")
                .query("container.ShowLeftBarButton")
                .set_on_click(
                    lambda _: PrepareUI.show_left_bar_button_action(
                        job
                            .get_userdata(PrepareUI)
                            .ui_controller
                    )
                )
        )
        job.advance()

    @staticmethod
    def show_left_bar_button_action(ui_controller: UIController) -> None: 
        (
            ui_controller
                .with_display("main")
                .query("container.LeftBar")
                .set_visible(True)
        )
        (
            ui_controller
                .with_display("main")
                .query("container.ShowLeftBarButton")
                .set_visible(False)
        )

    @staticmethod
    def hide_left_bar_button_action(ui_controller: UIController) -> None:
        # Show this:
        (
            ui_controller
                .with_display("main")
                .query("container.ShowLeftBarButton")
                .set_visible(True)
        )

        # Hide the `Left Bar`
        (
            ui_controller
                .with_display("main")
                .query("container.LeftBar")
                .set_visible(False)
        )

PREPARE_UI_TABLE: typing.List[typing.Callable[[Job], None]] = [
    PrepareUI.load_main,
    PrepareUI.wait_main_load,
    PrepareUI.register_components
]