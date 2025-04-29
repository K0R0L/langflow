from langflow.custom import Component
from langflow.io import Output
from langflow.schema import Data
from langflow.inputs.inputs import IntInput, MessageTextInput
from langflow.field_typing.range_spec import RangeSpec
from langflow.schema.dotdict import dotdict

from langflow.docbuilder import docbuilder

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
        key = self.key
        tag = self.tag
        value = get_form_value(forms, key,tag)
        if not value:
            return False
        return True


