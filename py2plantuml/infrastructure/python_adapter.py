from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
import re
import ast

from domain.saver import Saver
from domain.logger import Logger
from domain.common import Common
from domain.datastructure import Datastructure

class PythonAdapter:
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
    def read_python_ast(datastructure: Datastructure, filename: str, from_dir: str, saver: Saver) -> any:
        with open(filename, encoding="utf-8") as file:
            tree: any = ast.parse(file.read())
        filemodule = datastructure.get_language_dependent().get_package_name_from_filename(filename, from_dir)
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
                            static_type = PythonAdapter.get_type(datastructure.get_skip_types(),\
                                class_body.annotation.id, from_import, filemodule)
                            Logger.log_debug(f' Analyzing static type from file {filename}')
                        elif isinstance(class_body.annotation, ast.Subscript):
                            if isinstance(class_body.annotation.value, ast.Name) and \
                                isinstance(class_body.annotation.slice, ast.Name):
                                member_sub_type = PythonAdapter.get_type(datastructure.get_skip_types(),\
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
                                user_type: str = PythonAdapter.get_type(datastructure.get_skip_types(),\
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
                                            member_sub_type = PythonAdapter.get_type(datastructure.get_skip_types(), \
                                                annotation.slice.id, from_import, filemodule)                                                    

                                            member_type = annotation.value.id + '[' + member_sub_type + ']'
                                    elif isinstance(annotation, ast.Name):
                                        Logger.log_debug(f' Name function type from file {filename}')
                                        member_type = PythonAdapter.get_type(datastructure.get_skip_types(), \
                                            annotation.id, from_import, filemodule)                                                
                                    else:
                                        saver.append(f'\'WARNING: Will not import member named {member_name}')
                                    if len(member_type) > 0 and (is_member or member_type not in datastructure.get_skip_types()):
                                        Logger.log_debug(f'   Function type from file {filename} method {method_name}, member_type: {member_type}, is_member: {is_member}')
                                        class_datastructure.add_variable(member_name, member_type, is_member)
