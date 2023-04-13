from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
import ast
import yaml
import pprint
from infrastructure.generic_classes import GenericSubDataStructure
from infrastructure.generic_classes import GenericDatastructure
from infrastructure.generic_classes import GenericSaver
from infrastructure.generic_classes import GenericLogger
from infrastructure.common import CommonInfrastructure
 # pip install pyyaml
class YAMLAdapter:
    def __init__(self, saver: GenericSaver, logger: GenericLogger):
        self.saver = saver
        self.logger = logger

    @staticmethod
    def __check_boolean(value_dict: dict, key: str):
        if key in value_dict:
            value = value_dict[key]
            if isinstance(value, bool):
                return value
            assert isinstance(value, str)
            return value.lower() == 'true'
        return False

    def read(self, datastructure: GenericDatastructure, filename: str, from_dir: str) -> any:
        with open(filename, encoding="utf-8") as stream:
            yaml_content: dict = yaml.safe_load(stream)
            self.logger.log_trace(f"Filename: {filename}")
            self.logger.log_trace(pprint.pformat(yaml_content))
            self.logger.log_trace("\n\n\n\n")
        for sub_datastructure_yaml in yaml_content:
            self.logger.log_trace("See below content of sub_datastructure_yaml: ")
            self.logger.log_trace(pprint.pformat(sub_datastructure_yaml))
            value_dict = sub_datastructure_yaml['sub_datastructure']
            from_imports: Dict[str, str] = {}
            for from_import in value_dict['from_imports']:
                from_imports[from_import['imported_class_name']] = \
                    from_import['namespace_path']
            sub_datastructure: GenericSubDataStructure = \
                datastructure.append_class(\
                    value_dict['filename'], value_dict['filemodule'],\
                        from_imports, value_dict['fqdn_class_name'],\
                            value_dict['filemodule'].split('.'))
            if YAMLAdapter.__check_boolean(value_dict, 'is_abstract'):
                self.logger.log_trace(f"value_dict['is_abstract']: {value_dict['is_abstract']}")
                sub_datastructure.set_abstract()
            if YAMLAdapter.__check_boolean(value_dict, 'is_inner_class'):
                self.logger.log_trace(f"value_dict['is_inner_class']: {value_dict['is_inner_class']}")
                sub_datastructure.set_inner_class()
            if YAMLAdapter.__check_boolean(value_dict, 'is_interface'):
                self.logger.log_trace(f"value_dict['is_interface']: {value_dict['is_interface']}")
                sub_datastructure.set_interface()
            for base_class in value_dict['base_classes']:
                sub_datastructure.add_base_class(base_class, True)
            for anonymous_call_type in value_dict['anonymous_calls']:
                sub_datastructure.add_variable(\
                    'anonymous_call', anonymous_call_type, False)
            for inner_class_name in value_dict['inner_classes']:
                sub_datastructure.add_inner_class(inner_class_name)
            for variable in value_dict['variables']:
                sub_datastructure.add_variable(\
                    variable['variable_name'],
                    variable['variable_type'],
                    variable['is_member'] == True)
            for static in value_dict['statics']:
                sub_datastructure.add_static(\
                    static['static_name'],
                    static['static_type']
                    )
            for method in value_dict['methods']:
                parameters: List[Tuple[str, str]] = []
                for parameter in method['parameters']:
                    parameters.append(\
                        (parameter['parameter_name'], \
                            parameter['parameter_type']))
                method_variables: List[Tuple[str, str]] = []
                for method_variable in method['method_variables']:
                    method_variables.append(\
                        (method_variable['variable_name'], \
                            method_variable['variable_type']))
                sub_datastructure.add_method(\
                    method['method_name'], \
                        parameters, \
                            method['is_private'] == 'True', method_variables)
            
