from langflow.custom import Component
from langflow.inputs import Input
from langflow.io import DataInput, Output


class ToolsExecutorComponent(Component):
    display_name = "Tools executor"
    description = "Creates filter objects from filter configurations and component factory methods"
    icon = "code"
    name = "ToolsExecutor"

    inputs = [
        DataInput(
            name="data_input",
            display_name="Data",
            info="Filter configurations",
        ),
        Input(
            name="fields",
            display_name="Criteria",
            input_types=["Component"],
            component=Component,
            is_list=True,
            info="List of filter components with factory methods",
        ),
    ]

    outputs = [
        Output(display_name="Exit", name="exist_output", method="exist_output"),
    ]

    def exist_output(self) -> Component:
        filter_configs = []
        filter_configs = self.data_input.data
        
        factory_methods = {}
        for component in self.fields:
            if isinstance(component, dict) and "name" in component and "Factory Method" in component:
                component_name = component["name"]
                factory_method = component["Factory Method"]
                factory_methods[component_name] = factory_method
        
        filters = []
        
        for config in filter_configs["filters"]:
            if not isinstance(config, dict):
                raise Exception(f"Invalid filter config: {config}")
                continue
            
            filter_type = config["type"]
            key = config["key"]
            tag = config["tag"]
            
            if not key:
                raise Exception(f"No field specified for filter: {config}")
            
            factory = None
            if filter_type == "exist" and "exist" in factory_methods:
                factory = factory_methods["exist"]
            elif filter_type == "checkbox" and "check_box" in factory_methods:
                factory = factory_methods["check_box"]
            elif filter_type == "date" and "date_field_filter" in factory_methods:
                factory = factory_methods["date_field_filter"]
            elif filter_type == "text" and "text" in factory_methods:
                factory = factory_methods["text"]
            
            if not factory:
                raise Exception(f"Factory method not found for filter type: {filter_type}")
            
            try:
                if filter_type == "exist":
                    filter_obj = factory(key=key,tag=tag)
                elif filter_type == "checkbox":
                    value = config.get("value", False)
                    filter_obj = factory(key=key,tag=tag, value=value)
                elif filter_type == "date":
                    from_date = config.get("from", None)
                    to_date = config.get("to", None)
                    filter_obj = factory(key=key, from_date=from_date, to_date=to_date)
                elif filter_type == "text":
                    text = config.get("text", "")
                    filter_obj = factory(field=key, text=text)
                else:
                    raise Exception(f"Unknown filter type: {filter_type}")
                    
                filters.append(filter_obj)
                
            except Exception as e:
                raise Exception(f"Error creating filter object: {str(e)}")
        
        return filters
