from langflow.custom import Component
from langflow.io import Output
from langflow.inputs.inputs import MessageTextInput


class ExistComponent(Component):
    display_name = "Exist Key Filter"
    name = "Exist"
    MAX_FIELDS = 15
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
            advanced=True,
            display_name="Tag",
            input_types=[],
            info="Tag.",
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
        tag:str = self.tag
        value:str|bool|int|None = get_form_value(forms, key,tag)
        if not value:
            return False
        return True


