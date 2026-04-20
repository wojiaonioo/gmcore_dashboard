import glob
import os
import re
from pathlib import Path


_ASSIGNMENT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")
_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(
    r"^[+-]?(?:(?:\d+\.\d*|\.\d+|\d+)(?:[eEdD][+-]?\d+)?|\d+[eEdD][+-]?\d+)$"
)


def scan_testbed(testbed_root: str) -> dict:
    """Discover GMCORE test cases grouped by case category."""
    root = Path(testbed_root).expanduser().resolve()
    cases_by_category = {}

    if not root.is_dir():
        return cases_by_category

    for case_dir in sorted(root.iterdir(), key=lambda path: path.name):
        namelist_path = case_dir / "namelist"
        if not case_dir.is_dir() or not namelist_path.is_file():
            continue

        case_name = case_dir.name
        category = get_case_category(case_name)
        case_info = {
            "name": case_name,
            "path": str(case_dir.resolve()),
            "config": parse_namelist(str(namelist_path)),
            "nc_files": find_nc_files(str(case_dir)),
        }
        cases_by_category.setdefault(category, []).append(case_info)

    return cases_by_category


def parse_namelist(filepath: str) -> dict:
    """Parse a Fortran namelist into a flat dictionary."""
    namelist_path = Path(filepath)
    parameters = {}

    if not namelist_path.is_file():
        return parameters

    current_assignment = ""
    in_group = False

    for raw_line in namelist_path.read_text(encoding="utf-8").splitlines():
        line = _strip_comments(raw_line).strip()
        if not line:
            continue

        if line.startswith("&"):
            if current_assignment:
                _store_assignment(current_assignment, parameters)
                current_assignment = ""
            in_group = True
            continue

        if not in_group:
            continue

        if line == "/":
            if current_assignment:
                _store_assignment(current_assignment, parameters)
                current_assignment = ""
            in_group = False
            continue

        if _ASSIGNMENT_RE.match(line):
            if current_assignment:
                _store_assignment(current_assignment, parameters)
            current_assignment = line
            continue

        current_assignment = f"{current_assignment} {line}".strip()

    if current_assignment:
        _store_assignment(current_assignment, parameters)

    return parameters


def find_nc_files(case_dir: str) -> list:
    """Return NetCDF files in the case directory, newest first."""
    pattern = os.path.join(os.path.abspath(case_dir), "*.nc")
    nc_files = [os.path.abspath(path) for path in glob.glob(pattern) if os.path.isfile(path)]
    nc_files.sort(key=os.path.getmtime, reverse=True)
    return nc_files


def get_case_category(case_name: str) -> str:
    """Extract the dashboard grouping category from a case directory name."""
    base = case_name.split(".", 1)[0]
    underscore_letters = re.match(r"^(.*)_([A-Za-z][A-Za-z0-9]*)$", base)
    if underscore_letters:
        return underscore_letters.group(1)

    if "_" in base:
        return base.split("_", 1)[0]

    alpha_prefix = re.match(r"^[A-Za-z]+", base)
    if alpha_prefix:
        return alpha_prefix.group(0)

    return base


def get_executable(case_name: str) -> str:
    """Return the expected executable for a case."""
    if case_name.startswith("adv_"):
        return "gmcore_adv_driver.exe"
    return "gmcore_driver.exe"


def _store_assignment(text: str, parameters: dict) -> None:
    for assignment in _split_assignment_segments(text):
        if "=" not in assignment:
            continue

        key, value = assignment.split("=", 1)
        key = key.strip()
        if not key:
            continue

        parameters[key] = _parse_value(value.strip().rstrip(","))


def _parse_value(value: str):
    value = value.strip()
    if not value:
        return ""

    parts = _split_top_level_commas(value)
    if len(parts) > 1:
        return [_parse_value(part) for part in parts]

    lowered = value.lower()
    if lowered == ".true.":
        return True
    if lowered == ".false.":
        return False

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        quote = value[0]
        inner = value[1:-1]
        return inner.replace(quote * 2, quote)

    if _INT_RE.fullmatch(value):
        return int(value)

    if _FLOAT_RE.fullmatch(value):
        return float(re.sub(r"[dD]", "e", value))

    return value


def _split_assignment_segments(text: str) -> list:
    segments = []
    start = 0
    in_single = False
    in_double = False
    index = 0

    while index < len(text):
        char = text[index]

        if char == "'" and not in_double:
            if in_single and index + 1 < len(text) and text[index + 1] == "'":
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            if in_double and index + 1 < len(text) and text[index + 1] == '"':
                index += 2
                continue
            in_double = not in_double
        elif char == "," and not in_single and not in_double:
            tail = text[index + 1 :]
            if _ASSIGNMENT_RE.match(tail):
                segments.append(text[start:index].strip())
                start = index + 1

        index += 1

    last_segment = text[start:].strip()
    if last_segment:
        segments.append(last_segment)

    return segments


def _split_top_level_commas(text: str) -> list:
    parts = []
    start = 0
    in_single = False
    in_double = False
    index = 0

    while index < len(text):
        char = text[index]

        if char == "'" and not in_double:
            if in_single and index + 1 < len(text) and text[index + 1] == "'":
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            if in_double and index + 1 < len(text) and text[index + 1] == '"':
                index += 2
                continue
            in_double = not in_double
        elif char == "," and not in_single and not in_double:
            parts.append(text[start:index].strip())
            start = index + 1

        index += 1

    parts.append(text[start:].strip())
    return [part for part in parts if part]


def _strip_comments(text: str) -> str:
    characters = []
    in_single = False
    in_double = False
    index = 0

    while index < len(text):
        char = text[index]

        if char == "'" and not in_double:
            characters.append(char)
            if in_single and index + 1 < len(text) and text[index + 1] == "'":
                characters.append(text[index + 1])
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            characters.append(char)
            if in_double and index + 1 < len(text) and text[index + 1] == '"':
                characters.append(text[index + 1])
                index += 2
                continue
            in_double = not in_double
        elif char == "!" and not in_single and not in_double:
            break
        else:
            characters.append(char)

        index += 1

    return "".join(characters)
