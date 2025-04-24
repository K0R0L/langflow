from datetime import datetime
from typing import Any, List

from langflow.custom import Component
from langflow.io import (
    DataInput,
    DropdownInput,
    MessageTextInput,
    Output,
)
from langflow.schema import Data
from langflow.schema.dotdict import dotdict


class DataFieldFilter(Component):
    display_name: str = "Data Filter Component"
    description: str = "filter data"
    name: str = "data_field_filter"
    MAX_FIELDS = 15
    icon = "filter"

    inputs = [
        DropdownInput(
            name="type_of_operation",
            display_name="Operation type",
            real_time_refresh=True,
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=["Insert", "<", ">"],
            value=[],
        ),
    ]

    outputs = [
        Output(
            display_name="Data",
            name="data",
            method="build_data",
        ),
    ]

    def update_build_config(
        self,
        build_config: dotdict,
        field_value: Any,
        field_name: str | None = None,
    ):
        """Update the build configuration based on the selected operation."""
        if field_name == "type_of_operation":
            default_keys = {
                "code",
                "_type",
                "dict_list",
                "type_of_operation",
            }

            type_of_operation = build_config.get("type_of_operation", {}).get(
                "value", []
            )
            if type_of_operation:
                operation = type_of_operation
                if operation == "Insert":
                    num_fields = 4
                elif operation == "<":
                    num_fields = 2
                elif operation == ">":
                    num_fields = 2
                else:
                    num_fields = 0
            else:
                num_fields = 0

            existing_fields = {}

            for key in list(build_config.keys()):
                if key not in default_keys:
                    existing_fields[key] = build_config.pop(key)

            for i in range(1, num_fields + 1):
                key = f"field_{i}_name"
                if key in existing_fields:
                    field = existing_fields[key]
                    build_config[key] = field
                else:
                    if i % 2 == 1:
                        field = MessageTextInput(
                            display_name=f"Key {i//2+i%2}",
                            name=key,
                            info=f"Key{i//2+i%2}.",
                        )
                    else:
                        field = MessageTextInput(
                            display_name=f"Value:{i//2}",
                            name=key,
                            info=f"Value of form for key:{i//2}.",
                        )
                    build_config[field.name] = field.to_dict()
        return build_config

    def get_field_names(self) -> List[str]:
        """Get the list of field names from the component's attributes."""
        field_names = []
        for key, value in self._attributes.items():
            if key.startswith("field_") and key.endswith("_name"):
                field_names.append(value)
        return field_names

    def get_text_from_processed_data(self, processed_data: List[str]) -> str:
        """Convert processed_data into a readable text format."""
        text_lines = []
        for text in processed_data:
            text_lines.append(text)
            text_lines.append("")

        return "\n".join(text_lines)

    def build_data(self) -> Data:
        """Process the list of dictionaries."""
        fields = self.get_field_names()
        type_of_operation = self._attributes["type_of_operation"]
        return Data(data={"fields":fields,"type_of_operation": type_of_operation})
