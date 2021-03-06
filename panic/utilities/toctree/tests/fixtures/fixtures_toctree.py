"""Fixtures for TOC Tree related tests."""

import os

SOURCE = "/app/code/root"
BASENAME_SOURCE = os.path.basename(SOURCE)

DESTINATION = "documentation/source/codebase"

SOURCE_FILE_SYSTEM = [
    (
        f"{SOURCE}",
        ['__pycache__', 'folder1', 'folder2', 'folder3'],
        [],
    ),
    (
        f"{SOURCE}/folder1",
        ['__pycache__'],
        [
            "__init__.py",
            "file1.py",
            ".DS_Store",
            "manage.py",
        ],
    ),
    (
        f"{SOURCE}/folder2",
        ['__pycache__', 'tests'],
        [
            "__init__.py",
            "file2a.py",
            "file2b.py",
            ".DS_Store",
        ],
    ),
    (
        f"{SOURCE}/folder2/tests",
        ['__pycache__'],
        [],
    ),
    (
        f"{SOURCE}/folder3",
        ["folder4", '__pycache__'],
        [
            "__init__.py",
            "file3a.py",
            "file3b.py",
            "command.sh",
        ],
    ),
    (
        f"{SOURCE}/folder3/folder4",
        [],
        [
            "__init__.py",
            "file4a.py",
            "file4b.py",
        ],
    ),
]

DESTINATION_FILE_SYSTEM = [
    (
        f"{DESTINATION}",
        ['folder1', 'folder2', 'folder3'],
        ['index.rst'],
    ),
    (
        f"{DESTINATION}/folder1",
        [],
        ["index.rst", "file1.rst"],
    ),
    (
        f"{DESTINATION}/folder2",
        [],
        [
            "index.rst",
            "file2a.rst",
            "file2b.rst",
        ],
    ),
    (
        f"{DESTINATION}/folder3",
        ["folder4"],
        [
            "index.rst",
            "file3a.rst",
            "file3b.rst",
        ],
    ),
    (
        f"{DESTINATION}/folder3/folder4",
        [],
        [
            "index.rst",
            "file4a.rst",
            "file4b.rst",
        ],
    ),
]

DESTINATION_FILE_CONTENT = {
    f"{DESTINATION}/index.rst": [
        "codebase",
        "========",
        ".. automodule:: root",
        "   :members:",
        "",
        ".. toctree::",
        "   :glob:",
        "",
        "   folder1/index.rst",
        "   folder2/index.rst",
        "   folder3/index.rst",
        "   *",
    ],
    f"{DESTINATION}/folder1/index.rst": [
        "folder1",
        "=======",
        ".. automodule:: folder1",
        "   :members:",
        "",
        ".. toctree::",
        "   :glob:",
        "",
        "   *",
    ],
    f"{DESTINATION}/folder1/file1.rst": [
        "file1.py",
        "========",
        ".. automodule:: folder1.file1",
        "   :members:",
    ],
    f"{DESTINATION}/folder2/index.rst": [
        "folder2",
        "=======",
        ".. automodule:: folder2",
        "   :members:",
        "",
        ".. toctree::",
        "   :glob:",
        "",
        "   *",
    ],
    f"{DESTINATION}/folder2/file2a.rst": [
        "file2a.py",
        "=========",
        ".. automodule:: folder2.file2a",
        "   :members:",
    ],
    f"{DESTINATION}/folder2/file2b.rst": [
        "file2b.py",
        "=========",
        ".. automodule:: folder2.file2b",
        "   :members:",
    ],
    f"{DESTINATION}/folder3/index.rst": [
        "folder3",
        "=======",
        ".. automodule:: folder3",
        "   :members:",
        "",
        ".. toctree::",
        "   :glob:",
        "",
        "   folder4/index.rst",
        "   *",
    ],
    f"{DESTINATION}/folder3/file3a.rst": [
        "file3a.py",
        "=========",
        ".. automodule:: folder3.file3a",
        "   :members:",
    ],
    f"{DESTINATION}/folder3/file3b.rst": [
        "file3b.py",
        "=========",
        ".. automodule:: folder3.file3b",
        "   :members:",
    ],
    f"{DESTINATION}/folder3/folder4/index.rst": [
        "folder4",
        "=======",
        ".. automodule:: folder3.folder4",
        "   :members:",
        "",
        ".. toctree::",
        "   :glob:",
        "",
        "   *",
    ],
    f"{DESTINATION}/folder3/folder4/file4a.rst": [
        "file4a.py",
        "=========",
        ".. automodule:: folder3.folder4.file4a",
        "   :members:",
    ],
    f"{DESTINATION}/folder3/folder4/file4b.rst": [
        "file4b.py",
        "=========",
        ".. automodule:: folder3.folder4.file4b",
        "   :members:",
    ],
}

MODULE_MAPPINGS = {
    f'{DESTINATION}': f"{BASENAME_SOURCE}",
    f'{DESTINATION}/folder1': "folder1",
    f'{DESTINATION}/folder2': "folder2",
    f'{DESTINATION}/folder3': "folder3",
    f'{DESTINATION}/folder3/folder4': "folder3.folder4",
}
