from langflow.custom import Component
from langflow.inputs import Input
from langflow.io import DataInput, Output


class ToolsExecutorComponent(Component):
    display_name = "Tools executor"
    description = "Use as a template to create your own component."
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "code"
    name = "CustomComponent"

    inputs = [
        DataInput(
            name="data_input",
            display_name="Data",
            info="The initial list of Data objects to iterate over.",
        ),
        Input(
            name="fields",
            display_name="Criteria",
            input_types=["Component"],
            component=Component,
            is_list=True,
        ),
    ]

    outputs = [
        Output(display_name="Exist", name="exist_output", method="exist_output"),
    ]

    def exist_output(self) -> Component:
        for form_component in self.fields:
            if form_component["name"] == "exist":
                exist_factory_method = form_component["Factory Method"]
            elif form_component["name"] == "check_box":
                check_box_factory_method = form_component["Factory Method"]
            elif form_component["name"] == "date_field_filter":
                date_factory_method = form_component["Factory Method"]
            elif form_component["name"] == "Text":
                text_factory_method = form_component["Factory Method"]

        return None
