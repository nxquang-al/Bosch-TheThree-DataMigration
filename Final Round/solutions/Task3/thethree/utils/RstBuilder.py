import typing


class RstBuilder:
    def __init__(self) -> None:
        self._content = ''

    def _add(self, content: str, indent=0) -> None:
        self._content += " " * indent + content + "\n"

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
        self,
        name: str,
        attributes: dict,
        content: str = "",
        sub_directives: dict = {},
        indent=0,
    ) -> None:
        self._add(f".. {name}::", indent)
        for k, v in attributes.items():
            self._add(f"   :{k}: {v}", indent)
        self.content(content, indent)
        for k, v in sub_directives.items():
            self._add(f"   .. {k}::")
            self._add(v)

    def directives(
        self,
        directives: typing.List[typing.Tuple[str, typing.List[typing.Tuple[str, str]]]],
        indent=0,
    ) -> None:
        for directive in directives:
            if "html_content" in directive.keys():
                html_content = directive["html_content"]
            else:
                html_content = ""
            if "sub_directives" in directive.keys():
                sub_directives = directive["sub_directives"]
            else:
                sub_directives = {}
            self.directive(
                directive["name"],
                directive["attributes"],
                html_content,
                sub_directives,
                indent,
            )
            if "directives" in directive:
                self.directives(directive["directives"], indent + 3)

    def content(self, content: str, indent: int = 0) -> None:
        self._add(content, indent=indent)

    def get_rst(self) -> str:
        return self._content
