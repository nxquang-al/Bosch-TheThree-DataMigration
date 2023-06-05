import sys
import typing

class RstBuilder:
    def __init__(self, out: typing.TextIO = sys.stdout) -> None:
        self._out = out

    def _add(self, content: str) -> None:
        self._out.write(content + "\n")

    def title(self, title: str, border: str = "=") -> None:
        self._add(border * len(title))
        self._add(title)
        self._add(border * len(title))

    def newline(self) -> None:
        self._add("")
    
    def heading(self, heading: str, underline: str = "*") -> None:
        self._add(heading)
        self._add(underline * len(heading))

    def directive(self, name: str, fields: typing.List[typing.Tuple[str, str]]) -> None:
        self._add(f".. {name}::")
        for k, v in fields:
            self._add(f"   :{k}: {v}")
    
    def content(self, content: str) -> None:
        self._add(content)
