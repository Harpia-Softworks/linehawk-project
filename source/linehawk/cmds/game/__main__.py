# 2026 Line Hawk Project by Harpia Softworks & Contribuitors.
# Project is under the license `BSD v2`, read `LICENSE.md` for more information.
from linehawk.engine import Engine

class App:
    engine: Engine

    def __init__(self) -> None:
        self.engine = Engine()

    def run(self) -> App:
        self.engine.loop()
        return self

#
# Main
#

def main() -> int:
    a: App = App()
    a.run()
    return 0

if __name__ == '__main__':
    print(f"Executing as `Main`")
    exit( main() )