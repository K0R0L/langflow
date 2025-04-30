from langflow.custom import Component
from langflow.docbuilder import docbuilder
from langflow.inputs import Input
from langflow.inputs.inputs import DataInput
from langflow.io import Output
from langflow.schema import Data


class File:
    def __init__(self):
        self.builder = None
        self.context = None

        # js objects
        self.globalObj = None
        self.api = None
        self.document = None
        self.forms = None

    def open(self, file_path, params=""):
        self.builder = docbuilder.CDocBuilder()

        res = self.builder.OpenFile(file_path, params)
        if res != 0:
            return False

        self.context = self.builder.GetContext()
        self.globalObj = self.context.GetGlobal()
        self.Api = self.globalObj["Api"]
        self.document = self.Api.GetDocument()
        self.getAllForms()
        return True

    def close(self):
        if self.context is None:
            return
        del self.forms
        del self.document
        del self.api
        del self.globalObj
        del self.context
        self.context = None
        self.builder.CloseFile()

    def getAllForms(self):
        if self.context is None:
            return []
        if self.forms is None:
            self.forms = self.document.GetAllForms()
        return self.forms

    def getFormsByTag(self, tag):
        if self.context is None:
            return []
        return self.document.GetFormsByTag(tag)

    def getFormsByKey(self, key):
        if self.context is None:
            return []
        result = []
        for i in range(len(self.forms)):
            form = self.forms[i]
            if form.GetFormKey().ToString() == key:
                result.append(form)
        return result

    def getFormsByKeyTag(self, key, tag=None):
        if self.context is None:
            return []
        key_tag_forms = self.forms
        if tag is not None and tag != "":
            key_tag_forms = self.getFormsByTag(tag)
        result = []
        for i in range(len(key_tag_forms)):
            form = key_tag_forms[i]
            if form.GetFormKey().ToString() == key:
                result.append(form)
        return result

    def getFormValue(self, form):
        form_type = form.GetFormType().ToString()
        if form_type == "textForm":
            return form.GetText().ToString()
        elif form_type == "dateForm":
            return form.GetTime().ToDouble()
        elif form_type == "checkBoxForm":
            return form.IsChecked().ToBool()
        elif form_type == "radioButtonForm":
            return form.IsChecked().ToBool()
        elif form_type == "comboBoxForm":
            return form.GetText().ToString()
        elif form_type == "dropDownForm":
            return form.GetText().ToString()
        return None

    def getFormValueByKey(self, key, tag=None):
        forms_check = self.getFormsByKeyTag(key, tag)
        count = len(forms_check)

        if 0 == count:
            return None
        if 1 == count:
            return self.getFormValue(forms_check[0])

        choice = ""
        for i in range(count):
            form = forms_check[i]
            form_type = form.GetFormType().ToString()
            if "radioButtonForm" != form_type:
                return self.getFormValue(form)
            if form.IsChecked():
                choice = form.GetChoiceName()
        return choice

    def getRadioButtonValue(self, key):
        for i in range(len(self.forms)):
            form = self.forms[i]
            if form.GetFormKey().ToString() == key:
                form_type = form.GetFormType().ToString()
                if form_type == "checkBoxForm" or form_type == "radioButtonForm":
                    if form.IsChecked().ToBool():
                        return form.GetChoiceName().ToString()
        return None

    def __del__(self):
        self.close()


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
        Output(display_name="Paths", name="paths_list", method="build_paths"),
    ]

    def build_main(self) -> list:
        file_paths: list[str] = self.paths
        filters: list[Component] = self.fields
        output_keys = self.output_keys.data["output_keys"] if self.output_keys else None
        result = []

        for file_path in file_paths:
            if isinstance(file_path, Data):
                file_path = file_path.text

            file = File()
            if not file.open(file_path):
                continue

            passed = True
            for filter_component in filters:
                if hasattr(filter_component, "process"):
                    if not filter_component.process(file):
                        passed = False
                        break
            if passed:
                record = {"file_path": file_path}
                if output_keys:
                    for key in output_keys:
                        record[key] = file.getFormValueByKey(key)
                result.append(record)
            file.close()

        return result

    def build_data(self) -> Data:
        processed_data = self.build_main()
        return Data(data={"items": processed_data})

    def build_paths(self) -> list[Data]:
        processed_data = self.build_main()
        file_paths = [record["file_path"] for record in processed_data]
        return file_paths
