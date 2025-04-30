from langflow.custom import Component
from langflow.inputs.inputs import MessageTextInput
from langflow.io import Output


class ExistComponent(Component):
    display_name = "Exist Key Filter"
    name = "Exist"
    icon = "table"
    description: str = "This defines the keys that will be checked for availability."
    inputs = [
        MessageTextInput(
            name="key",
            display_name="Key",
            input_types=[],
            info="Key.",
        ),
        MessageTextInput(
            name="tag",
            display_name="Tag",
            input_types=[],
            info="Tag.",
            advanced=True,
        ),
    ]
    outputs = [
        Output(display_name="Filtered Data", name="output", method="build_output")
    ]

    def build_output(self) -> Component:
        return self

    def process(self, file) -> bool:
        forms = file.getFormsByKeyTag(self.key, self.tag)
        return len(forms) > 0
