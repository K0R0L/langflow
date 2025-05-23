from datetime import datetime
from typing import Optional
from langflow.custom import Component
from langflow.inputs.inputs import MessageTextInput
from langflow.io import Output


class DateKeyComponent(Component):
    display_name: str = "Date Filter"
    description: str = "Returns the date range, along with the corresponding keys."
    name: str = "date_field_filter"
    icon = "clock"

    def __init__(
        self,
        key_1: str = None,
        tag_1: str = None,
        field_1: str = None,
        key_2: str = None,
        tag_2: str = None,
        field_2: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.key_1: str = key_1
        self.tag_1: str = tag_1
        self.field_1: str = field_1
        self.key_2: str = key_2
        self.tag_2: str = tag_2
        self.field_2: str = field_2

    outputs = [
        Output(
            display_name="Data",
            name="data",
            method="build_output",
        ),
    ]

    def parse_date(self, date_str) -> int:
        if not date_str:
            return None
        try:
            dt = datetime.strptime(str(date_str), "%d/%m/%Y")
            return float(dt.timestamp()) * 1000
        except (TypeError, ValueError) as e:
            msg = f"Can't parse '{date_str}' as date: {e!s}"
            raise ValueError(msg) from e

    def get_field_names(self) -> list[str | None]:
        return [
            self.key_1,
            self.tag_1,
            self.field_1,
            self.key_2,
            self.tag_2,
            self.field_2,
        ]

    def process(self, file) -> bool:
        config_values: list[str] = self.get_field_names()
        key1, tag1, from_date_str, key2, tag2, to_date_str = config_values

        if not key1 and not key2:
            return False

        input_from_date: int | None = self.parse_date(from_date_str)
        input_to_date: int | None = self.parse_date(to_date_str)
        file_to_date: int | None = file.getFormValueByKey(key2, tag2)
        file_from_date: int | None = file.getFormValueByKey(key1, tag1)

        if all([input_to_date, input_from_date, file_from_date, file_to_date]):
            return (input_from_date < file_from_date) and (file_to_date < input_to_date)
        elif input_from_date and file_from_date:
            return input_from_date < file_from_date
        elif input_to_date and file_to_date:
            return file_to_date < input_to_date
        else:
            return False

    @classmethod
    def create_instance(
        cls,
        key_1: str,
        tag_1: str = None,
        field_1: str = None,
        key_2: str = None,
        tag_2: str = None,
        field_2: str = None,
    ) -> "DateKeyComponent":
        return cls(
            key_1=key_1,
            tag_1=tag_1,
            field_1=field_1,
            key_2=key_2,
            tag_2=tag_2,
            field_2=field_2,
        )

    def build_output(self) -> Component:
        return {
            "name": self.name,
            "Factory Method": self.create_instance,
        }
