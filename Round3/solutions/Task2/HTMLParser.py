"""
To build an HTML to RST parser, we inherit and modify the class HTMLParser
from the module html, which serves as the basis for parsing files formated in HTML

Some sections are borrowed from: https://github.com/averagehuman/python-html2rest
"""

from html.parser import HTMLParser
from io import StringIO
from textwrap import TextWrapper
import html

IGNORE_TAGS = ["title", "style", "script"]
UNDERLINES = list("=-~`+;")


class LineBuffer(object):
    def __init__(self):
        self._lines = []
        self._wrapper = TextWrapper()

    def __len__(self):
        return len(self._lines)

    def __getitem__(self, i):
        return self._lines[i]

    def __setitem__(self, i, value):
        self._lines[i] = value

    def clear(self):
        self._lines[:] = []

    def read(self):
        return "\n".join(self._lines)

    def write(self, s):
        # normalise whitespace
        s = " ".join(s.split())
        self._lines.extend(self._wrapper.wrap(s))

    def rawwrite(self, s):
        self._lines.extend(s.splitlines())

    def indent(self, numspaces=4, start=0):
        linebuf = self._lines
        n = len(linebuf)
        if n > start:
            indent = " " * numspaces
            for i in range(start, n):
                linebuf[i] = indent + linebuf[i]

    def lstrip(self):
        linebuf = self._lines
        for i in range(len(linebuf)):
            linebuf[i] = linebuf[i].lstrip()


