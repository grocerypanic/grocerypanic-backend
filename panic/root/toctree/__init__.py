"""TocTree settings for the Panic application."""

from utilities.filesystem.paths import PROJECT_ROOT_DIRECTORY
from utilities.toctree.settings import TocTreeFactorySettings

settings = TocTreeFactorySettings()
settings.files_filter_list = [
    f"{PROJECT_ROOT_DIRECTORY}/manage.py",
]
settings.folders_filter_list.append('tests_integration')
settings.folders_filter_list.append('templates')
