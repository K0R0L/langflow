from typing import Any, Dict, List

from langflow.custom import Component
from langflow.docbuilder import docbuilder
from langflow.inputs import Input
from langflow.inputs.inputs import (
    DataInput,
)
from langflow.io import Output
from langflow.schema import Data

STANDARD_ENCODE_FORMAT = (
    "<m_nCsvTxtEncoding>0</m_nCsvTxtEncoding><m_nCsvDelimiter>0</m_nCsvDelimiter>"
)


class FormFilterComponent(Component):
    display_name: str = "Form Filter"
    description: str = "Filters the specified forms based on the specified criteria."
    name: str = "FormFilter"
    icon = "filter"
    MAX_FIELDS = 15
    inputs = [
        DataInput(
            name="paths",
            display_name="File Paths",
            info="List of file paths to process.",
            is_list=True,
            required=True,
        ),
        Input(
            name="fields",
            input_types=["Component"],
            component=Component,
            is_list=True,
        ),
        DataInput(
            name="output_keys",
            display_name="Output keys",
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
        builder = docbuilder.CDocBuilder()
        try:
            builder.OpenFile(file_path, STANDARD_ENCODE_FORMAT)
        except Exception:
            msg=f"Error opening file: {file_path}"
            raise Exception(msg)

        context: docbuilder.CDocBuilderContext = builder.GetContext()
        globalObj: docbuilder.CDocBuilderValue = context.GetGlobal()
        api: docbuilder.CDocBuilderValue = globalObj["Api"]
        document: docbuilder.CDocBuilderValue  = api.GetDocument()
        forms: docbuilder.CDocBuilderValue = document.GetAllForms()
        record = {}
        record["file_path"] = file_path
        record["forms"] = forms
        record["api"] = api

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

    def get_form_value(self,forms, key,tag=None) -> Any:
        for i in range(forms.GetLength()):
            form = forms.Get(i)
            form_key = form.GetFormKey().ToString()
            form_tag = form.GetFormTag().ToString()
            
            if (not key or form_key == key) and (not tag or form_tag == tag) and (key or tag):
                form_type = form.GetFormType().ToString()
                if form_type == "textForm":
                    #raise Exception(f"{form_key=},{form.GetText().ToString()=}")
                    return form.GetText().ToString()
                elif form_type == "dateForm":
                    #raise Exception(f"{form_key=},{form.GetTime().ToInt()=},{form.GetText().ToString()=}")
                    return form.GetTime().ToInt()
                elif form_type == "checkBoxForm":
                    return form.IsChecked().ToBool()
        return None

    def build_main(self) -> List:
        file_paths: list[str] = self.paths
        filters: list[Component] = self.fields
        output_keys = self.output_keys.data["output_keys"] if self.output_keys else None
        result = []

        for file_path in file_paths:
            if isinstance(file_path, Data):
                file_path = file_path.text
            builder = docbuilder.CDocBuilder()
            try:
                builder.OpenFile(file_path, STANDARD_ENCODE_FORMAT)
            except Exception:
                continue
            context = builder.GetContext()
            globalObj = context.GetGlobal()
            api = globalObj["Api"]
            document = api.GetDocument()
            forms = document.GetAllForms()
            passed = True
            for filter_component in filters:
                if hasattr(filter_component, "process"):
                    #raise Exception(f"{forms=}, {key=}")
                    if not filter_component.process(api, forms, self.get_form_value):
                        passed = False
                        break
            if passed:
                record = {"file_path": file_path}
                if output_keys:
                    for key in output_keys:
                        #raise Exception(f"{forms=}, {key=}")
                        value = self.get_form_value(forms, key)
                        record[key] = value
                result.append(record)
            builder.CloseFile()
        return result

    def build_data(self) -> Data:
        processed_data = self.build_main()
        return Data(data={"items": processed_data})

    def load_directory(self) -> list[Data]:
        processed_data = self.build_main()
        file_paths = [record["file_path"] for record in processed_data]
        return file_paths







