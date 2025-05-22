from typing import Optional

from langflow.custom import Component
from langflow.inputs.inputs import BoolInput, MessageTextInput
from langflow.io import Output


class CheckBoxComponent(Component):
    display_name = "Checkbox Filter"
    name = "check_box"
    icon = "check-square"
    description: str = "Determines which checkboxes from the list have been checked"
    
    form_key: Optional[str] = None
    form_tag: Optional[str] = None
    checked: bool = True

    def __init__(
        self,
        form_key: str = None,
        form_tag: str = None,
        checked: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.form_key = form_key
        self.form_tag = form_tag
        self.checked = checked

    inputs = [
        MessageTextInput(
            name="form_key",
            display_name="Key",
            input_types=[],
            info="Key for checkbox identification",
            advanced=True 
        ),
        MessageTextInput(
            name="form_tag",
            display_name="Tag",
            input_types=[],
            info="Tag for checkbox grouping",
            advanced=True  
        ),
        BoolInput(
            name="checked",
            display_name="Checked State",
            info="Default checkbox state",
            input_types=[],
            value=True,
            advanced=True
        )
    ]
    
    outputs = [
        Output(display_name="Factory", name="factory", method="build_output")
    ]

    def process(self, file) -> bool:
        return self.checked == file.getFormValueByKey(self.form_key, self.form_tag)

    @classmethod
    def create_instance(
        cls,
        form_key: str,
        form_tag: str = None,
        checked: bool = True
    ) -> 'CheckBoxComponent':
        return cls(
            form_key=form_key,
            form_tag=form_tag,
            checked=checked
        )

    def build_output(self) -> Component:
        return {
            "name": self.name,
            "Factory Method": self.create_instance,
        }