class MyHTMLParser(HTMLParser):
    def __init__(self, relative_root=None, relative_dir=None):
        HTMLParser.__init__(self)
        self.stringBuffer = StringIO()
        self.lineBuffer = LineBuffer()
        self.inblock = 0
        self.res = ""
        self.ignoredata = False
        self.lists = []
        self.links = {}
        self.relative_root = relative_root
        self.relative_dir = relative_dir
        return

    def flush(self):
        """
        Flush all the content of the line buffer to self.res
        """
        if self.lineBuffer:
            if self.inblock > 1:
                indent = 4 * (self.inblock - 1)
                self.lineBuffer.indent(indent)
            # unescape() converts ascii to symbol
            self.res += html.unescape(self.lineBuffer.read())
            self.lineBuffer.clear()

    def flush_stringbuffer(self):
        """
        flush the content of stringBuffer to lineBuffer
        """
        sbuf = self.stringBuffer.getvalue()
        if not sbuf:
            return
        elif self.lineBuffer:
            self.lineBuffer[-1] += sbuf
        else:
            self.lineBuffer.write(sbuf)
        self.clear_stringbuffer()

    def clear_stringbuffer(self):
        self.stringBuffer.seek(0)
        self.stringBuffer.truncate()

    def write_to_buffer(self, text):
        """
        Write a string to stringBuffer
        """
        self.stringBuffer.write(text)

    def merge_with_newline(self, text=""):
        """
        Writeline: Write with an extra endline
        """
        return self.merge(text + "\n")

    def merge(self, text=""):
        """
        Write: flush content from buffer to self.res and append the given text
        """
        self.flush_stringbuffer()
        self.flush()
        self.res += html.unescape(text)

    def write_startblock(self, text=""):
        if self.pending():
            self.merge_with_newline()
        self.merge_with_newline()
        self.merge_with_newline(text)

    def write_endblock(self, text=""):
        self.merge_with_newline(text)
        self.merge_with_newline()

    def handle_starttag(self, tag, attrs) -> None:
        """
        A built-in method of the html module, to handle the start tag of an element
        e.g. <div id="main">

        Args:
            tag: the name of the tag converted to lowercase
            attrs: a list of (name, value) pairs containing the attributes found inside the tag
        """
        if tag == "p":
            self.handle_start_p()
        elif tag == "em":
            self.handle_start_em()
        elif tag == "b":
            self.handle_start_b()
        elif tag == "code":
            self.handle_start_code()
        elif tag == "br":
            self.handle_start_br()
        elif tag == "ul":
            self.handle_start_ul()
        elif tag == "ol":
            self.handle_start_ol()
        elif tag == "li":
            self.handle_start_li()
        elif tag == "a":
            self.handle_start_a(attrs)
        elif tag == "span" or tag == "body":
            pass
        else:
            # Unknown start tags
            if tag in IGNORE_TAGS:
                self.ignoredata = True
            elif len(tag) == 2 and tag[0] == "h":
                self.write_startblock()

        return

    def handle_endtag(self, tag: str) -> None:
        """
        A built-in method to handle the end tag of an element

        Args:
            tag: the name of the tag converted
        """
        if tag == "p":
            self.handle_end_p()
        elif tag == "em":
            self.handle_end_em()
        elif tag == "b":
            self.handle_end_b()
        elif tag == "code":
            self.handle_end_code()
        elif tag == "ul":
            self.handle_end_ul()
        elif tag == "ol":
            self.handle_end_ol()
        elif tag == "li":
            self.handle_end_li()
        elif tag == "a":
            self.handle_end_a()
        elif tag == "span":
            pass
        elif tag == "body":
            self.handle_end_body()
        else:
            # Unknown end tags
            self.ignoredata = False
            if len(tag) == 2 and tag[0] == "h":
                self.flush_stringbuffer()
                if self.lineBuffer:
                    linebuf = self.lineBuffer
                    linebuf[-1] = linebuf[-1].strip()
                    char = UNDERLINES[int(tag[1]) - 1]
                    linebuf.write(char * len(linebuf[-1]))
                    self.merge_with_newline()

        return

    def handle_data(self, data: str) -> None:
        """
        A method to process arbitrary data between the start tag and end tag
        """
        if self.ignoredata:
            return
        else:
            if "waiting_data" in self.links:
                # Data between <a> and </a>, is mapped with href to display later
                self.links[self.links["waiting_data"]] = data
            self.write_to_buffer(" ".join(data.splitlines()))

    def get_rst(self):
        """
        This method is called at the end to process all the hrefs and retreive rst

        Return:
            The converted rst
        """
        for href, link in self.links.items():
            if href[0] != "#":
                # At the end display all the hrefs with their corresponding data
                self.merge_with_newline(".. _{}: {}".format(link, href))
        return self.res

    def handle_start_p(self):
        """Handle the <p> tag"""
        if not self.inblock:
            self.merge_with_newline()

    def handle_end_p(self):
        """Handle the </p> tag"""
        if not self.inblock:
            self.lineBuffer.lstrip()
            self.merge_with_newline()

    def handle_start_em(self):
        """<em> tag"""
        self.write_to_buffer("*")

    def handle_end_em(self):
        """</em> tag"""
        self.write_to_buffer("*")

    def handle_start_b(self):
        """<b> tag"""
        self.write_to_buffer("**")

    def handle_end_b(self):
        """</b> tag"""
        self.write_to_buffer("**")

    def handle_start_code(self):
        """<code> tag"""
        self.write_to_buffer("``")

    def handle_end_code(self):
        """</code> tag"""
        self.write_to_buffer("``")

    def handle_start_a(self, attributes):
        """<a> tag"""
        href = dict(attributes).get("href", None)
        if not href or href.startswith("#"):
            # There is no href or the href links to the top of the current page
            return
        else:
            if self.relative_root and self.relative_dir:
                if href.startswith("/"):
                    href = self.relative_root + href
                elif "://" not in href:
                    href = self.relative_dir + href
        self.write_to_buffer("`")
        # waiting for the data stored between <a> and </a>
        self.links["waiting_data"] = href
        return

    def handle_end_a(self):
        """
        Handle the </a>
        """
        if "waiting_data" in self.links:
            self.write_to_buffer("`_")
            # When data is mapped to self.links[href], delete the waiting
            del self.links["waiting_data"]
        return

    def handle_start_br(self):
        """<br> tag, just a line break"""
        if not self.inblock:
            self.merge_with_newline()
            # self.merge('| ')
        else:
            self.write_to_buffer(" ")

    def handle_start_ul(self):
        """<ul> tag, start of an unordered list"""
        if self.lists:
            self.handle_end_li()
        self.merge_with_newline()
        self.lists.append("* ")
        self.inblock += 1  # Count for indentation

    def handle_end_ul(self):
        """</ul> tag"""
        self.handle_end_li()
        self.lists.pop()
        self.inblock -= 1
        if self.inblock:
            self.merge_with_newline()
        else:
            self.write_endblock()

    def handle_start_ol(self):
        """<ol> tag, start of an ordered list"""
        if self.lists:
            self.handle_end_li()
        self.merge_with_newline()
        self.lists.append("#. ")
        self.inblock += 1

    def handle_end_ol(self):
        """</ol> tag"""
        self.handle_end_li()
        self.lists.pop()
        self.inblock -= 1
        if self.inblock:
            self.merge_with_newline()
        else:
            self.write_endblock()

    def handle_start_li(self):
        """<li> tag, each tag is an item of the <ul> or <ol> list"""
        self.merge_with_newline()
        self.write_to_buffer(self.lists[-1])

    def handle_end_li(self):
        """</li> tag"""
        self.flush_stringbuffer()
        if (
            self.lineBuffer
            and self.lineBuffer[0]
            and self.lineBuffer[0].lstrip()[:2] in ["* ", "#."]
        ):
            start_index = 1
        else:
            start_index = 0
        self.lineBuffer.indent(len(self.lists[-1]), start=start_index)
        self.merge()

    def handle_end_body(self):
        """</body> tag"""
        if self.inblock:
            return
        else:
            self.lineBuffer.lstrip()
            self.merge_with_newline()

    def close(self):
        HTMLParser.close(self)
