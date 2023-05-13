from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
import re
from domain.logger import Logger
from domain.common import Common

from infrastructure.common import CommonInfrastructure
from infrastructure.generic_classes import GenericDatastructure
from infrastructure.generic_classes import GenericSubDataStructure

class LanguageDependent(ABC):
    @abstractmethod
    def get_skip_types(self) -> List[str]:
        """
        """

class PythonLanguage(LanguageDependent):
    def __init__(self, logger: Logger):
        self.logger = logger

    def get_skip_types(self) -> List[str]:
        return ['int', 'str', 'float', 'bool', 'abc.ABC', 'double']

class Datastructure(GenericDatastructure):
    NOT_EXTRACTED: str = '** Not extracted **'

    STATICS: str = 'statics'
    METHODS: str = 'methods'
    VARIABLES: str = 'variables'

    @dataclass
    class Method:
        method_name: str
        @dataclass
        class ParameterType:
            parameter: str
            user_type: str
        @dataclass
        class MethodVariable:
            variable_name: str
            variable_type: str
        parameters: List[ParameterType]
        is_private: bool
        variables: List[MethodVariable]

    @dataclass
    class Static:
        static_name: str
        static_type: str

    @dataclass
    class Variable:
        variable_name: str
        variable_type: str
        is_member: bool
        is_private: bool

    class SubDataStructure(GenericSubDataStructure):


        def __init__(self, filename: str, filemodule: str, from_imports: Dict[str, str], \
                fqdn_class_name: str, name_space_list: List[str], logger: Logger):
            self.fqdn_class_name: str = fqdn_class_name
            self.filename: str = filename
            self.from_imports: str = from_imports.copy()
            self.filemodule: str = filemodule
            self.name_space_list: List[str] = name_space_list

            self.bases: List[str] = []
            self.inner_classes: List[str] = []
            self.is_inner_class_field: bool = False
            self.is_abstract_field: bool = False
            self.is_interface_field: bool = False
            self.statics: List[Datastructure.Static] = []
            self.variables: List[Datastructure.Variable] = []
            self.methods: List[Datastructure.Method] = []
            self.logger = logger
            self.color = None
            self.default_color = None
        
        def set_abstract(self) -> None:
            self.is_abstract_field = True

        def set_inner_class(self) -> None:
            self.is_inner_class_field = True

        def set_interface(self) -> None:
            self.is_interface_field = True

        def set_color(self, color: str) -> None:
            self.color = f'#{color}'
        def set_default_color(self, color: str) -> None:
            self.set_color(color)
            self.default_color = self.color
        def clear_color(self) -> None:
            self.color = self.default_color
        def get_color(self) -> str:
            return self.color
    
        def add_base_class(self, base_class: str, add_no_module: bool = False) -> None:
            if base_class in self.from_imports.keys():
                base_class = self.from_imports[base_class]
            elif add_no_module:
                self.logger.log_debug(f'  Created base class name {base_class} as is from filemodule: >{self.filemodule}< and >{base_class}<')
            else:
                base_class = f'{self.filemodule}.{base_class}'
                self.logger.log_debug(f'  Created base class name {base_class} from filemodule: >{self.filemodule}< and >{base_class}<')
            self.bases.append(base_class)
 
        def add_static(self, static_name: str, static_type: str) -> None:
            self.statics.append(Datastructure.Static(static_name, static_type))
        def add_method(self, method_name: str, arguments_tuple: List[Tuple[str, str]], is_private: bool, method_variables_tuple: List[Tuple[str, str]] = None) -> None:
            arguments = [Datastructure.Method.ParameterType(parameter, user_type) for parameter, user_type in arguments_tuple]
            method_variables = [Datastructure.Method.MethodVariable(variable_name, variable_type) for variable_name, variable_type in method_variables_tuple]
            self.methods.append(Datastructure.Method(method_name, arguments, is_private, method_variables))
        def add_variable(self, variable_name: str, variable_type: str, is_member: bool, is_private = False) -> None:
            self.variables.append(Datastructure.Variable(variable_name, variable_type, is_member, is_private))
        def add_inner_class(self, inner_class_name: str) -> None:
            self.inner_classes.append(inner_class_name)

        def is_abstract(self) -> bool:
            return self.is_abstract_field
        def is_interface(self) -> bool:
            return self.is_interface_field
        def is_inner_class(self) -> bool:
            return self.is_inner_class_field

        def has_static_fields(self) -> bool:
            return len(self.statics) > 0
        def has_method_fields(self) -> bool:
            return len(self.methods) > 0
        def has_variables_fields(self) -> bool:
            return len(self.variables) > 0

        def get_fqdn_class_name(self) -> str:
            return self.fqdn_class_name

        def get_base_classes(self) -> List[str]:
            return self.bases
        def get_static_fields(self) -> List[Datastructure.Static]:
            return self.statics
        def get_method_fields(self) -> List[Datastructure.Method]:
            return self.methods
        def get_variable_fields(self) -> List[Datastructure.Variable]:
            return self.variables
        def get_inner_class_name(self) -> List[str]:
            return self.inner_classes
        def get_filename(self) -> str:
            return self.filename
        def get_filemodule(self) -> str:
            return self.filemodule
        def get_name_space_list(self) -> None:
            return self.name_space_list

    def __init__(self, language_dependent: LanguageDependent, logger: Logger):
        self.class_to_datastructure: Dict[str, Datastructure.SubDataStructure] = {}
        self.filename_to_datastructure: Dict[str, List[Datastructure.SubDataStructure]] = {}
        self.namespace_to_datastructures: Dict[str, List[Datastructure.SubDataStructure]] = {}
        self.namespace_to_namespace_list: Dict[str, List[str]] = {}
        self.language_dependent = language_dependent
        self.skip_types = language_dependent.get_skip_types()
        self.skip_types.append(self.NOT_EXTRACTED)
        self.skip_types.append(Common.COMPLEX_TYPE)
        self.skip_types.append(CommonInfrastructure.NOT_PROVIDED_TYPE)
        self.logger = logger

    def clear_color(self) -> None:
        for sub_datastructure in self.class_to_datastructure.values():
            sub_datastructure.clear_color()

    def set_color_class_name_list(self, class_name_list: List[str], color: str) -> None:
        for class_name in class_name_list:
            sub_datastructure = self.get_datastructures_from_class_name(class_name)
            sub_datastructure.set_color(color)

    def get_skip_types(self) -> List[str]:
        return self.skip_types

    def get_language_dependent(self) -> LanguageDependent:
        return self.language_dependent

    def append_class(self, filename: str, filemodule: str, \
          from_imports: Dict[str, str], fqdn_class_name: str,\
            name_space_list: List[str]) -> Datastructure.SubDataStructure:
        sub_datastructure = Datastructure.SubDataStructure(filename, filemodule, from_imports, fqdn_class_name, name_space_list, self.logger)
        self.append_sub_datastructure(sub_datastructure)
        return sub_datastructure

    def get_classname_list(self) -> List[str]:
        return self.class_to_datastructure.keys()

    def get_datastructures_from_class_name(self, class_name: str) -> Datastructure.SubDataStructure:
        if class_name in self.class_to_datastructure:
            return self.class_to_datastructure[class_name]
        self.logger.log_debug(f"Requested class {class_name} was not found in the datastructure")
        return None

    def get_sorted_name_spaces(self) -> List[str]:
        return sorted(self.namespace_to_datastructures.keys())

    def get_datastructures_from_namespace(self, namespace: str) -> List[Datastructure.SubDataStructure]:
        return self.namespace_to_datastructures[namespace]

    def get_namespace_list_from_namespace_name(self, namespace_name: str) -> List[str]:
        return self.namespace_to_namespace_list[namespace_name]

    def class_exists(self, class_name) -> bool:
        return class_name in self.class_to_datastructure.keys()

    def filename_exists(self, filename) -> bool:
        return filename in self.filename_to_datastructure.keys()

    def append_sub_datastructure(self, sub_datastructure: Datastructure.SubDataStructure) -> None:
        fqdn_class_name = sub_datastructure.get_fqdn_class_name()
        if fqdn_class_name not in self.class_to_datastructure.keys():
            self.class_to_datastructure[fqdn_class_name] = sub_datastructure
            namespace = '.'.join(sub_datastructure.get_name_space_list())
            if namespace not in self.namespace_to_datastructures:
                self.namespace_to_datastructures[namespace] = []
            self.namespace_to_datastructures[namespace].append(sub_datastructure)
            self.namespace_to_namespace_list[namespace] = sub_datastructure.get_name_space_list()
        else:
            self.logger.log_debug(f'WARNING: Class {fqdn_class_name} is being registered a second time \n' + \
                  f'   -> First time content is from file {self.class_to_datastructure[fqdn_class_name].get_filename()}, from class: {self.class_to_datastructure[fqdn_class_name].get_fqdn_class_name()}: Ignoring.')
            #traceback.print_stack()

