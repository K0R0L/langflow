from typing import List
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
    MAX_FIELDS = 15

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
            dt = datetime.strptime(str(date_str), "%d-%m-%Y")
            return int(dt.timestamp())
        except Exception:
            return None

    def get_field_names(self) -> List[str | None]:
        key1 = getattr(self, "field_1_name", None)
        from_date_str = getattr(self, "field_2_name", None)
        key2 = getattr(self, "field_3_name", None)
        to_date_str = getattr(self, "field_4_name", None)
        #raise Exception(f"{to_date_str=}")
        tag1 = getattr(self, "tag_1", None)
        tag2 = getattr(self, "tag_2", None)
        return [key1, tag1, from_date_str, key2, tag2, to_date_str]

    def process(self, file) -> bool:
        config_values: List[str] = self.get_field_names()
        key1, tag1, from_date_str, key2, tag2, to_date_str = config_values
        #raise Exception(f"{to_date_str=}")

        if not key1 and not key2:
            return False

        input_from_date: int | None = self.parse_date(from_date_str)
        input_to_date: int | None = self.parse_date(to_date_str)
        file_to_date: int | None = file.getFormValueByKey(key2,tag2)
        #raise Exception(f"{get_form_value(forms, key1,tag1)=}") 
        file_from_date: int | None = file.getFormValueByKey(key1,tag1)

        #raise Exception(f"{config_values=}")
        #raise Exception(f"{input_to_date=}, {input_from_date=},{file_to_date=},{file_from_date=}")
        if input_to_date and input_from_date and key1 and key2:
            raise Exception(f"{input_to_date=}, {input_from_date=},{file_to_date=},{file_from_date=},{(input_to_date > file_to_date) and (input_from_date < file_from_date)=}") 
            return (input_to_date > file_to_date) and (input_from_date < file_from_date)

        elif input_from_date and key1:
            #raise Exception(f"{file_from_date=}, {input_from_date=},{input_from_date < file_from_date=}") 
            return input_from_date < file_from_date

        elif input_to_date and key2:
            return file_to_date < input_to_date
        else:
            return False

    def build_data(self) -> Component:
        return self
