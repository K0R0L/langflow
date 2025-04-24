from langflow.custom import Component
from langflow.io import Output, DataInput
from langflow.schema import Data
from typing import List, Dict, Any

class DataToText(Component):
    display_name = "Data To Text"
    name = "DataToText"
    inputs = [
        DataInput(
            name="dict_list",
            display_name="Data",
            info="List of dictionaries to process.",
            input_types=["Data"],
            required=True,
        ),
    ]
    outputs: List[Output] = [Output(display_name="Text", name="output", method="build_output")]

    def get_text_from_processed_data(self, processed_data: List[Dict[str, Any]]) -> str:
        """Convert processed_data into a readable text format."""
        text_lines = []
        for person in processed_data:
            #for key, record in person.items():
             #   text_lines.append(f"  {key}: {record}")
            text_lines.append(person)

        return "\n".join(text_lines)
         
    def build_output(self) -> Data:
        type_of_operation = self.dict_list.data.get("type_of_operation", [])
        fields = self.dict_list.data.get("fields", [])
        text = f"type_of_operation: {type_of_operation}, fields: {self.get_text_from_processed_data(fields)}"
        return text
