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
            display_name="Criteria",
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

    def get_form_value(self, forms, key, tag=None) -> str | int | bool | None:
        for i in range(forms.GetLength()):
            form = forms.Get(i)
            form_key = form.GetFormKey().ToString()
            if form_key == key:
                form_type = form.GetFormType().ToString()
                if form_type == "textForm":
                    return form.GetText().ToString()
                elif form_type == "dateForm":
                    return form.GetTime().ToDouble()
                elif form_type == "checkBoxForm":
                    return form.IsChecked().ToBool()
        return None

    def build_main(self) -> list[dict]:
        
        file_paths: list[str] = self.paths


        filters: list[Component] = self.fields
        output_keys: list[str] = (
            self.output_keys.data["output_keys"] if self.output_keys else None
        )
        result: list[dict] = []

        for file_path in file_paths:
            if isinstance(file_path, Data):
                file_path: str = file_path.text
            builder = docbuilder.CDocBuilder()

            builder.OpenFile(file_path, STANDARD_ENCODE_FORMAT)
   
            context: docbuilder.CDocBuilderContext = builder.GetContext()
            globalObj: docbuilder.CDocBuilderValue = context.GetGlobal()
            api: docbuilder.CDocBuilderValue | None = globalObj["Api"]
            document: docbuilder.CDocBuilderValue | None = api.GetDocument()
            forms: docbuilder.CDocBuilderValue | None = document.GetAllForms()
            passed: bool= True
            for filter_component in filters:
                if hasattr(filter_component, "process"):
                    if not filter_component.process(api, forms, self.get_form_value):
                        passed = False
                        break
            if passed:
                record = {"file_path": file_path}
                if output_keys:
                    for key in output_keys:
                        value: str | int | bool | None = self.get_form_value(forms, key)
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
