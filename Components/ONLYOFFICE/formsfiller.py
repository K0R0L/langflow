from typing import Any, List, Dict
from langflow.custom import Component
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs.inputs import (
    DataInput,
    IntInput,
    MessageTextInput,
)
from langflow.io import Output
from langflow.schema import Data
from langflow.schema.dotdict import dotdict
from langflow.docbuilder import docbuilder


class FormsFiller(Component):
    display_name: str = "Forms Filler"
    description: str = "Fill forms with data from files."
    name: str = "FormsFiller"
    MAX_FIELDS = 15
    icon = "FolderSync"

    inputs = [
        MessageTextInput(
            name="name",
            display_name="Name",
            info="Name of the person or entity.",
            value="",
            tool_mode=True,
        ),
        MessageTextInput(
            name="start_date",
            display_name="Start Date",
            info="Start date for the form (e.g., 01-01-2024).",
            value="",
            tool_mode=True,
        ),
        MessageTextInput(
            name="end_date",
            display_name="End Date",
            info="End date for the form (e.g., 31-12-2024).",
            value="",
            tool_mode=True,
        ),
        MessageTextInput(
            name="start_money",
            display_name="Start Money",
            info="Initial amount of money.",
            value="",
            tool_mode=True,
        ),
        MessageTextInput(
            name="end_money",
            display_name="End Money",
            info="Final amount of money.",
            value="",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="dict_list", method="build_data"),
    ]

    def process_file(
        self, file_path: str, field_names: List[str]
    ) -> Dict[str, Any]:
        """Process the file and extract data based on the provided field names."""
        builder = docbuilder.CDocBuilder()
        try:
            builder.OpenFile(
                file_path,
                "<m_nCsvTxtEncoding>0</m_nCsvTxtEncoding><m_nCsvDelimiter>0</m_nCsvDelimiter>",
            )
            context = builder.GetContext()
            globalObj = context.GetGlobal()
            api = globalObj["Api"]
            document = api.GetDocument()

            length = document.GetElementsCount().ToInt()
            record = {}
            for i in range(length):
                paragraph = document.GetElement(i)
                contentControls = paragraph.GetAllContentControls()
                controlLength = contentControls.GetLength()

                for j in range(controlLength):
                    control = contentControls.Get(j)
                    tag = control.GetTag().ToString()
                    text = control.GetElement(0).GetText().ToString()

                    if tag in field_names:
                        record[tag] = text

        except Exception as e:
            print(f"Ошибка при обработке файла '{file_path}': {e}")
        finally:
            builder.CloseFile()

        return record

    def get_text_from_processed_data(self, processed_data: List[str]) -> str:
        """Convert processed_data into a readable text format."""
        text_lines = []
        for person in processed_data:
            for key, record in person.items():
                text_lines.append(f"  {key}: {record}")
                text_lines.append("")

        return "\n".join(text_lines)

    def build_data(self) -> Data:
        """Process files and return extracted data."""
        file_paths = self.paths
        field_names = self.get_field_names()
        processed_data = []

        for file_path in file_paths:
            if isinstance(file_path, Data):
                file_path = file_path.text
            file_data = self.process_file(file_path, field_names)
            processed_data.append(file_data)
        return Data(data={"items": processed_data})
