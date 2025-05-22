from typing import Optional

from langflow.custom import Component
from langflow.inputs.inputs import MessageTextInput
from langflow.io import Output


class ExistComponent(Component):
    display_name = "Text Key Filter"
    name = "Text"
    icon = "table"
    description: str = "Check if text value matches form data"
    
    key: Optional[str] = None
    tag: Optional[str] = None
    value: Optional[str] = None

    def __init__(
        self,
        key: str = None,
        tag: str = None,
        value: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.key = key
        self.tag = tag
        self.value = value

    inputs = [
        MessageTextInput(
            name="key",
            display_name="Key",
            input_types=[],
            info="Form field key",
            advanced=True
        ),
        MessageTextInput(
            name="tag",
            display_name="Tag",
            input_types=[],
            info="Form field tag",
            advanced=True
        ),
        MessageTextInput(
            name="value",
            display_name="Value",
            input_types=[],
            info="Value to compare",
            advanced=True
        ),
    ]
    
    outputs = [
        Output(display_name="Factory", name="factory", method="build_output")
    ]

    def process(self, file) -> bool:
        return str(self.value) == str(file.getFormValueByKey(self.key, self.tag))

    @classmethod
    def create_instance(
        cls,
        key: str,
        tag: str = None,
        value: str = None
    ) -> 'ExistComponent':
        return cls(
            key=key,
            tag=tag,
            value=value
        )

    def build_output(self) -> Component:
        return {
            "name": self.name,
            "Factory Method": self.create_instance,
        }