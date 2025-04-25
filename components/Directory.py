from langflow.base.data.utils import (
    TEXT_FILE_TYPES,
    retrieve_file_paths,
)
from langflow.custom import Component
from langflow.io import BoolInput, IntInput, MessageTextInput, MultiselectInput
from langflow.schema import Data
from langflow.template import Output


class DirectoryPathComponent(Component):
    display_name = "Directory Path"
    description = "Load paths from a directory."
    icon = "folder"
    name = "DirectoryPath"

    inputs = [
        MessageTextInput(
            name="path",
            display_name="Path",
            info="Path to the directory to load files from. Defaults to current directory ('.')",
            value=".",
            tool_mode=True,
        ),
        MultiselectInput(
            name="types",
            display_name="File Types",
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=TEXT_FILE_TYPES,
            value=[],
        ),
        IntInput(
            name="depth",
            display_name="Depth",
            advanced=True,
            info="Depth to search for files.",
            value=0,
        ),
        IntInput(
            name="max_concurrency",
            display_name="Max Concurrency",
            advanced=True,
            info="Maximum concurrency for loading files.",
            value=2,
        ),
        BoolInput(
            name="load_hidden",
            display_name="Load Hidden",
            advanced=True,
            info="If true, hidden files will be loaded.",
        ),
        BoolInput(
            name="recursive",
            display_name="Recursive",
            advanced=True,
            info="If true, the search will be recursive.",
        ),
        BoolInput(
            name="silent_errors",
            display_name="Silent Errors",
            advanced=True,
            info="If true, errors will not raise an exception.",
        ),
        BoolInput(
            name="use_multithreading",
            display_name="Use Multithreading",
            advanced=True,
            info="If true, multithreading will be used.",
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="load_directory"),
    ]

    def load_directory(self) -> list[Data]:
        path = self.path
        types = self.types
        depth = self.depth
        load_hidden = self.load_hidden
        recursive = self.recursive

        resolved_path = self.resolve_path(path)

        if not types:
            types = TEXT_FILE_TYPES

        invalid_types = [t for t in types if t not in TEXT_FILE_TYPES]
        if invalid_types:
            msg = f"Invalid file types specified: {invalid_types}. Valid types are: {TEXT_FILE_TYPES}"
            raise ValueError(msg)

        valid_types = types

        file_paths = retrieve_file_paths(
            resolved_path,
            load_hidden=load_hidden,
            recursive=recursive,
            depth=depth,
            types=valid_types,
        )

        return file_paths
