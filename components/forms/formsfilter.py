from typing import Any, Dict, List

from langflow.custom import Component
from langflow.docbuilder import docbuilder
from langflow.inputs.inputs import (
    DataInput,
)
from langflow.io import Output
from langflow.schema import Data
from datetime import datetime

STANDARD_ENCODE_FORMAT = (
    "<m_nCsvTxtEncoding>0</m_nCsvTxtEncoding><m_nCsvDelimiter>0</m_nCsvDelimiter>"
)


class FromFilter(Component):
    display_name: str = "From Filter"
    description: str = "Get data from files by fields"
    name: str = "FromFilter"
    icon = "FolderSync"
    MAX_FIELDS = 15
    inputs = [
        DataInput(
            name="paths",
            display_name="File Paths",
            info="List of file paths to process.",
            is_list=True,
            required=True,
        ),
        DataInput(
            name="fields",
            display_name="Fields",
            info="List of fields to extract from the files.",
            input_types=["Data"],
            value=None,
            is_list=True,
        ),
        DataInput(
            name="output_keys",
            display_name="Fields",
            info="List of fields to extract from the files.",
            input_types=["Data"],
            value=None,
            
        ),
        
    ]

    outputs = [
        Output(display_name="Data", name="data_list", method="build_data"),
        Output(display_name="Paths", name="paths_list", method="load_directory"),
    ]

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process the file and extract data based on the provided field names."""
        builder = docbuilder.CDocBuilder()
        try:
            builder.OpenFile(file_path, STANDARD_ENCODE_FORMAT)
        except Exception as e:
            msg=f"Error opening file: {file_path}: {e}"
            raise Exception(msg)

        context = builder.GetContext()
        globalObj = context.GetGlobal()
        api = globalObj["Api"]
        document = api.GetDocument()
        forms = document.GetAllForms()
        formsLength: int = forms.GetLength()
        record = {}
        record["file_path"] = file_path
        for i in range(formsLength):
            form = forms.Get(i)
            key: str = form.GetFormKey().ToString()
            form_type: str = form.GetFormType().ToString()

            if form_type == "textForm":
                text: str = form.GetText().ToString()
                record[key] = text
            elif form_type == "dateForm":
                time: int = form.GetTime().ToInt()
                record[key] = time

            elif form_type == "checkBoxForm":
                checkBox: bool = form.IsChecked().ToBool()
                record[key] = checkBox
        builder.CloseFile()
        return record

    def get_existing_fields(
        self, data: List[Dict[str, Any]], existing_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter data to include only existing fields."""
        filtered_data = []
        for record in data:
            if all(key in record for key in existing_fields):
                filtered_data.append(record)
        return filtered_data

    def _should_include_person(
        self,
        person: dict,
        operation: str,
        parsed_values: tuple,
        keys,
    ) -> bool:
        """Determine if person should be included in filtered results (money only)."""
        if operation == "Insert":
            start_field, end_field = parsed_values
            form_start = self.parse_date(person[keys[0]]) 
            form_end =self.parse_date(person[keys[1]])
            return (end_field >= form_end) and (form_start >= start_field)
        else:
            if operation == "<":
                form_field = self.parse_date(person[keys[0]])
                field = parsed_values[0]
                return field < form_field
            elif operation == ">":
                form_field = self.parse_date(person[keys[1]])
                field = parsed_values[1]
                return form_field < field

        return False
        
    def parse_date(self,date_str)-> int:
        """Convert date string to milliseconds since epoch."""
        if not date_str:
            return None
        try:
            dt = datetime.strptime(date_str, "%d-%m-%Y")
            return int(dt.timestamp() * 1000)
        except Exception:
            return None
            
    def filter_date(
        self,
        money_data: list[dict[str, Any]],
        *field_names: int,
    ) -> list[dict[str, Any]]:
        """Filter money data based on operation type and amounts."""
        amounts:list[str] = field_names[0][1::2]
        keys:list[str] = field_names[0][0::2]

        parsed_dates = [self.parse_date(a) for a in amounts]

        if parsed_dates[0] and parsed_dates[1]:
            operation ="Insert"
        elif parsed_dates[0]:
            operation = "<"
        elif parsed_dates[1]:
            operation = ">"
        else:
            msg="Invalid operation"
            raise Exception(msg)

        return [
            person
            for person in money_data
            if self._should_include_person(
                person, operation, parsed_dates, keys
            )
        ]

    def build_main(self) -> List:
        """Process files and return extracted data."""
        file_paths = self.paths
        all_data = self.fields
        existing_fields = []
        checkbox_values = []
        operation_fields = []
        output_keys = self.output_keys.data["output_keys"]
        for data_obj in all_data:
            data = data_obj.data
            if "existing_fields" in data:
                existing_fields.extend(data["existing_fields"])
            if "check_box" in data:
                checkbox_values.extend(data["check_box"])
            if "fields" in data:
                operation_fields.append(data["fields"])
        processed_data = []

        for file_path in file_paths:
            if isinstance(file_path, Data):
                file_path = file_path.text
            file_data: Dict[str, Any] = self.process_file(file_path)
            processed_data.append(file_data)

        if existing_fields:
            processed_data = self.get_existing_fields(processed_data, existing_fields)
        if checkbox_values:
            processed_data = [
                record for record in processed_data
                if not any(
                    value in record and record[value] is False
                    for value in checkbox_values
                )
            ]

        while len(operation_fields) > 0:
            field_names = operation_fields.pop()
            processed_data = self.filter_date(
                processed_data,
                field_names,
            )

        #processed_data = [
        #    {key: record[key] for key in record if key != "file_path"}
        #    for record in processed_data
        #]
        if output_keys is not None:
            processed_data = [
                {key: record[key] for key in record if key in output_keys}
                for record in processed_data
            ]
        return processed_data

    def build_data(self) -> Data:
        processed_data = self.build_main()
        return Data(data={"items": processed_data})

    def load_directory(self) -> list[Data]:
        processed_data = self.build_main()
        file_paths = [record["file_path"] for record in processed_data]
        return file_paths



