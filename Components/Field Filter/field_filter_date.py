from datetime import datetime

from langflow.custom import Component
from langflow.io import (
    MessageTextInput,
    Output,
)


class DateKeyComponent(Component):
    display_name: str = "Date Filter"
    description: str = "Returns the date range, along with the corresponding keys."
    name: str = "date_field_filter"

    icon = "clock"

    inputs = [
        MessageTextInput(
            name="field_1_name",
            display_name="Key 1",
            input_types=[],
            info="Key1.",
        ),
        MessageTextInput(
            name="tag_1",
            display_name="Tag 1",
            input_types=[],
            advanced=True,
            info="Tag1.",
        ),
        MessageTextInput(
            name="field_2_name",
            display_name="From",
            placeholder="DD/MM/YYYY",
            input_types=[],
            info="Value of form for key:1.",
        ),
        MessageTextInput(
            name="field_3_name",
            display_name="Key 2",
            input_types=[],
            info="Key2.",
        ),
        MessageTextInput(
            name="tag_2",
            advanced=True,
            display_name="Tag 2",
            input_types=[],
            info="Tag2.",
        ),
        MessageTextInput(
            name="field_4_name",
            display_name="To",
            placeholder="DD/MM/YYYY",
            input_types=[],
            info="Value of form for key:2.",
        ),
    ]

    outputs = [
        Output(
            display_name="Data",
            name="data",
            method="build_data",
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
        key1: str | None = self.field_1_name
        from_date_str: str | None = self.field_2_name
        key2: str | None = self.field_3_name
        to_date_str: str | None = self.field_4_name
        tag1: str | None = self.tag_1
        tag2: str | None = self.tag_2
        return [key1, tag1, from_date_str, key2, tag2, to_date_str]

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

    def build_data(self) -> Component:
        return self
