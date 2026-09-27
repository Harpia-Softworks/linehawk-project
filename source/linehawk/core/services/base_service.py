class BaseService:
    _name: str

    def __init__(self, name: str) -> None:
        self._name = name

    def tick(self) -> None:
        pass

    def draw(self) -> None:
        pass