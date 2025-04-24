from langflow.custom import Component
from langflow.io import Output, DropdownInput
from langflow.schema import Data
from langflow.inputs.inputs import IntInput, MessageTextInput
from langflow.field_typing.range_spec import RangeSpec
from langflow.schema.dotdict import dotdict


class OutputComponent(Component):
    display_name = "Output keys"
    name = "output"
    MAX_FIELDS = 15
    inputs = [
        IntInput(
            name="number_of_fields",
            display_name="Number of Keys",
            info="Number of Keys to be added to the record.",
            real_time_refresh=True,
            value=0,
            range_spec=RangeSpec(
                min=1, max=MAX_FIELDS, step=1, step_type="int"
            ),
        ),
    ]
    outputs = [
        Output(
            display_name="Filtered Data", name="output", method="build_output"
        )
    ]

    def update_build_config(
        self, build_config: dotdict, field_value, field_name=None
    ):
        if field_name == "number_of_fields":
            default_keys = {"code", "_type", "number_of_fields", "data"}
            try:
                field_value_int = int(field_value)
            except ValueError:
                return build_config
            if field_value_int > self.MAX_FIELDS:
                build_config["number_of_fields"]["value"] = self.MAX_FIELDS
                raise ValueError(
                    f"Number of fields cannot exceed {self.MAX_FIELDS}."
                )

            existing_fields = {}
            for key in list(build_config.keys()):
                if key not in default_keys:
                    existing_fields[key] = build_config.pop(key)

            for i in range(1, field_value_int + 1):
                key = f"field_{i}_name"
                if key in existing_fields:
                    field = existing_fields[key]
                    build_config[key] = field
                else:
                    field = MessageTextInput(
                        display_name=f"Field {i} Name",
                        name=key,
                        info=f"Name of field {i}.",
                    )
                    build_config[field.name] = field.to_dict()
            build_config["number_of_fields"]["value"] = field_value_int
        return build_config

    def get_field_names(self):
        field_names = []
        for i in range(1, getattr(self, "number_of_fields", 0) + 1):
            field_name = getattr(self, f"field_{i}_name", None)
            if field_name:
                field_names.append(field_name)
        return field_names

    def build_output(self) -> Data:
        field_names = self.get_field_names()
        return Data(data={"output_keys": field_names})