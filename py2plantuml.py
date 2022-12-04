from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
import os
import re
import ast
import sys
import os
import re
import argparse
import traceback
from pathlib import Path
from pprint import pprint


class Logger:
    DEBUG = False
    @staticmethod
    def set_debug() -> None:
        Logger.DEBUG = True
    @staticmethod
    def log_info(line: str) -> None:
        print(line)

    @staticmethod
    def log_debug(line: str) -> None:
        if Logger.DEBUG:
            print(f'{line}')

class Saver:
    def __init__(self, out_dir: str, saver: Saver = None):
        self.lines_to_save: List[str] = []
        self.out_dir: str = out_dir
        if saver is not None:
            self.lines_to_save = saver.copy_content()

    def append(self, line: str) -> Saver:
        self.lines_to_save.append(line)
        return self

    def copy_content(self) -> List[str]:
        return self.lines_to_save.copy()

    def save(self, filename) -> None:
        filename = os.path.join(self.out_dir, filename)
        Logger.log_info(f'INFO: Creating file {filename}')
        with open(filename, 'w', encoding="utf-8") as file:
            file.write('\n'.join(self.lines_to_save))

    def clone(self) -> Saver:
        return Saver(self.out_dir, self)

    def removed_last_line_if_same(self, line: str) -> bool:
        return_value = False
        old_value = None if len(self.lines_to_save) == 0 else self.lines_to_save[-1]

        if len(self.lines_to_save) > 0 and line == self.lines_to_save[-1]:
            self.lines_to_save.pop()
            return_value = True
        self.lines_to_save.append(f'\'Compared {line} with last element of {old_value}' )
        return return_value

class Common:
    COMPLEX_TYPE: str = '*** TYPE NOT DECODED ***'
    NOT_PROVIDED_TYPE: str = '**???**'
    @staticmethod
    def reduce_member_type(member_type: str, is_member: bool = True) -> Tuple[str, str, str]:
        connection: str = '*--' if is_member else '--'
        note: str = ''
        if member_type.startswith('List['):
            member_type=member_type[5:-1]
            connection = f'"many" {connection} "1"'
            note = ': (list)'
        elif member_type.startswith('Set['):
            member_type=member_type[4:-1]
            connection = f'"many" {connection} "1"'
            note = ': (set)'
        elif 1 in [ c in member_type for c in '[{(,)}]' ]:
            member_type=Common.COMPLEX_TYPE
            note = ': (complex type)'
        if not is_member:
            if len(note) == 0: note += ' :'
            note += ' uses '
        return connection, member_type, note

class LanguageDependent(ABC):
    @abstractmethod
    def get_skip_types(self) -> List[str]:
        """
        """

class PythonLanguage(LanguageDependent):
    def __init__(self):
        pass

    def get_skip_types(self) -> List[str]:
        return ['int', 'str', 'float', 'bool', 'abc.ABC']


class Datastructure:
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

    class SubDataStructure:
        def __init__(self, filename: str, filemodule: str, from_imports: Dict[str, str], fqdn_class_name: str):
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
        
        def set_abstract(self) -> None:
            self.is_abstract_field = True
    
        def add_base_class(self, base_class: str) -> None:
            if base_class in self.from_imports.keys():
                base_class = self.from_imports[base_class]
            else:
                base_class = self.filemodule + base_class
            self.bases.append(base_class)
 
        def add_static(self, static_name: str, static_type: str) -> None:
            self.statics.append(Datastructure.Static(static_name, static_type))
        def add_method(self, method_name: str, arguments: List[Datastructure.Method.ParameterType]) -> None:
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


        def clone(self) -> Datastructure.SubDataStructure:
            sub_datastructure: Datastructure.SubDataStructure = \
                Datastructure.SubDataStructure(self.filename, self.filemodule, self.from_imports.copy(), self.fqdn_class_name)

            sub_datastructure.is_abstract_field = self.is_abstract_field
            sub_datastructure.bases = self.bases[:]
            sub_datastructure.statics = self.statics[:]
            sub_datastructure.methods = self.methods[:]
            sub_datastructure.variables = self.variables[:]
            sub_datastructure.inner_classes = self.inner_classes[:]
            
            return sub_datastructure

    def __init__(self, language_dependent: LanguageDependent):
        self.class_to_datastructure: Dict[str, Datastructure.SubDataStructure] = {}
        self.filename_to_datastructure: Dict[str, List[Datastructure.SubDataStructure]] = {}
        self.language_dependent = language_dependent
        self.skip_types = language_dependent.get_skip_types()
        self.skip_types.append(self.NOT_EXTRACTED)
        self.skip_types.append(Common.COMPLEX_TYPE)
        self.skip_types.append(Common.NOT_PROVIDED_TYPE)

    def get_skip_types(self):
        return self.skip_types

    def get_language_dependent(self) -> LanguageDependent:
        return self.language_dependent

    def append_class(self, filename: str, filemodule: str, from_imports: Dict[str, str], fqdn_class_name: str) -> Datastructure.SubDataStructure:
        sub_datastructure = Datastructure.SubDataStructure(filename, filemodule, from_imports, fqdn_class_name)
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
            Logger.log_debug(f'WARNING: Class {fqdn_class_name} is being registered a second time \n' + \
                  f'   -> First time content is from file {self.class_to_datastructure[fqdn_class_name].get_filename()}, from class: {self.class_to_datastructure[fqdn_class_name].get_fqdn_class_name()}: Ignoring.')
            #traceback.print_stack()

