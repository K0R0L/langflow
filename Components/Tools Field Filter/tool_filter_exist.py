from langflow.custom import Component
from langflow.io import Output


class ExistComponent(Component):
    display_name = "Exist Key Filter"
    name = "exist"
    icon = "table"
    description: str = "Check if key-tag pair exists in file"

    def __init__(self, key: str = None, tag: str = None, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.tag = tag

    outputs = [Output(display_name="Result", name="result", method="build_output")]

    def process(self, file) -> bool:
        forms = file.getFormsByKeyTag(self.key, self.tag)
        return len(forms) > 0

    @classmethod
    def create_instance(cls, key: str, tag: str) -> "ExistComponent":
        return cls(key=key, tag=tag)

    def build_output(self) -> Component:
        return {"name": self.name, "Factory Method": self.create_instance}
