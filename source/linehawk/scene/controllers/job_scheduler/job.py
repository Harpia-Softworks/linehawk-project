import typing
import enum

class JobStatus(enum.IntEnum):
    """Contains the current status for the `Job` element."""
    RUNNING         = 0
    WAITING         = 1
    FINISHED        = 2
    DIED            = 3
    CLEANING_UP     = 4
    LAZY            = 5

T = typing.TypeVar('T')

class Job:
    __userdata: object
    name: str
    __steps: typing.List[typing.Callable[[Job], None]]
    __state: int
    __status: JobStatus
    def __init__(self) -> None:
        self.__userdata = None
        self.name = str()
        self.__state = 0
        self.__status = JobStatus.LAZY
        self.__steps = list()

    def get_status(self) -> JobStatus: return self.__status
    def get_state(self) -> int: return self.__state

    def perform(self) -> typing.Self:
        match self.__status:
            case JobStatus.RUNNING | JobStatus.WAITING:
                self.__steps[self.__state](self)
            case JobStatus.FINISHED | JobStatus.DIED:
                # TODO: do something
                self.__status = JobStatus.CLEANING_UP
            case JobStatus.CLEANING_UP:
                self.__status = JobStatus.LAZY
            case _:
                pass
        return self

    def set(
            self,
            name: str,
            steps: typing.List[typing.Callable[[Job], None]],
            userdata: object
    ) -> typing.Self:
        """
        Set the machine to run again.
        """
        self.name = name
        self.__steps = steps
        self.__state = 0
        self.__status = JobStatus.RUNNING
        self.__userdata = userdata
        return self

    def advance(self, amount: int = 1) -> typing.Self:
        self.__state += amount
        if self.__state >= len(self.__steps):
            self.__status = JobStatus.FINISHED
        return self

    def rewind(self, amount: int = 1) -> typing.Self:
        if self.__state - amount < 0:
            raise ValueError(f"Impossible to rewind this amount: {amount}")
        self.__state -= amount
        return self

    def wait[T](
            self,
            condition: bool,
            evaluate: typing.Callable[[Job], T]
    ) -> typing.Optional[T]:
        """Set the current mode to be waiting"""
        if condition:
            self.__status = JobStatus.RUNNING
            return evaluate(self)
        else:
            self.__status = JobStatus.WAITING
        return None

    def get_userdata[T](self, convert_to: type[T]) -> T:
        if not isinstance(self.__userdata, convert_to):
            raise TypeError(f"Invalid type assigned to job: {self.name}")
        return self.__userdata