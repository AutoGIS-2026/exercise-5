#!/usr/bin/env python3


"""Run the code cells of a jupyter notebook and collect the variables they define."""


import copy
import os
import pathlib
import sys
import types

import nbformat


# Errors raised while running student notebooks, reported by grade-assignment.py
NOTEBOOK_ERRORS = []

_CACHE = {}


def _clean_source(source):
    """Neutralise IPython-only syntax (magics, shell commands) so `exec` can run the cell."""
    lines = source.splitlines()
    if lines and lines[0].lstrip().startswith("%%"):
        lines = lines[1:]  # cell magic, e.g. %%time: run the cell body
    cleaned = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("%", "!")):
            indent = line[: len(line) - len(stripped)]
            line = indent + "pass  # IPython magic/shell command skipped by the autograder"
        cleaned.append(line)
    return "\n".join(cleaned)


def _first_code_line(source):
    for line in source.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "%", "!")):
            return line if len(line) <= 60 else line[:57] + "..."
    return ""


def _snapshot(namespace):
    variables = {}
    for name, value in namespace.items():
        if name.startswith("__") or isinstance(value, types.ModuleType):
            continue
        try:
            variables[name] = copy.deepcopy(value)
        except Exception:  # keep a reference to anything that cannot be copied
            variables[name] = value
    return variables


def _figures():
    """Return the open matplotlib figures (without importing matplotlib if unused)."""
    if "matplotlib.pyplot" not in sys.modules:
        return []
    pyplot = sys.modules["matplotlib.pyplot"]
    return [pyplot.figure(number) for number in pyplot.get_fignums()]


def run_notebook(path):
    """
    Execute all code cells of a notebook, in order, in one namespace.

    A cell tag (e.g., `Part 2`) starts a section, and all following cells, tagged or
    not, belong to it until the next tag. For each section, record the source code of
    its editable cells and a snapshot of all variables at the end of the section.

    All matplotlib figures the notebook creates are stored in the namespace as
    `_FIGURES` (a list, in order of creation).

    Returns
    =======
    tuple(dict, dict) :
        section_data ({section: {"variables": {...}, "source": "..."}}) and the final
        namespace
    """
    path = pathlib.Path(path).absolute()
    if path in _CACHE:
        return _CACHE[path]

    notebook = nbformat.read(str(path), as_version=4)
    figures_before = _figures()

    # Run from the notebook’s directory, like Jupyter does
    os.chdir(path.parent)

    namespace = {"display": lambda *args, **kwargs: None}
    section_data = {}
    current_section = None
    code_cell_number = 0

    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        code_cell_number += 1

        tags = cell.get("metadata", {}).get("tags", [])
        if tags and tags[0] != current_section:
            if current_section is not None:
                section_data[current_section]["variables"] = _snapshot(namespace)
            current_section = tags[0]
            section_data.setdefault(current_section, {"variables": {}, "source": ""})

        is_test_cell = cell.get("metadata", {}).get("editable") is False
        if current_section is not None and not is_test_cell:
            section_data[current_section]["source"] += cell.source + "\n"

        try:
            code = compile(_clean_source(cell.source), f"{path.name}, cell {code_cell_number}", "exec")
            exec(code, namespace)
        except Exception as error:  # record the error, and continue with the next cell
            NOTEBOOK_ERRORS.append({
                "notebook": path.name,
                "cell": code_cell_number,
                "first_line": _first_code_line(cell.source),
                "test_cell": is_test_cell,
                "error": f"{type(error).__name__}: {error}".splitlines()[0][:200],
            })

    if current_section is not None:
        section_data[current_section]["variables"] = _snapshot(namespace)

    namespace.pop("__builtins__", None)
    namespace["_FIGURES"] = [
        figure for figure in _figures()
        if not any(figure is before for before in figures_before)
    ]
    _CACHE[path] = (section_data, namespace)
    return _CACHE[path]


def import_notebook(path):
    """Return `(section_data, namespace)`, see `run_notebook()`."""
    return run_notebook(path)


def import_notebook_namespace(path):
    """Return the notebook’s final namespace as an object (`problem1.some_function`)."""
    _, namespace = run_notebook(path)
    return types.SimpleNamespace(**namespace)
