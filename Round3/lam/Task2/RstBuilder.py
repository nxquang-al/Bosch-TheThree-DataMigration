import sys
import typing


class RstBuilder:
    def __init__(self, out: typing.TextIO = sys.stdout) -> None:
        self._out = out

    def _add(self, content: str, indent=0) -> None:
        self._out.write(" " * indent + content + "\n")

    def heading(self, title: str, border: str = "=") -> None:
        self._add(border * len(title))
        self._add(title)
        self._add(border * len(title))

    def newline(self) -> None:
        self._add("")

    def subheading(self, subheading: str, underline: str = "*") -> None:
        self._add(subheading)
        self._add(underline * len(subheading))

    def directive(
        self, name: str, attributes: dict, content: str = "", indent=0
    ) -> None:
        self._add(f".. {name}::", indent)
        for k, v in attributes.items():
            self._add(f"   :{k}: {v}", indent)
        self.content(content, indent)

    def directives(
        self,
        directives: typing.List[typing.Tuple[str, typing.List[typing.Tuple[str, str]]]],
        indent=0,
    ) -> None:
        for directive in directives:
            if "html_content" in directive.keys():
                self.directive(
                    directive["name"],
                    directive["attributes"],
                    directive["html_content"],
                    indent,
                )
            else:
                self.directive(
                    directive["name"],
                    directive["attributes"],
                    indent=indent,
                )
            if "directives" in directive:
                self.directives(directive["directives"], indent + 3)

    def content(self, content: str, indent: int = 0) -> None:
        self._add(content, indent=indent)
