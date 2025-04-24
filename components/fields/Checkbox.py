from langflow.custom import Component
from langflow.io import (
    DropdownInput,
    Output,
)
from langflow.schema import Data


class CheckboxComponent(Component):
    display_name: str = "Checkbox"
    description: str = "Checkbox field filter"
    name: str = "checkbox"
    MAX_FIELDS = 15
    icon = "filter"

    inputs = [
        DropdownInput(
            name="type_of_input",
            display_name="Input type",
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=["date", "money"],
            real_time_refresh=True,
            value=[],
        ),
    ]
    outputs = [
        Output(
            display_name="Filtered Data", name="output", method="build_output"
        )
    ]

    def build_output(self) -> Data:
        return Data(data={"checkbox": self.type_of_input})
