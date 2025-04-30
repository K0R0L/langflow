from langflow.custom import Component
from langflow.io import Output
from langflow.inputs.inputs import MessageTextInput


class ExistComponent(Component):
    display_name = "Text Key Filter"
    name = "Text"
    MAX_FIELDS = 15
    icon = "table"
    description: str = "This defines the keys that will be checked for availability."
    inputs = [
        MessageTextInput(
            name="key",
            display_name="Key",
            input_types=[],
            info="Key."
        ),
        MessageTextInput(
            name="tag",
            display_name="Tag",
            input_types=[],
            info="Tag.",
            advanced=True
        ),
        MessageTextInput(
            name="value",
            display_name="Value",
            input_types=[],
            info="Value."
        ),
        
    ]
    outputs = [
        Output(
            display_name="Filtered Data", name="output", method="build_output"
        )
    ]


    def build_output(self) -> Component:
        return self

    def process(self, file) -> bool:
        return self.value == file.getFormValueByKey(self.key, self.tag)


