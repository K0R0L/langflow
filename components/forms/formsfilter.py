from datetime import datetime
from typing import Any, Dict, List

from langflow.custom import Component
from langflow.docbuilder import docbuilder
from langflow.inputs.inputs import DataInput
from langflow.io import Output
from langflow.schema import Data

STANDARD_ENCODE_FORMAT = (
    "<m_nCsvTxtEncoding>0</m_nCsvTxtEncoding><m_nCsvDelimiter>0</m_nCsvDelimiter>"
)


class FromFilter(Component):
    display_name: str = "From Filter"
    description: str = "Get data from files by fields"
    name: str = "FromFilter"
    icon = "FolderSync"

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
        ),
        DataInput(
            name="existing_fields",
            display_name="Existing Fields",
            info="List of existing fields in the file.",
            input_types=["Data"],
            value=None,
        ),
        DataInput(
            name="checkbox",
            display_name="Checkbox",
            info="Checkbox field.",
            input_types=["Data"],
            value=None,
        ),
        DataInput(
            name="output_keys",
            display_name="outputs",
            info="what field you want to outputs",
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
            self.log(f"Error opening file: {file_path}: {e}")
            return {}

        context = builder.GetContext()
        globalObj = context.GetGlobal()
        api = globalObj["Api"]
        document = api.GetDocument()
        forms = document.GetAllForms()
        formsLength = forms.GetLength()
        record = {}
        record["file_path"] = file_path
        for i in range(formsLength):
            form = forms.Get(i)
            key = form.GetFormKey().ToString()
            text = form.GetText().ToString()
            record[key] = text
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

    def _parse_dates(self, *values: list[str]) -> tuple:
        parsed_values = []
        for value in values:
            parsed_values.append(datetime.strptime(value, "%d-%m-%Y"))
        return parsed_values

    def _parse_amounts(self, *values: str) -> tuple:
        parsed_values = []
        for value in values:
            #TODO: add normal parsing
            parsed_values.append(float(value.split()[0]))
        return parsed_values

    def filter_vacation_data(
        self,
        vacation_data: List[Dict[str, Any]],
        operation: str,
        *field_names: str,
        type_of_input: str,
    ) -> List[Dict[str, Any]]:
        dates = field_names[0][1::2]
        keys = field_names[0][0::2]
        parsed_dates = self._parse_dates(*dates)

        return [
            person
            for person in vacation_data
            if self._should_include_person(
                person, operation, parsed_dates, keys, type_of_input
            )
        ]

    def _should_include_person(
        self,
        person: dict,
        operation: str,
        parsed_values: tuple,
        keys,
        type_of_input: str,
    ) -> bool:
        """Determine if person should be included in filtered results."""
        if operation == "Insert":
            start_field, end_field = parsed_values
            if type_of_input == "date":
                form_start, form_end = self._parse_dates(
                    person[keys[0]], person[keys[1]]
                )
            elif type_of_input == "money":
                form_start, form_end = self._parse_amounts(
                    person[keys[0]], person[keys[1]]
                )
            return (end_field >= form_end) and (form_start >= start_field)
        else:
            field = parsed_values[0]
            if type_of_input == "date":
                form_field = self._parse_dates(person[keys[0]])[0]
            elif type_of_input == "money":
                form_field = self._parse_amounts(person[keys[0]])[0]
            if operation == "<":
                return form_field < field
            elif operation == ">":
                return form_field > field

        return False

    def filter_money_data(
        self,
        money_data: list[dict[str, Any]],
        operation: str,
        *field_names: int,
        type_of_input: str,
    ) -> list[dict[str, Any]]:
        """Filter money data based on operation type and amounts."""
        amounts = field_names[0][1::2]
        keys = field_names[0][0::2]
        parsed_dates = self._parse_amounts(*amounts)

        return [
            person
            for person in money_data
            if self._should_include_person(
                person, operation, parsed_dates, keys, type_of_input
            )
        ]

    def build_data(self) -> Data:
        """Process files and return extracted data."""
        file_paths = self.paths
        flag = False
        # TODO: refactor this
        if self.checkbox is not None:
            checkbox = [self.checkbox.data.get("checkbox", [])]
            flag = True
        else:
            checkbox = []
        if self.fields is not None:
            field_names = self.fields.data.get("fields", [])
            type_of_operation = self.fields.data.get("type_of_operation", [])
            checkbox.append("doOperation")
        else:
            field_names = []
            type_of_operation = []
        if self.existing_fields is not None:
            existing_fields = self.existing_fields.data.get("existing_fields", [])
            checkbox.append("isExist")
        else:
            existing_fields = []
        if self.output_keys is not None:
            output_keys = self.output_keys.data.get("output_keys",[])
        else:
            output_keys = None
        
            
        processed_data = []
        
        if "doOperation" in checkbox and not flag:
            msg = f"you havent input input_types"
            raise ValueError(msg)
        # TODO: use asynchronous processing
        for file_path in file_paths:
            if isinstance(file_path, Data):
                file_path = file_path.text
            file_data: Dict[str, Any] = self.process_file(file_path)
            processed_data.append(file_data)
        
        if "isExist" in checkbox:
            processed_data = self.get_existing_fields(processed_data, existing_fields)

        if "doOperation" in checkbox:
            if "date" in checkbox:
                processed_data = self.filter_vacation_data(
                    processed_data, type_of_operation, field_names, type_of_input="date"
                )
            elif "money" in checkbox:
                processed_data = self.filter_money_data(
                    processed_data,
                    type_of_operation,
                    field_names,
                    type_of_input="money",
                )
            else:
                self.log(f"Invalid input type: {checkbox}. Expected 'date' or 'money'.")

        processed_data = [
            {key: record[key] for key in record if key != "file_path"}
            for record in processed_data
        ]
        if output_keys is not None:
            processed_data = [
                {key: record[key] for key in record if key in output_keys}
                for record in processed_data
            ]
        

        return Data(data={"items": processed_data})

    def load_directory(self) -> list[Data]:
        file_paths = self.paths
        flag = False
        # TODO: refactor this
        if self.checkbox is not None:
            checkbox = [self.checkbox.data.get("checkbox", [])]
            flag = True
        else:
            checkbox = []
        if self.fields is not None:
            field_names = self.fields.data.get("fields", [])
            type_of_operation = self.fields.data.get("type_of_operation", [])
            checkbox.append("doOperation")
        else:
            field_names = []
            type_of_operation = []
        if self.existing_fields is not None:
            existing_fields = self.existing_fields.data.get("existing_fields", [])
            checkbox.append("isExist")
        else:
            existing_fields = []
        processed_data = []
        checkbox.append("date")
        if "doOperation" in checkbox and not flag:
            msg = f"you havent input input_types"
            raise ValueError(msg)

        # TODO: use asynchronous processing
        for file_path in file_paths:
            file_data: Dict[str, Any] = self.process_file(file_path)
            processed_data.append(file_data)

        if "isExist" in checkbox:
            processed_data = self.get_existing_fields(processed_data, existing_fields)

        if "doOperation" in checkbox:
            if "date" in checkbox:
                processed_data = self.filter_vacation_data(
                    processed_data, type_of_operation, field_names, type_of_input="date"
                )
            elif "money" in checkbox:
                processed_data = self.filter_money_data(
                    processed_data,
                    type_of_operation,
                    field_names,
                    type_of_input="money",
                )
            else:
                self.log(f"Invalid input type: {checkbox}. Expected 'date' or 'money'.")

        file_paths = [record["file_path"] for record in processed_data]
        return file_paths
