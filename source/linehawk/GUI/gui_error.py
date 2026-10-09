from linehawk.linehawk_error import LineHawkError

class GUIError(LineHawkError):
    """
    Base for all the `GUI` errors.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)