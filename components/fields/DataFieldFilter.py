from typing import List

from langflow.custom import Component
from langflow.io import (
    MessageTextInput,
    Output,
)
from langflow.schema import Data


class DataFieldFilter(Component):
    display_name: str = "Data Filter Component"
    description: str = "filter data"
    name: str = "data_field_filter"
    MAX_FIELDS = 15
    icon = "filter"

    inputs = [
        MessageTextInput(
            name="field_1_name",
            display_name="Key 1",
            info="Key1.",
        ),
        MessageTextInput(
            name="field_2_name",
            display_name="Value:1",
            info="Value of form for key:1.",
        ),
        MessageTextInput(
            name="field_3_name",
            display_name="Key 2",
            info="Key2.",
        ),
        MessageTextInput(
            name="field_4_name",
            display_name="Value:2",
            info="Value of form for key:2.",
        ),
    ]

    outputs = [
        Output(
            display_name="Data",
            name="data",
            method="build_data",
        ),
    ]

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
        return Data(data={"fields":fields})
