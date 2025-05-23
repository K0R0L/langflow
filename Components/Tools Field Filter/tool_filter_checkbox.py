from langflow.custom import Component
from langflow.io import Output


class CheckBoxComponent(Component):
    display_name = "Checkbox Filter"
    name = "check_box"
    icon = "check-square"
    description: str = "Determines which checkboxes from the list have been checked"

    def __init__(
        self, key: str = None, tag: str = None, checked: bool = True, **kwargs
    ):
        super().__init__(**kwargs)
        self.key = key
        self.tag = tag
        self.checked = checked

    outputs = [Output(display_name="Factory", name="factory", method="build_output")]

    def process(self, file) -> bool:
        return self.checked == file.getFormValueByKey(self.key, self.tag)

    @classmethod
    def create_instance(
        cls, key: str, tag: str = None, checked: bool = True
    ) -> "CheckBoxComponent":
        return cls(key=key, tag=tag, checked=checked)

    def build_output(self) -> Component:
        return {
            "name": self.name,
            "Factory Method": self.create_instance,
        }
