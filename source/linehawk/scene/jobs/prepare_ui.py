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
                .query("container.LeftBar.ActionBox.StartButton")
                .set_on_click(lambda _: print("bruh"))
        )
        job.advance()

PREPARE_UI_TABLE: typing.List[typing.Callable[[Job], None]] = [
    PrepareUI.load_main,
    PrepareUI.wait_main_load,
    PrepareUI.register_components
]