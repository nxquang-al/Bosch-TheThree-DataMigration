# Data Migration - Round 2 - TheThree

## Installation

## Task 1: Reqif to Json

```bash

```

## Task 2: Json to RST

### a) HTML to RST parser

- We implemented a class `MyHTMLParser` by inheriting from the `html.parser.HTMLParser` and overridden its handler methods to carry out the desired behavior when start tags, end tags, and data are encounterd.

- List of tags that our parser can handle:

  - \<body>\</body>
  - \<div>\</div>
  - \<span>\</span>
  - \<p>\</p>
  - \<em>\</em>, \<b>\</b>, \<code>\</code>
  - \<br>, \<a>\</a>
  - \<ul>, \<ol>, \<li>

- Example:

```python
text = '<ol><li>Coffee<ul><li>Arabica</li><li>Robusta</li></ul></li><li>Tea</li><li>Milk</li></ol>'
parser = MyHTMLParser()
parser.feed(text)
parser.get_rst()

### Output:
#
#
# #. Coffee
#
#     * Arabica
#     * Robusta
#
# #. Tea
# #. Milk
#
#
```

- Reference: [python-html2rest](https://github.com/averagehuman/python-html2rest)

### b) JSON to RST parser
