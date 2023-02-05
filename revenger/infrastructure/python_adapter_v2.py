from __future__ import annotations

from _ast import ImportFrom, ClassDef, Name, AnnAssign, FunctionDef
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any
import ast
import re
from infrastructure.generic_classes import GenericSubDataStructure
from infrastructure.generic_classes import GenericDatastructure
from infrastructure.generic_classes import GenericSaver
from infrastructure.generic_classes import GenericLogger
from infrastructure.generic_classes import GenericPythonAdapter
from infrastructure.common import CommonInfrastructure
from domain.datastructure import Datastructure

class PythonAdapterV2(GenericPythonAdapter):
    def __init__(self, saver: GenericSaver, logger: GenericLogger):
        self.saver = saver
        self.logger = logger
        self.logger.log_warn(f' ============== Analysing With Py Adapter V2 =======================')

    @staticmethod
    def __get_namespace_name_from_filename(filename: str, from_dir: str) -> str:
        if from_dir is not None:
            filename = filename.replace(from_dir, '')
        return re.sub('^\.', '', re.sub('\.py$', '', filename.replace('/', '.')))

    def read_python_ast(self, datastructure: GenericDatastructure, filename: str, from_dir: str) -> any:
        with open(filename, encoding="utf-8") as file:
            tree: any = ast.parse(file.read())
            self.logger.log_trace(f"Filename: {filename}")
            self.logger.log_trace(ast.dump(tree, indent=4))
            self.logger.log_trace("\n\n\n\n")
        filemodule: str = PythonAdapterV2.__get_namespace_name_from_filename(filename, from_dir)
        from_import: Dict[str, str] = {}

        node_visitor = self.AstVisitor(datastructure, filename, filemodule, self.logger)
        node_visitor.visit(tree)
        self.logger.log_debug(f'Analyzing file: {filename}')
        # for node in tree.body:
        #     if isinstance(node, ast.ImportFrom):
        #         module_path = node.module
        #         for module_name in node.names:
        #             from_import[module_name.name] = module_path + '.' + module_name.name
        #
        # for node in tree.body:
        #     if isinstance(node, ast.ClassDef):
        #         self.analyze_class_def(node, datastructure, filename, from_import, filemodule)

    def analyze_class_def(self, \
                          node: ast.ClassDef, datastructure: GenericDatastructure, \
                          filename: str, from_import: Dict[str, str], filemodule: str, parent_class_name: str = None):
        if parent_class_name is None:
            class_name: str = f'{filemodule}.{node.name}'
            self.logger.log_debug(f'Created class_name {class_name} from filemodule: >{filemodule}< and >{node.name}<')
        else:
            class_name: str = f'{filemodule}.{parent_class_name}.{node.name}'
            self.logger.log_debug(
                f'Created class_name {class_name} from filemodule: >{filemodule}<, parent_class_name: >{parent_class_name}< and >{node.name}<')

        class_datastructure: GenericSubDataStructure = \
            datastructure.append_class(filename, filemodule, from_import, class_name, filemodule.split('.'))
        self.logger.log_debug(
            f' Creating class {class_name} from file {filename}, filemodule: {filemodule}, from_import: {from_import}')
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_class = base.id
                if base_class == 'ABC':
                    class_datastructure.set_abstract()
                else:
                    class_datastructure.add_base_class(base_class)
        for class_body in node.body:
            if isinstance(class_body, ast.ClassDef):
                inner_class_name: str = f'{class_name}.{class_body.name}'
                self.logger.log_debug(
                    f'  Created inner class name {inner_class_name} from filemodule: >{filemodule}< and >{node.name}<')
                from_parent: str = f'{parent_class_name}.{node.name}' if parent_class_name is not None \
                    else node.name
                self.logger.log_debug(f'  Created from_parent name {from_parent}')
                class_datastructure.add_inner_class(inner_class_name)
                self.analyze_class_def(class_body, datastructure, filename, from_import, filemodule, from_parent)

            if isinstance(class_body, ast.AnnAssign):
                static_name: str = class_body.target.id
                static_type: str = CommonInfrastructure.NOT_EXTRACTED
                if isinstance(class_body.annotation, ast.Name):
                    static_type = self.get_type(datastructure.get_skip_types(), \
                                                class_body.annotation.id, from_import, filemodule)
                    self.logger.log_debug(f' Analyzing ast.Name static type {static_type} from file {filename}')
                elif isinstance(class_body.annotation, ast.Subscript):
                    if isinstance(class_body.annotation.value, ast.Name) and \
                            isinstance(class_body.annotation.slice, ast.Name):
                        member_sub_type = self.get_type(datastructure.get_skip_types(), \
                                                        class_body.annotation.slice.id, from_import, filemodule)
                        static_type = class_body.annotation.value.id + '[' + \
                                      member_sub_type + ']'
                        self.logger.log_debug(
                            f' Analyzing ast.Subscript static type {static_type} from file {filename}')
                self.logger.log_debug(
                    f'   Static type from file {filename} found static_name: {static_name}, static_type: {static_type}')
                class_datastructure.add_static(static_name, static_type)

            if isinstance(class_body, ast.FunctionDef):
                method_name: str = class_body.name
                arguments: List[Tuple[str, str]] = []
                for argument in class_body.args.args:
                    if argument.arg != 'self':
                        user_type: str = self.get_type(datastructure.get_skip_types(), \
                                                       argument.annotation.id, from_import, filemodule) \
                            if hasattr(argument, 'annotation') and isinstance(argument.annotation, ast.Name) \
                            else CommonInfrastructure.NOT_PROVIDED_TYPE
                        arguments.append((argument.arg, user_type))
                if method_name != '':
                    is_private: bool = method_name.startswith('_')
                    class_datastructure.add_method(method_name, \
                                                   [(argument_name, argument_type) for argument_name, argument_type in
                                                    arguments],
                                                   is_private)
                for fun_body in class_body.body:
                    if isinstance(fun_body, ast.AnnAssign):
                        target = fun_body.target
                        if isinstance(target, ast.Attribute) or isinstance(target, ast.Name):
                            is_member: bool = False
                            if isinstance(target, ast.Attribute):
                                member_name: str = 'self.' + target.attr
                                member_type: str = ""
                                annotation = fun_body.annotation
                                is_member = True
                            else:
                                member_name: str = f'{method_name}.{target.id}'
                                self.logger.log_debug(
                                    f'  Created member_name {member_name} from method_name: >{method_name}> and >{target.id}<')
                                member_type: str = ""
                                annotation = fun_body.annotation
                            if isinstance(annotation, ast.Subscript):
                                if isinstance(annotation.value, ast.Name) and \
                                        isinstance(annotation.slice, ast.Name) and \
                                        hasattr(annotation, 'slice'):
                                    self.logger.log_debug(f' Subscript function type from file {filename}')
                                    member_sub_type = self.get_type(datastructure.get_skip_types(), \
                                                                    annotation.slice.id, from_import, filemodule)

                                    member_type = annotation.value.id + '[' + member_sub_type + ']'
                            elif isinstance(annotation, ast.Name):
                                self.logger.log_debug(f' Name function type from file {filename}')
                                member_type = self.get_type(datastructure.get_skip_types(), \
                                                            annotation.id, from_import, filemodule)
                            else:
                                self.saver.append(f'\'WARNING: Will not import member named {member_name}')
                            if len(member_type) > 0 and (
                                    is_member or member_type not in datastructure.get_skip_types()):
                                self.logger.log_debug(
                                    f'   Function type from file {filename} method {method_name}, member_type: {member_type}, is_member: {is_member}')
                                class_datastructure.add_variable(member_name, member_type, is_member)

    class AstVisitor(ast.NodeVisitor):

        def __init__(self, datastructure: GenericDatastructure, filename, filemodule: str, logger: GenericLogger):
            self.datastructure = datastructure
            self.filename = filename
            self.filemodule = filemodule
            self.logger = logger
            self.from_import: Dict[str, str] = {}
            self.active_class_name_list: List[str] = []
            self.active_method_name_list: List[str] = []
            self.namespace_list: List[str] = []

        def get_current_class_name(self) -> str:
            if len(self.active_class_name_list) > 0:
                return self.active_class_name_list[-1]
            return "##NoClass##"

        def get_type(self, skip_types: List[str], initial_type: str, type_dict: Dict[str, str], filemodule: str) -> str:
            member_sub_type = initial_type
            if member_sub_type in type_dict.keys():
                member_sub_type = type_dict[member_sub_type]
                self.logger.log_debug(
                    f'  Type {member_sub_type} *** found *** in {type_dict.keys()} saving as type from module {member_sub_type}')
            elif member_sub_type not in skip_types:
                member_sub_type = f'{filemodule}.{member_sub_type}'
                self.logger.log_debug(f'  Created sub type {member_sub_type} from filemodule: >{filemodule}<')
                self.logger.log_debug(
                    f'  Type {member_sub_type} not found in {type_dict.keys()} saving as type from module {member_sub_type}')
            return member_sub_type

        # TODO: Move it to classDef itself and improve implementation
        def analyse_class_def(self, node: ClassDef) -> Tuple[GenericSubDataStructure | None, str]:
            active_class_name: str = None

            if len(self.active_class_name_list) > 0:
                active_class_name = self.active_class_name_list[-1]

            fqdn_class_name: str = f'{self.filemodule}.{node.name}'
            if active_class_name is not None:
                fqdn_class_name = f'{self.filemodule}.{active_class_name}.{node.name}'

            parent_sub_datastructure: GenericSubDataStructure = self.datastructure.get_datastructures_from_class_name(
                self.get_current_class_name())

            if parent_sub_datastructure is not None:
                parent_sub_datastructure.add_inner_class(fqdn_class_name)

            self.datastructure.append_class(self.filename, self.filemodule, self.from_import, fqdn_class_name, self.namespace_list)

            sub_datastructure: GenericSubDataStructure = self.datastructure.get_datastructures_from_class_name(fqdn_class_name)
            if sub_datastructure is not None:
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_class = base.id
                        if base_class == 'ABC':
                            sub_datastructure.set_abstract()
                        else:
                            sub_datastructure.add_base_class(base_class)

            return sub_datastructure, fqdn_class_name


        def visit_ImportFrom(self, node: ImportFrom) -> Any:
            module_path = node.module

            for module_name in node.names:
                self.from_import[module_name.name] = module_path + '.' + module_name.name

            self.logger.log_warn(f' {self.from_import}')
            ast.NodeVisitor.generic_visit(self, node)

        def generic_visit(self, node):
            # print(node)
            ast.NodeVisitor.generic_visit(self, node)

        def visit_ClassDef(self, node: ClassDef) -> Any:

            sub_datastructure, fqdn_class_name = self.analyse_class_def(node)

            self.active_class_name_list.append(fqdn_class_name)
            ast.NodeVisitor.generic_visit(self, node)

            if len(self.active_class_name_list) > 0:
                self.active_class_name_list.pop()

        def visit_AnnAssign(self, node: AnnAssign) -> Any:
            static_name: str = node.target.id
            static_type: str = CommonInfrastructure.NOT_EXTRACTED
            if isinstance(node.annotation, ast.Name):
                static_type = self.get_type(self.datastructure.get_skip_types(), \
                                            node.annotation.id, self.from_import, self.filemodule)
                self.logger.log_debug(f' Analyzing ast.Name static type {static_type} from file {self.filename}')
            elif isinstance(node.annotation, ast.Subscript):
                if isinstance(node.annotation.value, ast.Name) and \
                        isinstance(node.annotation.slice, ast.Name):
                    member_sub_type = self.get_type(self.datastructure.get_skip_types(), \
                                                    node.annotation.slice.id, self.from_import, self.filemodule)
                    static_type = node.annotation.value.id + '[' + \
                                  member_sub_type + ']'
                    self.logger.log_debug(
                        f' Analyzing ast.Subscript static type {static_type} from file {self.filename}')
            self.logger.log_debug(
                f'   Static type from file {self.filename} found static_name: {static_name}, static_type: {static_type}')
            sub_datastructure: GenericSubDataStructure = self.datastructure.get_datastructures_from_class_name(
                self.get_current_class_name())

            sub_datastructure.add_static(static_name, static_type)

            # Instance and method vars
            method: Datastructure.Method = sub_datastructure.get_method(self.active_method_name_list[-1])
            target = node.target
            if isinstance(target, ast.Attribute) or isinstance(target, ast.Name):
                is_member: bool = False
                if isinstance(target, ast.Attribute):
                    member_name: str = 'self.' + target.attr
                    member_type: str = ""
                    annotation = node.annotation
                    is_member = True
                else:
                    member_name: str = f'{self.active_method_name_list[-1]}.{target.id}'
                    self.logger.log_debug(
                        f'  Created member_name {member_name} from method_name: >{self.active_method_name_list[-1]}> and >{target.id}<')
                    member_type: str = ""
                    annotation = node.annotation
                if isinstance(annotation, ast.Subscript):
                    if isinstance(annotation.value, ast.Name) and \
                            isinstance(annotation.slice, ast.Name) and \
                            hasattr(annotation, 'slice'):
                        self.logger.log_debug(f' Subscript function type from file {self.filename}')
                        member_sub_type = self.get_type(self.datastructure.get_skip_types(), \
                                                        annotation.slice.id, self.from_import, self.filemodule)

                        member_type = annotation.value.id + '[' + member_sub_type + ']'
                elif isinstance(annotation, ast.Name):
                    self.logger.log_debug(f' Name function type from file {self.filename}')
                    member_type = self.get_type(self.datastructure.get_skip_types(), \
                                                annotation.id, self.from_import, self.filemodule)
                # else:
                #     self.saver.append(f'\'WARNING: Will not import member named {member_name}')
                if len(member_type) > 0 and (
                        is_member or member_type not in self.datastructure.get_skip_types()):
                    self.logger.log_debug(
                        f'   Function type from file {self.filename} method {method.method_name}, member_type: {member_type}, is_member: {is_member}')
                    sub_datastructure.add_variable(member_name, member_type, is_member)
                else:
                    method.variables.append(Datastructure.Method.MethodVariable(member_name, member_type))

            ast.NodeVisitor.generic_visit(self, node)

        def visit_FunctionDef(self, node: FunctionDef) -> Any:
            sub_datastructure: GenericSubDataStructure = self.datastructure.get_datastructures_from_class_name(
                self.get_current_class_name())
            method_name: str = node.name
            self.active_method_name_list.append(method_name)

            arguments: List[Tuple[str, str]] = []
            for argument in node.args.args:
                if argument.arg != 'self':
                    user_type: str = self.get_type(self.datastructure.get_skip_types(), \
                                                   argument.annotation.id, self.from_import, self.filemodule) \
                        if hasattr(argument, 'annotation') and isinstance(argument.annotation, ast.Name) \
                        else CommonInfrastructure.NOT_PROVIDED_TYPE
                    arguments.append((argument.arg, user_type))
            if method_name != '':
                is_private: bool = method_name.startswith('_')
                sub_datastructure.add_method(method_name, \
                                               [(argument_name, argument_type) for argument_name, argument_type in
                                                arguments],
                                               is_private, ()) # TODO: method variables

            ast.NodeVisitor.generic_visit(self, node)
            if len(self.active_method_name_list) > 0:
                self.active_method_name_list.pop()
