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
    @abstractmethod
    def get_package_name(self, parameters: List[str]) -> str:
        """
        """

class PythonLanguage(LanguageDependent):
    def __init__(self, logger: Logger):
        self.logger = logger

    def get_skip_types(self) -> List[str]:
        return ['int', 'str', 'float', 'bool', 'abc.ABC']

    def __get_package_name_from_filename(self, filename: str, from_dir: str) -> str:
        if from_dir is not None:
            filename = filename.replace(from_dir, '')
        return re.sub('^\.', '', re.sub('\.py$', '', filename.replace('/', '.')))

    def get_package_name(self, parameters: List[str]) -> str:
        if len(parameters) != 2:
            self.logger.log_error("get_package_name for Python requires 2 parameters: filename and from_dir.")
            exit(1)
        return self.__get_package_name_from_filename(parameters[0], parameters[1])

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
        parameters: List[ParameterType]

    @dataclass
    class Static:
        static_name: str
        static_type: str

    @dataclass
    class Variable:
        variable_name: str
        variable_type: str
        is_member: bool

    class SubDataStructure(GenericSubDataStructure):
        def __init__(self, filename: str, filemodule: str, from_imports: Dict[str, str], fqdn_class_name: str, logger: Logger):
            self.fqdn_class_name: str = fqdn_class_name
            self.filename: str = filename
            self.from_imports: str = from_imports.copy()
            self.filemodule: str = filemodule

            self.bases: List[str] = []
            self.inner_classes: List[str] = []
            self.is_abstract_field: bool = False
            self.statics: List[Datastructure.Static] = []
            self.variables: List[Datastructure.Variable] = []
            self.methods: List[Datastructure.Method] = []

            self.logger = logger
        
        def set_abstract(self) -> None:
            self.is_abstract_field = True
    
        def add_base_class(self, base_class: str) -> None:
            if base_class in self.from_imports.keys():
                base_class = self.from_imports[base_class]
            else:
                base_class = f'{self.filemodule}.{base_class}'
                self.logger.log_debug(f'  Created base class name {base_class} from filemodule: >{self.filemodule}< and >{base_class}<')
            self.bases.append(base_class)
 
        def add_static(self, static_name: str, static_type: str) -> None:
            self.statics.append(Datastructure.Static(static_name, static_type))
        def add_method(self, method_name: str, arguments_tuple: List[Tuple[str, str]]) -> None:
            arguments = [Datastructure.Method.ParameterType(parameter, user_type) for parameter, user_type in arguments_tuple]
            self.methods.append(Datastructure.Method(method_name, arguments))
        def add_variable(self, variable_name: str, variable_type: str, is_member: bool) -> None:
            self.variables.append(Datastructure.Variable(variable_name, variable_type, is_member))
        def add_inner_class(self, inner_class_name: str) -> None:
            self.inner_classes.append(inner_class_name)

        def is_abstract(self) -> bool:
            return self.is_abstract_field
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
        def get_filename(self) -> str:
            return self.filename
        def get_filemodule(self) -> str:
            return self.filemodule

    def __init__(self, language_dependent: LanguageDependent, logger: Logger):
        self.class_to_datastructure: Dict[str, Datastructure.SubDataStructure] = {}
        self.filename_to_datastructure: Dict[str, List[Datastructure.SubDataStructure]] = {}
        self.language_dependent = language_dependent
        self.skip_types = language_dependent.get_skip_types()
        self.skip_types.append(self.NOT_EXTRACTED)
        self.skip_types.append(Common.COMPLEX_TYPE)
        self.skip_types.append(CommonInfrastructure.NOT_PROVIDED_TYPE)
        self.logger = logger

    def get_skip_types(self) -> List[str]:
        return self.skip_types

    def get_package_name(self, parameters: List[str]):
        return self.language_dependent.get_package_name(parameters)

    def get_language_dependent(self) -> LanguageDependent:
        return self.language_dependent

    def append_class(self, filename: str, filemodule: str, from_imports: Dict[str, str], fqdn_class_name: str) -> Datastructure.SubDataStructure:
        sub_datastructure = Datastructure.SubDataStructure(filename, filemodule, from_imports, fqdn_class_name, self.logger)
        self.append_sub_datastructure(sub_datastructure)
        return sub_datastructure

    def get_sorted_list_filenames(self) -> List[str]:
        return sorted(self.filename_to_datastructure.keys())

    def get_classname_list(self) -> List[str]:
        return self.class_to_datastructure.keys()

    def get_datastructures_from_filename(self, filename: str) -> List[Datastructure.SubDataStructure]:
        return self.filename_to_datastructure[filename]

    def get_datastructures_from_class_name(self, class_name: str) -> Datastructure.SubDataStructure:
        if class_name in self.class_to_datastructure:
            return self.class_to_datastructure[class_name]
        self.logger.log_debug(f"Requested class {class_name} was not found in the datastructure")
        return None

    def class_exists(self, class_name) -> bool:
        return class_name in self.class_to_datastructure.keys()

    def filename_exists(self, filename) -> bool:
        return filename in self.filename_to_datastructure.keys()

    def append_sub_datastructure(self, sub_datastructure: Datastructure.SubDataStructure) -> None:
        filename = sub_datastructure.get_filename()
        fqdn_class_name = sub_datastructure.get_fqdn_class_name()
        if fqdn_class_name not in self.class_to_datastructure.keys():
            self.class_to_datastructure[fqdn_class_name] = sub_datastructure
            if filename not in self.filename_to_datastructure.keys():
                self.filename_to_datastructure[filename] = []
            self.filename_to_datastructure[filename].append(self.class_to_datastructure[fqdn_class_name])
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
                self.logger.log_debug(f'  Could not find sub_datastructure for class {classname}')
        self.logger.log_debug(f'  {classname} was skipped because it belongs to the skipped types {self.datastructure.get_skip_types()}')
        
        return None

    def __add_class_to_reduced_datastructure_if_not_exist(self, \
               class_name: str, reduced_datastructure: Datastructure) -> Datastructure.SubDataStructure:
        if self.datastructure.class_exists(class_name):
            return self.__append_sub_datastructures_from_classname(class_name, reduced_datastructure)
        return None

    def create_reduced_class_list_from_class_name_list(self, class_name_list: List[str]) -> Datastructure:
        reduced_datastructure: Datastructure = Datastructure(self.datastructure.get_language_dependent(), self.logger)
        self.logger.log_debug(f'create_reduced_class_list_from_class_name_list(class_name_list = {class_name_list})')

        for class_name in class_name_list:
            self.logger.log_debug(f' Adding class {class_name}')
            sub_datastructure: Datastructure.SubDataStructure = \
                self.__add_class_to_reduced_datastructure_if_not_exist(class_name, reduced_datastructure)
            if sub_datastructure is not None:
                for base_class_name in sub_datastructure.get_base_classes():
                    self.__append_sub_datastructures_from_classname(\
                        base_class_name, reduced_datastructure)
                    self.logger.log_debug(f' Adding parent class {base_class_name} of {class_name}')
                    self.logger.log_debug(f'  All reduced base classes for {class_name}: {reduced_datastructure.get_datastructures_from_class_name(class_name).get_base_classes()})')

                static_field: Datastructure.Static
                for static_field in sub_datastructure.get_static_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(static_field.static_type)
                    self.__append_sub_datastructures_from_classname(\
                        reduced_member_type, reduced_datastructure)
                    self.logger.log_debug(f' Adding static related class {reduced_member_type} of {class_name}')

                variable_field: Datastructure.Variable
                for variable_field in sub_datastructure.get_variable_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(variable_field.variable_type)
                    self.__append_sub_datastructures_from_classname(\
                        reduced_member_type, reduced_datastructure)
                    self.logger.log_debug(f' Adding variable related class {reduced_member_type} of {class_name}')

                method_field: Datastructure.Method
                for method_field in sub_datastructure.get_method_fields():
                    for parameter in method_field.parameters:
                        _, reduced_member_type, _ = Common.reduce_member_type(parameter.user_type)
                        self.__append_sub_datastructures_from_classname(\
                            reduced_member_type, reduced_datastructure)
                        self.logger.log_debug(f' {reduced_member_type} is a parameter from method {method_field.method_name} from class {sub_datastructure.get_fqdn_class_name()} ')

                for inner_class_name in sub_datastructure.get_inner_class_name():
                    _, reduced_member_type, _ = Common.reduce_member_type(inner_class_name)
                    self.__append_sub_datastructures_from_classname(\
                        reduced_member_type, reduced_datastructure)
                    self.logger.log_debug(f' Adding inner class {reduced_member_type} of {class_name}')

        for filename in self.datastructure.get_sorted_list_filenames():
            for sub_datastructure in self.datastructure.get_datastructures_from_filename(filename):

                for base_classname in sub_datastructure.get_base_classes():
                    if base_classname in class_name_list:
                        self.__append_sub_datastructures_from_classname(\
                            sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                        self.logger.log_debug(f' Adding child related class {sub_datastructure.get_fqdn_class_name()} of {base_classname}')

                static_field: Datastructure.Static
                for static_field in sub_datastructure.get_static_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(static_field.static_type)
                    if reduced_member_type in class_name_list:
                        self.__append_sub_datastructures_from_classname(\
                            sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                        self.logger.log_debug(f' {reduced_member_type} is a static related class of {sub_datastructure.get_fqdn_class_name()} ')

                variable_field: Datastructure.Variable
                for variable_field in sub_datastructure.get_variable_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(variable_field.variable_type)
                    if reduced_member_type in class_name_list:
                        self.__append_sub_datastructures_from_classname(\
                            sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                        self.logger.log_debug(f' {reduced_member_type} is a variable related class of {sub_datastructure.get_fqdn_class_name()} ')

                method_field: Datastructure.Method
                for method_field in sub_datastructure.get_method_fields():
                    for parameter in method_field.parameters:
                        _, reduced_member_type, _ = Common.reduce_member_type(parameter.user_type)
                        if reduced_member_type in class_name_list:
                            self.__append_sub_datastructures_from_classname(\
                                sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                            self.logger.log_debug(f' {reduced_member_type} is a parameter from method {method_field.method_name} related class of {sub_datastructure.get_fqdn_class_name()} ')

                for inner_class_name in sub_datastructure.get_inner_class_name():
                    _, reduced_member_type, _ = Common.reduce_member_type(inner_class_name)
                    if reduced_member_type in class_name_list:
                        self.__append_sub_datastructures_from_classname(\
                            sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                        self.logger.log_debug(f' {reduced_member_type} contains class of {sub_datastructure.get_fqdn_class_name()} ')

        return reduced_datastructure

    def get_class_name_list_grouped_by_namespaces(self) -> Dict[List[str]]:
        class_name_list_grouped_by_namespaces: Dict[List[str]] = {}
        for filename in self.datastructure.get_sorted_list_filenames():
            for sub_datastructure in self.datastructure.get_datastructures_from_filename(filename):
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