from .job import *
import typing

class Scheduler:
    """
    Contains an bunch of cooperative jobs that might not have anything to do
    with each other.
    """
    __slots: typing.List[Job]

    def __init__(self) -> None:
        self.__slots = list()

    def get(
            self,
            name: str,
            steps: typing.List[typing.Callable[[Job], None]],
            userdata: object
    ) -> Job:
        found: typing.Optional[Job] = None
        for index in range(0, len(self.__slots)):
            test_job: Job = self.__slots[index]
            if test_job.get_status() == JobStatus.LAZY:
                found = test_job
                break
        if not found:
            new_job: Job = Job()
            new_job.set(
                name,
                steps,
                userdata
            )
            self.__slots.append(new_job)
            return new_job
        else:
            found.set(
                name,
                steps,
                userdata
            )
            return found

    def tick(self) -> typing.Self:
        for job in self.__slots:
            job.perform()
        return self