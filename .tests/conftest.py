#!/usr/bin/env python


"""Define fixtures shared among all tests."""


import pathlib
import pytest

import nbformat


TESTS_PATH = pathlib.Path(__file__).absolute().parent
REPOSITORY_PATH = TESTS_PATH.parent


# Exercise 5 is graded manually: the autograder only checks the committed output
# files and notebooks, it does not run the notebooks (which might use large data sets).


@pytest.fixture(scope="session")
def repository_path():
    yield REPOSITORY_PATH


@pytest.fixture(scope="session")
def output_directory(repository_path):
    yield repository_path / "docs"


def own_code(notebook_path):
    """Lines of code that the student added to a notebook (no comments, no blank lines)."""
    notebook = nbformat.read(str(notebook_path), as_version=4)
    lines = []
    for cell in notebook.cells:
        if cell.cell_type != "code" or cell.get("metadata", {}).get("editable") is False:
            continue
        lines += [
            line for line in cell.source.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
    return lines


@pytest.fixture(scope="session")
def problem1_code(repository_path):
    yield own_code(repository_path / "Exercise-5-problem-1.ipynb")


@pytest.fixture(scope="session")
def problem2_code(repository_path):
    yield own_code(repository_path / "Exercise-5-problem-2.ipynb")
