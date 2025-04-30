from langflow.custom import Component
from langflow.io import Output
from langflow.inputs.inputs import MessageTextInput

class RadioButtonComponent(Component):
    display_name = "RadioButton Filter"
    name = "radio_button"
    description: str = "Choice checker for radiobutton group."
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
            advanced=True
        ),
        MessageTextInput(
            name="choice",
            display_name="Choice",
            info="Choice for radio button group",
            input_types=[],
            value="",
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
        return self.choice == file.getFormValueByKey(self.key, self.tag)
