"""Update the version specifiers."""

import re

VERSION = "2.0.0b17"


def replace_version(filename):
    """Replace the version information in the given file."""
    with open(filename) as in_f:
        lines = []
        for line in in_f.readlines():
            match = re.match(r"(.*)([0-9]+\.[0-9]+\.[0-9]+(?:[ab][0-9]+))(.*)", line)
            if match:
                lines.append(f"{match.group(1)}{VERSION}{match.group(3)}\n")
            else:
                lines.append(line)

    with open(filename, "w") as out_f:
        for line in lines:
            out_f.write(line)


replace_version("uedition_editor/__about__.py")
replace_version("uedition_editor/frontend/src/about.ts")