class DatastructureHandler:
    @staticmethod
    def __append_sub_datastructures_from_classname(\
                from_datastructure: Datastructure, classname: str, \
                reduced_datastructure: Datastructure) -> Datastructure.SubDataStructure:
        #type_wo_namespace: str = re.sub('^.*\.', '', classname)
        if classname not in from_datastructure.get_skip_types():
            sub_datastructure: Datastructure.SubDataStructure = from_datastructure.get_datastructures_from_class_name(classname)
            if sub_datastructure is not None:
                reduced_datastructure.append_sub_datastructure(sub_datastructure)
                Logger.log_debug(f'  Appended sub datastructure of {sub_datastructure.get_fqdn_class_name()}')
                return sub_datastructure
            else:
                Logger.log_debug(f'  Could not find sub_datastructure for class {classname}')
        Logger.log_debug(f'  {classname} was skipped because it belongs to the skipped types {from_datastructure.get_skip_types()}')
        
        return None

    @staticmethod
    def __add_class_to_reduced_datastructure_if_not_exist(from_datastructure: Datastructure, \
               class_name: str, reduced_datastructure: Datastructure) -> Datastructure.SubDataStructure:
        if from_datastructure.class_exists(class_name):
            return DatastructureHandler.__append_sub_datastructures_from_classname(\
                from_datastructure, class_name, reduced_datastructure)
        return None

    @staticmethod
    def create_reduced_class_list_from_class_name_list(from_datastructure: Datastructure, class_name_list: List[str]) -> Datastructure:
        reduced_datastructure: Datastructure = Datastructure(from_datastructure.get_language_dependent())
        Logger.log_debug(f'create_reduced_class_list_from_class_name_list(class_name_list = {class_name_list})')

        for class_name in class_name_list:
            Logger.log_debug(f' Adding class {class_name}')
            sub_datastructure: Datastructure.SubDataStructure = \
                DatastructureHandler.__add_class_to_reduced_datastructure_if_not_exist(\
                            from_datastructure, class_name, reduced_datastructure)
            if sub_datastructure is not None:
                for base_class_name in sub_datastructure.get_base_classes():
                    DatastructureHandler.__append_sub_datastructures_from_classname(\
                        from_datastructure, base_class_name, reduced_datastructure)
                    Logger.log_debug(f' Adding parent class {base_class_name} of {class_name}')
                    Logger.log_debug(f'  All reduced base classes for {class_name}: {reduced_datastructure.get_datastructures_from_class_name(class_name).get_base_classes()})')

                static_field: Datastructure.Static
                for static_field in sub_datastructure.get_static_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(static_field.static_type)
                    DatastructureHandler.__append_sub_datastructures_from_classname(\
                        from_datastructure, reduced_member_type, reduced_datastructure)
                    Logger.log_debug(f' Adding static related class {reduced_member_type} of {class_name}')

                variable_field: Datastructure.Variable
                for variable_field in sub_datastructure.get_variable_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(variable_field.variable_type)
                    DatastructureHandler.__append_sub_datastructures_from_classname(\
                        from_datastructure, reduced_member_type, reduced_datastructure)
                    Logger.log_debug(f' Adding variable related class {reduced_member_type} of {class_name}')

        for filename in from_datastructure.get_sorted_list_filenames():
            for sub_datastructure in from_datastructure.get_datastructures_from_filename(filename):

                for base_classname in sub_datastructure.get_base_classes():
                    if base_classname in class_name_list:
                        DatastructureHandler.__append_sub_datastructures_from_classname(\
                            from_datastructure, sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                        Logger.log_debug(f' Adding child related class {sub_datastructure.get_fqdn_class_name()} of {base_classname}')

                static_field: Datastructure.Static
                for static_field in sub_datastructure.get_static_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(static_field.static_type)
                    if reduced_member_type in class_name_list:
                        DatastructureHandler.__append_sub_datastructures_from_classname(\
                            from_datastructure, sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                        Logger.log_debug(f' {reduced_member_type} is a static related class of {sub_datastructure.get_fqdn_class_name()} ')

                variable_field: Datastructure.Variable
                for variable_field in sub_datastructure.get_variable_fields():
                    _, reduced_member_type, _ = Common.reduce_member_type(variable_field.variable_type)
                    if reduced_member_type in class_name_list:
                        DatastructureHandler.__append_sub_datastructures_from_classname(\
                            from_datastructure, sub_datastructure.get_fqdn_class_name(), reduced_datastructure)
                        Logger.log_debug(f' {reduced_member_type} is a variable related class of {sub_datastructure.get_fqdn_class_name()} ')

        return reduced_datastructure

    @staticmethod
    def get_class_name_list_grouped_by_namespaces(from_datastructure: Datastructure) -> Dict[List[str]]:
        class_name_list_grouped_by_namespaces: Dict[List[str]] = {}
        for filename in from_datastructure.get_sorted_list_filenames():
            for sub_datastructure in from_datastructure.get_datastructures_from_filename(filename):
                classname: str = sub_datastructure.get_fqdn_class_name()
                namespace_list = classname.split('.')[0: -1]
                full_name_space = ''
                for namespace in namespace_list:
                    if len(full_name_space) > 0: full_name_space += '.'
                    full_name_space += namespace
                    if full_name_space not in class_name_list_grouped_by_namespaces.keys():
                       class_name_list_grouped_by_namespaces[full_name_space] = []
        for namespace in class_name_list_grouped_by_namespaces.keys():
            for classname in from_datastructure.get_classname_list():
                if classname.startswith(namespace):
                    class_name_list_grouped_by_namespaces[namespace].append(classname)
        return class_name_list_grouped_by_namespaces

class PyAnalysis:
    DETAILED_FILENAME_SUFFIX: str           = '-diagram-detailed.puml'
    SIMPLIFIED_FILENAME_SUFFIX: str         = '-diagram-simplified.puml'
    DETAILED_PER_NS_FILE_NAME_SUFFIX: str   = '-diagram-detailed-grouped-per-namespace.puml'
    SIMPLIFIED_PER_NS_FILE_NAME_SUFFIX: str = '-diagram-simplified-grouped-per-namespace.puml'



    def __init__(self, datastructure: Datastructure):
        self.datastructure: Datastructure = datastructure
        
    @staticmethod
    def __get_file_name_from_class_namespace_name(detailed: bool, grouped_per_ns: bool, class_name: str, want_svg_file: bool) -> str:
        file_name: str = ''
        if detailed:
            if grouped_per_ns:
                file_name = f'{class_name}{PyAnalysis.DETAILED_PER_NS_FILE_NAME_SUFFIX}'
            else:
                file_name = f'{class_name}{PyAnalysis.DETAILED_FILENAME_SUFFIX}'
        else:
            if grouped_per_ns:
                file_name = f'{class_name}{PyAnalysis.SIMPLIFIED_PER_NS_FILE_NAME_SUFFIX}'
            else:
                file_name = f'{class_name}{PyAnalysis.SIMPLIFIED_FILENAME_SUFFIX}'            

        if want_svg_file:
            file_name = re.sub('puml$', 'svg', file_name)
        
        return file_name
    
    @staticmethod
    def __get_user_info(detailed: bool, grouped_per_ns: bool, class_namespace_name: str) -> str:
        user_info_detailed = 'simplified' if not detailed else 'detailed'
        user_info_svg_grouped = 'and **grouped per namespace**' if grouped_per_ns else ''
        return f'{class_namespace_name} **{user_info_detailed}** {user_info_svg_grouped}'

    @staticmethod
    def __get_file_name(detailed: bool, grouped_per_ns: bool, class_namespace_name: str = None) -> Tuple[str, str, str]:

        puml2svg = lambda file_name :  re.sub('puml$', 'svg', file_name)
        full_detailed_file_name: str            = f'full{PyAnalysis.DETAILED_FILENAME_SUFFIX}'
        full_simplified_file_name: str          = f'full{PyAnalysis.SIMPLIFIED_FILENAME_SUFFIX}'
        full_detailed_file_name_per_ns: str     = f'full{PyAnalysis.DETAILED_PER_NS_FILE_NAME_SUFFIX}'
        full_simplified_file_name_per_ns: str   = f'full{PyAnalysis.SIMPLIFIED_PER_NS_FILE_NAME_SUFFIX}'
        
        full_file_name_simplified: str = puml2svg(full_simplified_file_name)
        full_file_name_detailed: str = puml2svg(full_detailed_file_name)
        full_file_name_detailed_per_ns: str = puml2svg(full_detailed_file_name_per_ns)
        full_file_name_simplified_per_ns: str = puml2svg(full_simplified_file_name_per_ns)

        if class_namespace_name is None:
            if detailed:
                if grouped_per_ns:
                    return "Full diagram **detailed** and **grouped per namespace**", full_detailed_file_name_per_ns, \
                        "Full diagram **detailed**", full_file_name_detailed, \
                            "Full diagram **simplified** and **grouped per namespace**", full_file_name_simplified_per_ns
                else:
                    return "Full diagram **detailed**", full_detailed_file_name, \
                        "Full diagram **detailed** and **grouped per namespace**", full_file_name_detailed_per_ns, \
                            "Full diagram **simplified**", full_file_name_simplified
            else:
                if grouped_per_ns:
                    return "Full diagram **simplified** and **grouped per namespace**", full_simplified_file_name_per_ns, \
                        "Full diagram **simplified**", full_file_name_simplified, \
                            "Full diagram **detailed** and **grouped per namespace**", full_file_name_detailed_per_ns
                else:
                    return "Full diagram **simplified**", full_simplified_file_name, \
                        "Full diagram **simplified** and **grouped per namespace**", full_file_name_simplified_per_ns, \
                            "Full diagram **detailed**", full_file_name_detailed

        user_info_puml_file: str = PyAnalysis.__get_user_info(detailed, grouped_per_ns, class_namespace_name)
        puml_file: str = PyAnalysis.__get_file_name_from_class_namespace_name(detailed, grouped_per_ns, class_namespace_name, False)

        user_info_opposite_detailed_svg: str = PyAnalysis.__get_user_info(not detailed, grouped_per_ns, class_namespace_name)
        svg_file_name_opposite_detailed: str = PyAnalysis.__get_file_name_from_class_namespace_name(not detailed, grouped_per_ns, class_namespace_name, True)

        full_file_name: str = full_file_name_simplified_per_ns
        user_info_full_file_name: str = f"Full diagram **simplified** and **grouped per namespace**"

        if detailed:
            full_file_name: str = full_file_name_detailed_per_ns
            user_info_full_file_name = f"Full diagram **detailed** and **grouped per namespace**"

        return user_info_puml_file, puml_file, \
            user_info_opposite_detailed_svg, svg_file_name_opposite_detailed, \
                user_info_full_file_name, full_file_name


    @staticmethod
    def get_type(skip_types: List[str], initial_type: str, type_dict: Dict[str, str], filemodule: str) -> str:
        member_sub_type = initial_type
        if member_sub_type in type_dict.keys():
            member_sub_type = type_dict[member_sub_type]
            Logger.log_debug(f'  Type {member_sub_type} *** found *** in {type_dict.keys()} saving as type from module {member_sub_type}')
        elif member_sub_type not in skip_types:
            member_sub_type = filemodule + member_sub_type 
            Logger.log_debug(f'  Type {member_sub_type} not found in {type_dict.keys()} saving as type from module {member_sub_type}')
        return member_sub_type

    @staticmethod
    def __get_package_name_from_filename(filename: str, from_dir: str = None) -> str:
        if from_dir is not None:
            filename = filename.replace(from_dir, '')
        return re.sub('^\.', '', re.sub('py$', '', filename.replace('/', '.')))
    
    @staticmethod
    def __read_python_ast(datastructure: Datastructure, filename: str, from_dir: str, saver: Saver) -> any:
        with open(filename, encoding="utf-8") as file:
            tree: any = ast.parse(file.read())
        filemodule = PyAnalysis.__get_package_name_from_filename(filename, from_dir)
        from_import: dict = {}
        Logger.log_debug(f'Analyzing file: {filename}')
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                module_path = node.module
                for module_name in node.names:
                    from_import[module_name.name] = module_path + '.' + module_name.name

        for node in tree.body:    
            if isinstance(node, ast.ClassDef):
                class_name = f'{filemodule}{node.name}'
                class_datastructure: Datastructure.SubDataStructure = \
                    datastructure.append_class(filename, filemodule, from_import, class_name)
                Logger.log_debug(f' Creating class {class_name} from file {filename}, filemodule: {filemodule}, from_import: {from_import}')
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_class = base.id
                        if base_class == 'ABC':
                            class_datastructure.set_abstract()
                        else:
                            class_datastructure.add_base_class(base_class)
                for class_body in node.body:
                    if isinstance(class_body, ast.AnnAssign):
                        static_name: str = class_body.target.id
                        static_type: str = Datastructure.NOT_EXTRACTED
                        if isinstance(class_body.annotation, ast.Name):
                            static_type = PyAnalysis.get_type(datastructure.get_skip_types(),\
                                class_body.annotation.id, from_import, filemodule)
                            Logger.log_debug(f' Analyzing static type from file {filename}')
                        elif isinstance(class_body.annotation, ast.Subscript):
                            if isinstance(class_body.annotation.value, ast.Name) and \
                                isinstance(class_body.annotation.slice, ast.Name):
                                member_sub_type = PyAnalysis.get_type(datastructure.get_skip_types(),\
                                    class_body.annotation.slice.id, from_import, filemodule)
                                static_type = class_body.annotation.value.id + '[' + \
                                        member_sub_type + ']'
                                Logger.log_debug(f' Analyzing Subscript static type from file {filename}')
                        Logger.log_debug(f'   Static type from file {filename} found {static_name}, static_type: {static_type}')
                        class_datastructure.add_static(static_name, static_type)

                    if isinstance(class_body, ast.FunctionDef):
                        method_name: str = class_body.name
                        arguments: List[Tuple[str, str]] = []
                        for argument in class_body.args.args:
                            if argument.arg != 'self':
                                user_type: str = PyAnalysis.get_type(datastructure.get_skip_types(),\
                                    argument.annotation.id, from_import, filemodule) \
                                        if hasattr(argument, 'annotation') and isinstance(argument.annotation, ast.Name)\
                                            else Common.NOT_PROVIDED_TYPE
                                arguments.append((argument.arg, user_type))
                        if method_name != '':
                            class_datastructure.add_method(method_name,\
                                [ Datastructure.Method.ParameterType(argument_name, argument_type) for argument_name, argument_type in arguments])
                        for fun_body in class_body.body:
                            if isinstance(fun_body, ast.AnnAssign):
                                target = fun_body.target
                                if isinstance(target, ast.Attribute) or isinstance(target, ast.Name):
                                    is_member: bool = False
                                    if isinstance(target, ast.Attribute):
                                        member_name: str = 'self.'+target.attr
                                        member_type: str = ""
                                        annotation = fun_body.annotation
                                        is_member = True
                                    else:
                                        member_name: str = f'{method_name}.{target.id}'
                                        member_type: str = ""
                                        annotation = fun_body.annotation
                                    if isinstance(annotation, ast.Subscript):
                                        if isinstance(annotation.value, ast.Name) and \
                                            isinstance(annotation.slice, ast.Name) and \
                                                hasattr(annotation, 'slice'):
                                            Logger.log_debug(f' Subscript function type from file {filename}')
                                            member_sub_type = PyAnalysis.get_type(datastructure.get_skip_types(), \
                                                annotation.slice.id, from_import, filemodule)                                                    

                                            member_type = annotation.value.id + '[' + member_sub_type + ']'
                                    elif isinstance(annotation, ast.Name):
                                        Logger.log_debug(f' Name function type from file {filename}')
                                        member_type = PyAnalysis.get_type(datastructure.get_skip_types(), \
                                            annotation.id, from_import, filemodule)                                                
                                    else:
                                        saver.append(f'\'WARNING: Will not import member named {member_name}')
                                    if len(member_type) > 0 and (is_member or member_type not in datastructure.get_skip_types()):
                                        Logger.log_debug(f'   Function type from file {filename} method {method_name}, member_type: {member_type}, is_member: {is_member}')
                                        class_datastructure.add_variable(member_name, member_type, is_member)


    @staticmethod
    def __get_namespace_name(namespace_list: List[str], index: int, detailed: bool, grouped_per_ns: bool) -> str:
        namespace_name: str = '.'.join([ namespace for namespace in namespace_list[0: index]])

        namespace_filtered_filename: str = PyAnalysis.__get_file_name_from_class_namespace_name(detailed, grouped_per_ns, namespace_name, True)

        return f'namespace {namespace_name} [[{namespace_filtered_filename}]] {{'

    @staticmethod
    def __sub_namespace_handler(previous_sub_namespace_list: List[str], current_sub_namespace_list: List[str], detailed: bool, grouped_per_ns: bool, saver: Saver, ending_file: bool) -> None:
        
        if ending_file:

            if len(previous_sub_namespace_list) > 0 and \
                saver.removed_last_line_if_same(PyAnalysis.__get_namespace_name(previous_sub_namespace_list, len(previous_sub_namespace_list), detailed, grouped_per_ns)):
                previous_sub_namespace_list.pop()
            saver.append(f'\' Closing all previous_sub_namespace_list namespace {current_sub_namespace_list} because file analysis is finished.' )  
            while len(previous_sub_namespace_list) > 0:
                namespace = previous_sub_namespace_list.pop()
                saver.append(f'\' Closing namespace {namespace}\n}}' )    
            return   

        if len(previous_sub_namespace_list) == 0:
            previous_sub_namespace_list.extend(current_sub_namespace_list)
            #saver.append(f'\' Creating namespaces {current_sub_namespace_list} because previous_sub_namespace_list is empty' )  
            for index in range(0, len(current_sub_namespace_list)):
                saver.append(PyAnalysis.__get_namespace_name(current_sub_namespace_list, index + 1, detailed, grouped_per_ns))
            return          
        
        root_index: int = 0
        index: int = 0
        if len(current_sub_namespace_list) == 0 or current_sub_namespace_list[0] not in previous_sub_namespace_list:
            if saver.removed_last_line_if_same(PyAnalysis.__get_namespace_name(previous_sub_namespace_list, len(previous_sub_namespace_list), detailed, grouped_per_ns)):
                previous_sub_namespace_list.pop()
            saver.append(f'\' Closing all previous_sub_namespace_list namespace because previous_ns: {current_sub_namespace_list} and current_ns: {current_sub_namespace_list})' )  
            while len(previous_sub_namespace_list) > 0:
                namespace = previous_sub_namespace_list.pop()
                saver.append(f'\' Closing namespace {namespace}\n}}' )  
        else:
            # This assumes all elements defining a namespace are unique
            root_index = previous_sub_namespace_list.index(current_sub_namespace_list[0])
            found: bool = True
            for index in range(root_index, len(previous_sub_namespace_list)):
                if index - root_index >= len(current_sub_namespace_list) or \
                    previous_sub_namespace_list[index] != current_sub_namespace_list[index - root_index]:
                    found = False
                    break
            
            if not found:
                if saver.removed_last_line_if_same(PyAnalysis.__get_namespace_name(previous_sub_namespace_list, len(previous_sub_namespace_list), detailed, grouped_per_ns)):
                    previous_sub_namespace_list.pop()
                    index -= 1
                saver.append(f'\' Closing previous_sub_namespace_list namespace from index {index} because previous_ns: {current_sub_namespace_list} and current_ns: {current_sub_namespace_list})' )  
                while len(previous_sub_namespace_list) > index:
                    namespace = previous_sub_namespace_list.pop()
                    saver.append(f'\' Closing namespace {namespace}\n}}' )
        #saver.append(f'\' Creating namespaces {current_sub_namespace_list} reduced to {current_sub_namespace_list[max(1, index - root_index):]}' )  
        for sub_index in range(index - root_index, len(current_sub_namespace_list)):
            namespace = current_sub_namespace_list[sub_index]
            previous_sub_namespace_list.append(namespace)
            saver.append(PyAnalysis.__get_namespace_name(current_sub_namespace_list, sub_index + 1, detailed, grouped_per_ns))

    @staticmethod
    def __create_puml_classes(datastructure: Datastructure, detailed: bool, grouped_per_ns: bool, saver: Saver, from_dir: str) -> None:
        previous_sub_namespace_list: List[str] = []
        list_file_names = datastructure.get_sorted_list_filenames()
        for file_name in list_file_names:
            classes: List[Datastructure.SubDataStructure] = datastructure.get_datastructures_from_filename(file_name)
            current_sub_namespace_list = PyAnalysis.__get_package_name_from_filename(file_name, from_dir).split('.')[0:-1]
            if grouped_per_ns:
                PyAnalysis.__sub_namespace_handler(previous_sub_namespace_list, current_sub_namespace_list, detailed, grouped_per_ns, saver, False)

            empty_spaces = '  ' * (max(len(current_sub_namespace_list) - 1, 0))
            for sub_datastructure in classes:
                fqdn_class_name: str = sub_datastructure.get_fqdn_class_name()
                is_abstract: str = 'abstract ' if sub_datastructure.is_abstract() else ''
                    
                saver.append(f'{empty_spaces}{is_abstract}class {fqdn_class_name} [[{PyAnalysis.__get_file_name_from_class_namespace_name(detailed, grouped_per_ns, fqdn_class_name, True)}]]{{')
                if detailed:
                    static_field: Datastructure.Static
                    for static_field in sub_datastructure.get_static_fields():
                        saver.append(f'{empty_spaces}  + {{static}} {static_field.static_name}: {static_field.static_type}')
                    #pprint(class_content['members'])
                    variable_field: Datastructure.Variable
                    for variable_field in sub_datastructure.get_variable_fields():
                        saver.append(f'{empty_spaces}  - {variable_field.variable_name}: {variable_field.variable_type}' )
                    method_field: Datastructure.Method
                    for method_field in sub_datastructure.get_method_fields():
                        visible = '+'
                        method_name: str = method_field.method_name
                        parameters: str = ', '.join([f'{parameter.parameter}:{parameter.user_type}' for parameter in method_field.parameters])
                        if method_name.startswith('_'):
                            visible = '-'
                        saver.append(f'{empty_spaces}  {visible} {method_name}({parameters})' )

                saver.append(f'{empty_spaces}}}')
            if grouped_per_ns:
                PyAnalysis.__sub_namespace_handler(previous_sub_namespace_list, None, detailed, grouped_per_ns, saver, True)

        saver.append(' \' *************************************** ')
        saver.append(' \' *************************************** ')
        saver.append(' \' *************************************** ')


    @staticmethod
    def __create_puml_connection(datastructure: Datastructure, class_name: str, full_member_type: str, is_member: bool, saver: Saver) -> None:
        connection, member_type, note = Common.reduce_member_type(full_member_type, is_member)
        if member_type not in datastructure.get_skip_types() and \
                class_name not in datastructure.get_skip_types():
            saver.append(f'{class_name} {connection} {member_type} {note}')

    @staticmethod
    def __create_puml_classes_relations(datastructure: Datastructure, saver: Saver, create_all_relation: bool) -> None:
        for file_name in datastructure.get_sorted_list_filenames():
            saver.append(f'\' Class relations extracted from file:\n\' {file_name}')
            sub_datastructure: Datastructure.SubDataStructure
            for sub_datastructure in datastructure.get_datastructures_from_filename(file_name):
                class_name = sub_datastructure.get_fqdn_class_name()
                Logger.log_debug(f' Creation relations for class {class_name} (create_all_relation: {create_all_relation}, File {file_name})')
                for base in sub_datastructure.get_base_classes():
                    if base not in datastructure.get_skip_types() and \
                        class_name not in datastructure.get_skip_types():
                        if create_all_relation or datastructure.class_exists(base):
                            saver.append(f'{base} <-- {class_name}')
                        else:
                            Logger.log_debug(f'  Relation skipped: {base} <-- {class_name} (create_all_relation: {create_all_relation}, datastructure.class_exists({base}): {datastructure.class_exists(base)})')
                static_field: Datastructure.Static
                for static_field in sub_datastructure.get_static_fields():
                    _, naked_type, _ = Common.reduce_member_type(static_field.static_type)
                    if create_all_relation or datastructure.class_exists(naked_type):
                        PyAnalysis.__create_puml_connection(datastructure, class_name, static_field.static_type, True, saver)
                    else:
                        Logger.log_debug(f'  Relation skipped: {class_name} ?-- {naked_type} (create_all_relation: {create_all_relation}, datastructure.class_exists({naked_type}): {datastructure.class_exists(naked_type)})')
                variable_field: Datastructure.Variable
                for variable_field in sub_datastructure.get_variable_fields():
                    _, naked_type, _ = Common.reduce_member_type(variable_field.variable_type)
                    if create_all_relation or datastructure.class_exists(naked_type):
                        PyAnalysis.__create_puml_connection(datastructure, class_name, variable_field.variable_type, variable_field.is_member, saver)
                    else:
                        Logger.log_debug(f'  Relation skipped: {class_name} ?-- {naked_type} (create_all_relation: {create_all_relation}, datastructure.class_exists({naked_type}): {datastructure.class_exists(naked_type)})')
                for method_field in sub_datastructure.get_method_fields():
                    for parameter in method_field.parameters:
                        _, naked_type, _ = Common.reduce_member_type(parameter.user_type)
                        if create_all_relation or datastructure.class_exists(naked_type):
                            PyAnalysis.__create_puml_connection(datastructure, class_name, parameter.user_type, False, saver)
                        else:
                            Logger.log_debug(f'  Relation skipped: {class_name} ?-- {naked_type} (create_all_relation: {create_all_relation}, datastructure.class_exists({naked_type}): {datastructure.class_exists(naked_type)})')
            
    @staticmethod
    def __create_full_diagram(datastructure: Datastructure, detailed: bool, grouped_per_ns: bool, initial_saver: Saver, from_dir: str, class_namespace_name: str = None) -> None:
        saver: Saver = initial_saver.clone()
        user_info_filename, filename, user_info_link_1, link_path_1, user_info_link_2, link_path_2 = \
            PyAnalysis.__get_file_name(detailed, grouped_per_ns, class_namespace_name)
        saver.append(f'title <size:20>{user_info_filename}</size>')
        saver.append( f'note "Your are analyzing:\\n{user_info_filename}\\n\\n' +
                      '==Filter==\\n' +
                      'You can click either the namespaces \\n' + 
                      'or class names for filtering them and their\\n' +
                      'direct dependencies.\\n\\n' +
                      '==Select other==\\n' +
                      f'* {user_info_link_1}:\\n   [[{link_path_1}]]\\n* {user_info_link_2}:\\n   [[{link_path_2}]]" as FloatingNote')
        PyAnalysis.__create_puml_classes(datastructure, detailed, grouped_per_ns, saver, from_dir)
        create_all_relation: bool = class_namespace_name == None
        PyAnalysis.__create_puml_classes_relations(datastructure, saver, create_all_relation)
        saver.append('@enduml')
        saver.save(filename)

    @staticmethod
    def __create_puml_files(datastructure: Datastructure, saver: Saver, from_dir: str, class_name: str = None) -> None:
        PyAnalysis.__create_full_diagram(datastructure, True,  False,  saver, from_dir, class_name)
        PyAnalysis.__create_full_diagram(datastructure, True,  True,   saver, from_dir, class_name)
        PyAnalysis.__create_full_diagram(datastructure, False, False,  saver, from_dir, class_name)
        PyAnalysis.__create_full_diagram(datastructure, False, True,   saver, from_dir, class_name)
                        
    def read_all_python_files(self, from_dir: str, out_dir: str) -> Dict[str, List[str]]:
        saver: Saver = Saver(out_dir)
        saver.append('@startuml')
        for file in list(Path(from_dir).rglob("*.py")):
            file_name: str = os.path.join(from_dir, file)
            PyAnalysis.__read_python_ast(self.datastructure, file_name, from_dir, saver)
        PyAnalysis.__create_puml_files(self.datastructure, saver, from_dir, None)

        class_list: List[str] = self.datastructure.get_classname_list()
        for class_name in class_list:
             reduced_class_list = DatastructureHandler.create_reduced_class_list_from_class_name_list(\
                self.datastructure, [class_name])
             PyAnalysis.__create_puml_files(reduced_class_list, saver, from_dir, class_name)

        class_name_list_grouped_by_namespaces: Dict[List[str]] = DatastructureHandler.get_class_name_list_grouped_by_namespaces(self.datastructure)
        for namespace_name, class_name_list in class_name_list_grouped_by_namespaces.items():
             reduced_namespace_list = DatastructureHandler.create_reduced_class_list_from_class_name_list(self.datastructure, class_name_list)
             PyAnalysis.__create_puml_files(reduced_namespace_list, saver, from_dir, namespace_name)


def main(from_dir: str, out_dir: str) -> None:
    program_name = os.path.basename(sys.argv[0])
    
    # create the top-level parser
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('--from_dir', type=str, help='Specify where to read the python files from')
    parser.add_argument('--out_dir', type=str, help='Specify where to store all puml files')
    args = parser.parse_args()
    if args.from_dir: from_dir = args.from_dir
    if args.out_dir: out_dir = args.out_dir

    py_analysis: PyAnalysis = PyAnalysis(Datastructure(PythonLanguage()))
    py_analysis.read_all_python_files(from_dir, out_dir)

    file_name: str = os.path.join(os.getcwd(), out_dir, re.sub('puml$', 'svg', f'full{PyAnalysis.DETAILED_FILENAME_SUFFIX}'))
    print(f'Please open {file_name} in your browser')



if __name__ == "__main__":
    main('/Users/jean-philippe.ulpiano/development/pygame/candy_cat', '/Users/jean-philippe.ulpiano/development/pygame/tmp-out')
