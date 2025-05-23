from langflow.custom import Component
from langflow.inputs import Input
from langflow.io import DataInput, Output


class ToolsExecutorComponent(Component):
    display_name = "Tools executor"
    description = "Creates filter objects from filter configurations and component factory methods"
    icon = "code"
    name = "ToolsExecutor"

    inputs = [
        DataInput(
            name="data_input",
            display_name="Data",
            info="Filter configurations",
        ),
        Input(
            name="fields",
            display_name="Criteria",
            input_types=["Component"],
            component=Component,
            is_list=True,
            info="List of filter components with factory methods",
        ),
    ]

    outputs = [
        Output(display_name="Exit", name="exist_output", method="exist_output"),
    ]

    def exist_output(self) -> Component:
        filter_configs = []
        filter_configs = self.data_input.data

        factory_methods = {}
        for component in self.fields:
            if (
                isinstance(component, dict)
                and "name" in component
                and "Factory Method" in component
            ):
                component_name = component["name"]
                factory_method = component["Factory Method"]
                factory_methods[component_name] = factory_method
        filters = []

        for config in filter_configs["filters"]:
            if not isinstance(config, dict):
                raise Exception(f"Invalid filter config: {config}")

            filter_type = config["type"]

            factory = None
            if filter_type in factory_methods:
                factory = factory_methods[filter_type]

            if not factory:
                raise Exception(
                    f"Factory method not found for filter type: {filter_type}"
                )

            try:
                if filter_type == "exist":
                    key = config["key"]
                    tag = config["tag"]
                    filter_obj = factory(key=key, tag=tag)
                elif filter_type == "check_box":
                    key = config["key"]
                    tag = config["tag"]
                    value = config["value"]
                    bool_value = value.lower() == "true"
                    filter_obj = factory(key=key, tag=tag, checked=bool_value)

                elif filter_type == "date_field_filter":
                    key_1 = config["key_1"]
                    tag_1 = config["tag_1"]
                    field_1 = config["field_1"]
                    key_2 = config["key_2"]
                    tag_2 = config["tag_2"]
                    field_2 = config["field_2"]
                    filter_obj = factory(
                        key_1=key_1,
                        tag_1=tag_1,
                        field_1=field_1,
                        key_2=key_2,
                        tag_2=tag_2,
                        field_2=field_2,
                    )

                elif filter_type == "text":
                    key = config["key"]
                    tag = config["tag"]
                    text_value = config["text"]
                    filter_obj = factory(key=key, tag=tag, value=text_value)

                else:
                    raise Exception(f"Unknown filter type: {filter_type}")

                filters.append(filter_obj)

            except Exception as e:
                raise Exception(f"Error creating filter object: {str(e)}")

        return filters
