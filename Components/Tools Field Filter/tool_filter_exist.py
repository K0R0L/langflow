from typing import Optional

from langflow.custom import Component
from langflow.inputs.inputs import MessageTextInput
from langflow.io import Output


class ExistComponent(Component):
    display_name = "Exist Key Filter"
    name = "exist"
    icon = "table"
    description: str = "Check if key-tag pair exists in file"
    
    key: Optional[str] = None
    tag: Optional[str] = None

    def __init__(self, key: str = None, tag: str = None, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.tag = tag

    inputs = [
        MessageTextInput(
            name="form_key",
            display_name="Key",
            input_types=[],
            info="Key to check",
            advanced=True,
        ),
        MessageTextInput(
            name="form_tag",
            display_name="Tag",
            input_types=[],
            info="Tag to check",
            advanced=True,
        ),
    ]
    
    outputs = [
        Output(display_name="Result", name="result", method="build_output")
    ]

    def process(self, file) -> bool:
        forms = file.getFormsByKeyTag(self.form_key, self.form_tag)
        return len(forms) > 0

    @classmethod
    def create_instance(cls, form_key: str, tag: str) -> 'ExistComponent':
        return cls(form_key=form_key, tag=tag)
        
    def build_output(self) -> Component:
        return {"name":self.name,"Factory Method":self.create_instance}