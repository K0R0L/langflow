from langflow.custom import Component
from langflow.io import Output
from langflow.inputs.inputs import MessageTextInput, BoolInput

class CheckBoxComponent(Component):
    display_name = "Checkbox Filter"
    name = "check_box"
    description: str = "This determines which checkboxes from the list have been checked."
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
            advanced=True,
            input_types=[],
            info="Tag.",
        ),
        BoolInput(
            name="flag",
            display_name="Checked",
            info="Is the checkbox checked?",
            input_types=[],
            value=True,
        ),
        
    ]
    outputs = [
        Output(
            display_name="Filtered Data", name="output", method="build_output"
        )
    ]

    def build_output(self) -> Component:
        return self

    def process(self, api, forms, get_form_value) -> bool:
        key:str = self.key
        flag:bool = self.flag
        value:bool|None = get_form_value(forms, key)

        return value == flag
