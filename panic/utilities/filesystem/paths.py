"""Filesystem paths."""

import pathlib

from .. import apps

PROJECT_ROOT_DIRECTORY = pathlib.Path(apps.__file__).parent.parent

DOCUMENTATION_SOURCE_DIRECTORY = (
    PROJECT_ROOT_DIRECTORY.parent / "documentation" / "source"
)

DOCUMENTATION_CODEBASE_DIRECTORY = (
    DOCUMENTATION_SOURCE_DIRECTORY / "codebase" / "panic"
)