class DatastructureHandler:
    def __init__(self, datastructure: Datastructure, logger: Logger):
        self.datastructure = datastructure
        self.logger = logger

    def __append_sub_datastructures_from_classname(self, classname: str, \
                reduced_datastructure: Datastructure) -> Datastructure.SubDataStructure:
        #type_wo_namespace: str = re.sub('^.*\.', '', classname)
        if classname not in self.datastructure.get_skip_types():
            sub_datastructure: Datastructure.SubDataStructure = self.datastructure.get_datastructures_from_class_name(classname)
            if sub_datastructure is not None:
                reduced_datastructure.append_sub_datastructure(sub_datastructure)
                self.logger.log_debug(f'  Appended sub datastructure of {sub_datastructure.get_fqdn_class_name()}')
                return sub_datastructure
            else:
                self.logger.log_debug(f'  Could not find internal sub_datastructure for class {classname}')
        else:
            self.logger.log_debug(f'  {classname} was skipped because it belongs to the skipped types {self.datastructure.get_skip_types()}')
        
        return None

    def __add_class_to_reduced_datastructure_if_not_exist(self, \
               class_name: str, reduced_datastructure: Datastructure) -> Datastructure.SubDataStructure:
        if self.datastructure.class_exists(class_name):
            return self.__append_sub_datastructures_from_classname(class_name, reduced_datastructure)
        return None

    def create_reduced_class_list_from_class_name_list(self, class_name_list: List[str]) -> Datastructure:
        self.datastructure.clear_color()
        reduced_datastructure: Datastructure = Datastructure(self.datastructure.get_language_dependent(), self.logger)
        self.logger.log_debug(f'create_reduced_class_list_from_class_name_list(class_name_list = {class_name_list})')

        for class_name in class_name_list:
            self.logger.log_debug(f' Adding class {class_name}')
            sub_datastructure: Datastructure.SubDataStructure = \
                self.__add_class_to_reduced_datastructure_if_not_exist(class_name, reduced_datastructure)
            if sub_datastructure is not None:
                sub_datastructure.set_color('yellow')
                self.logger.log_debug(f'  All base classes for class {class_name} are: {sub_datastructure.get_base_classes()})')
                for base_class_name in sub_datastructure.get_base_classes():
                    self.__append_sub_datastructures_from_classname(\
                        base_class_name, reduced_datastructure)
                    self.logger.log_debug(f' Adding parent class {base_class_name} of {class_name}')
                    self.logger.log_debug(f'  All reduced base classes for {class_name}: {reduced_datastructure.get_datastructures_from_class_name(class_name).get_base_classes()})')

                static_field: Datastructure.Static
                self.logger.log_debug(f'  All static fields for class {class_name} are: {[f"{static_field.static_name}:{static_field.static_type}" for static_field in sub_datastructure.get_static_fields()]})')
                for static_field in sub_datastructure.get_static_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(static_field.static_type)
                    self.__append_sub_datastructures_from_classname(\
                        reduced_member_type, reduced_datastructure)
                    self.logger.log_debug(f' Adding static related class {reduced_member_type} of {class_name}')

                variable_field: Datastructure.Variable
                self.logger.log_debug(f'  All variable fields for class {class_name} are: {[f"{variable_field.variable_name}:{variable_field.variable_type}" for variable_field in sub_datastructure.get_variable_fields()]})')
                for variable_field in sub_datastructure.get_variable_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(variable_field.variable_type)
                    self.__append_sub_datastructures_from_classname(\
                        reduced_member_type, reduced_datastructure)
                    self.logger.log_debug(f' Adding variable related class {reduced_member_type} of {class_name}')

                method_field: Datastructure.Method
                self.logger.log_debug(f'  All methods for class {class_name} are: {[f"{method_field.method_name}" for method_field in sub_datastructure.get_method_fields()]})')
                for method_field in sub_datastructure.get_method_fields():
                    self.logger.log_debug(f'    All parameters for method {class_name}.{method_field.method_name} are: {[f"{parameter.parameter}:{parameter.user_type}" for parameter in method_field.parameters]})')
                    for parameter in method_field.parameters:
                        _, reduced_member_type, _ = Common.reduce_member_type(parameter.user_type)
                        self.__append_sub_datastructures_from_classname(\
                            reduced_member_type, reduced_datastructure)
                        self.logger.log_debug(f' {parameter.parameter}:{parameter.user_type} (reduced to {reduced_member_type}) is a parameter from method {method_field.method_name} from class {sub_datastructure.get_fqdn_class_name()} ')
                    self.logger.log_debug(f'    All local variables for method {class_name}.{method_field.method_name} are: {[f"{variable.variable_name}:{variable.variable_type}" for variable in method_field.variables]})')
                    for variable in method_field.variables:
                        _, reduced_member_type, _ = Common.reduce_member_type(variable.variable_type)
                        self.__append_sub_datastructures_from_classname(\
                            reduced_member_type, reduced_datastructure)
                        self.logger.log_debug(f' {variable.variable_name}:{variable.variable_type} (reduced to {reduced_member_type}) is a variable from method {method_field.method_name} from class {sub_datastructure.get_fqdn_class_name()} ')

                self.logger.log_debug(f'  All inner classes for class {class_name} are: {sub_datastructure.get_inner_class_name()})')
                for inner_class_name in sub_datastructure.get_inner_class_name():
                    _, reduced_member_type, _ = Common.reduce_member_type(inner_class_name)
                    self.__append_sub_datastructures_from_classname(\
                        reduced_member_type, reduced_datastructure)
                    self.logger.log_debug(f' Adding inner class {reduced_member_type} of {class_name}')
        
        self.logger.log_debug(f'Analyzing all classes referencing {class_name}')
        for namespace_name in self.datastructure.get_sorted_name_spaces():
            for sub_datastructure in self.datastructure.get_datastructures_from_namespace(namespace_name):

                for base_classname in sub_datastructure.get_base_classes():
                    if base_classname in class_name_list:
                        self.logger.log_debug(f' Adding child related class {sub_datastructure.get_fqdn_class_name()} of {base_classname}')
                        self.__append_sub_datastructures_from_classname(\
                            sub_datastructure.get_fqdn_class_name(), reduced_datastructure)

                static_field: Datastructure.Static
                for static_field in sub_datastructure.get_static_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(static_field.static_type)
                    if reduced_member_type in class_name_list:
                        self.logger.log_debug(f' Adding {static_field.static_name}.{reduced_member_type} which is a static related class of {sub_datastructure.get_fqdn_class_name()} ')
                        self.__append_sub_datastructures_from_classname(\
                            sub_datastructure.get_fqdn_class_name(), reduced_datastructure)

                variable_field: Datastructure.Variable
                for variable_field in sub_datastructure.get_variable_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(variable_field.variable_type)
                    if reduced_member_type in class_name_list:
                        self.logger.log_debug(f' Adding {variable_field.variable_name}:{variable_field.variable_type} (reduced to {reduced_member_type}) which is a variable related class of {sub_datastructure.get_fqdn_class_name()} ')
                        self.__append_sub_datastructures_from_classname(\
                            sub_datastructure.get_fqdn_class_name(), reduced_datastructure)

                method_field: Datastructure.Method
                for method_field in sub_datastructure.get_method_fields():
                    for parameter in method_field.parameters:
                        _, reduced_member_type, _ = Common.reduce_member_type(parameter.user_type)
                        if reduced_member_type in class_name_list:
                            self.logger.log_debug(f' Adding {reduced_member_type} which is a parameter from method {method_field.method_name} related class of {sub_datastructure.get_fqdn_class_name()} ')
                            self.__append_sub_datastructures_from_classname(\
                                sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                    for variable in method_field.variables:
                        _, reduced_member_type, _ = Common.reduce_member_type(variable.variable_type)
                        if reduced_member_type in class_name_list:
                            self.logger.log_debug(f' Adding {variable.variable_name}:{variable.variable_type} (reduced to {reduced_member_type}) which is a local variable from method {method_field.method_name} from class {sub_datastructure.get_fqdn_class_name()} ')
                            self.__append_sub_datastructures_from_classname(\
                                reduced_member_type, reduced_datastructure)

                for inner_class_name in sub_datastructure.get_inner_class_name():
                    _, reduced_member_type, _ = Common.reduce_member_type(inner_class_name)
                    if reduced_member_type in class_name_list:
                        self.logger.log_debug(f' Adding {reduced_member_type} contains class of {sub_datastructure.get_fqdn_class_name()} ')
                        self.__append_sub_datastructures_from_classname(\
                            sub_datastructure.get_fqdn_class_name(), reduced_datastructure)

        return reduced_datastructure

    def get_class_name_list_grouped_by_namespaces(self) -> Dict[List[str]]:
        class_name_list_grouped_by_namespaces: Dict[List[str]] = {}
        for namespace_name in self.datastructure.get_sorted_name_spaces():
            for sub_datastructure in self.datastructure.get_datastructures_from_namespace(namespace_name):
                classname: str = sub_datastructure.get_fqdn_class_name()
                namespace_list = classname.split('.')[0: -1]
                full_name_space = ''
                for namespace in namespace_list:
                    if len(full_name_space) > 0: full_name_space += '.'
                    full_name_space += namespace
                    if full_name_space not in class_name_list_grouped_by_namespaces.keys():
                       class_name_list_grouped_by_namespaces[full_name_space] = []
        for namespace in class_name_list_grouped_by_namespaces.keys():
            for classname in self.datastructure.get_classname_list():
                if classname.startswith(namespace):
                    class_name_list_grouped_by_namespaces[namespace].append(classname)
        return class_name_list_grouped_by_namespaces