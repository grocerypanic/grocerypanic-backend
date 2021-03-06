"""TocTree settings for the Panic application."""

from utilities.filesystem.paths import PROJECT_ROOT_DIRECTORY
from utilities.toctree.settings import TocTreeFactorySettings

factory_settings = TocTreeFactorySettings()
factory_settings.files_filter_list = [
    f"{PROJECT_ROOT_DIRECTORY}/manage.py",
]
factory_settings.folders_filter_list.append('tests_integration')
