from __future__ import annotations
from typing import List, Dict, Tuple
import os
import re
import ast
import sys
import os
import re
import argparse
from pathlib import Path
from pprint import pprint



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
        with open(filename, 'w', encoding="utf-8") as file:
            file.write('\n'.join(self.lines_to_save))

    def clone(self) -> Saver:
        return Saver(self.out_dir, self)

    def removed_last_line_if_same(self, line: str) -> bool:
        if len(self.lines_to_save) > 0 and line == self.lines_to_save[-1]:
            self.lines_to_save.pop()
            return True
        return False


class PyAnalysis:
    NOT_EXTRACTED: str = '** Not extracted **'
    SKIP_TYPES: List[str] = ['int', 'str', 'float', 'bool', 'abc.ABC', NOT_EXTRACTED]
    FULL_DETAILED_FILE_NAME: str = 'full-diagram-detailed.puml'
    FULL_SIMPLIFIED_FILE_NAME: str = 'full-diagram-simplified.puml'
    FULL_DETAILED_PER_NS_FILE_NAME: str = 'full-diagram-detailed-per-ns.puml'
    FULL_SIMPLIFIED_PER_NS_FILE_NAME: str = 'full-diagram-simplified-per-ns.puml'

    def __init__(self):
        pass

    @staticmethod
    def __get_file_name_from_class_name(detailed: bool, class_name: str, want_svg_file: bool) -> str:
        file_name: str = f'{class_name}-diagram-simplified.puml'
        if detailed:
            file_name = f'{class_name}-diagram-detailed.puml'

        if want_svg_file:
            file_name = re.sub('puml$', 'svg', file_name)
        
        return file_name
    
    @staticmethod
    def __get_file_name(detailed: bool, class_name: str = None) -> Tuple[str, str, str]:

        full_file_name_simplified: str = re.sub('puml$', 'svg', PyAnalysis.FULL_SIMPLIFIED_FILE_NAME)
        full_file_name_detailed: str = re.sub('puml$', 'svg', PyAnalysis.FULL_DETAILED_FILE_NAME)

        if class_name is None:
            if detailed:
                return PyAnalysis.FULL_DETAILED_FILE_NAME, full_file_name_simplified, None
            else:
                return PyAnalysis.FULL_SIMPLIFIED_FILE_NAME, full_file_name_detailed, None

        puml_file: str = PyAnalysis.__get_file_name_from_class_name(detailed, class_name, False)
        svg_file_name_opposite_detailed: str = PyAnalysis.__get_file_name_from_class_name(not detailed, class_name, True)
        full_file_name: str = full_file_name_simplified

        if detailed:
            full_file_name: str = full_file_name_detailed

        return puml_file, svg_file_name_opposite_detailed, full_file_name


    @staticmethod
    def get_type(initial_type: str, type_dict: Dict[str, str], filemodule: str) -> str:
        member_sub_type = initial_type
        if member_sub_type in type_dict.keys():
            member_sub_type = type_dict[member_sub_type]
        elif member_sub_type not in ['int', 'float', 'str', 'bool']:
            member_sub_type = filemodule + member_sub_type 
        return member_sub_type

    @staticmethod
    def __get_package_name_from_filename(filename: str, from_dir: str = None) -> str:
        if from_dir is not None:
            filename = filename.replace(from_dir, '')
        return re.sub('^\.', '', re.sub('py$', '', filename.replace('/', '.')))

    def __read_python_ast(self, filename: str, from_dir: str, saver: Saver) -> any:
        with open(filename, encoding="utf-8") as file:
            tree: any = ast.parse(file.read())
        classes: Dict[str, List[Dict[str, any]]] = {}
        filemodule = PyAnalysis.__get_package_name_from_filename(filename, from_dir)
        from_import: dict = {}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                module_path = node.module
                for module_name in node.names:
                    from_import[module_name.name] = module_path + '.' + module_name.name

        for node in tree.body:    
            if isinstance(node, ast.ClassDef):
                class_name = f'{filemodule}{node.name}'
                properties: dict = {'bases': [], 'statics': [], 'methods': [], 'members': [], 'isabstract': False}
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_class = base.id
                        if base_class == 'ABC':
                            properties['isabstract'] = True
                        if base_class in from_import.keys():
                            base_class = from_import[base_class]
                        else:
                            base_class = filemodule + base_class

                        properties['bases'].append(base_class)
                for class_body in node.body:
                    if isinstance(class_body, ast.AnnAssign):
                        static_name: str = class_body.target.id
                        static_type: str = PyAnalysis.NOT_EXTRACTED
                        if isinstance(class_body.annotation, ast.Name):
                            static_type = PyAnalysis.get_type(\
                                class_body.annotation.id, from_import, filemodule)
                        elif isinstance(class_body.annotation, ast.Subscript):
                            if isinstance(class_body.annotation.value, ast.Name) and \
                                isinstance(class_body.annotation.slice, ast.Name):
                                member_sub_type = PyAnalysis.get_type(\
                                    class_body.annotation.slice.id, from_import, filemodule)
                                static_type = class_body.annotation.value.id + '[' + \
                                        member_sub_type + ']'
                        properties['statics'].append((static_name, static_type ))
                    if isinstance(class_body, ast.FunctionDef):
                        name: str = class_body.name
                        arguments: list = [a.arg for a in class_body.args.args if a.arg != 'self']
                        if name != '':
                            properties['methods'].append((name, ', '.join(arguments) ))
                        for fun_body in class_body.body:
                            if isinstance(fun_body, ast.AnnAssign):
                                target = fun_body.target
                                if isinstance(target, ast.Attribute):
                                    if target.value.id == 'self':
                                        member_name: str = target.attr
                                        member_type: str = ""
                                        annotation = fun_body.annotation
                                        if isinstance(annotation, ast.Subscript):
                                            if isinstance(annotation.value, ast.Name) and \
                                                isinstance(annotation.slice, ast.Name) and \
                                                    hasattr(annotation, 'slice'):
                                                member_sub_type = PyAnalysis.get_type(\
                                                    annotation.slice.id, from_import, filemodule)                                                    

                                                member_type = annotation.value.id + '[' + member_sub_type + ']'
                                        elif isinstance(annotation, ast.Name):
                                            member_type = PyAnalysis.get_type(\
                                                annotation.id, from_import, filemodule)                                                
                                        else:
                                            saver.append(f'\'WARNING: Will not import member named {member_name}')
                                    if len(member_type) > 0:
                                        properties['members'].append((member_name, member_type ))
                classes[class_name] = properties
        
        # pprint(classes)
        return classes


    def __sub_namespace_handler(previous_sub_namespace_list: List[str], current_sub_namespace_list: List[str], saver: Saver, ending_file: bool) -> None:
        
        opening_namespace = lambda namespace: f'namespace {namespace} {{'
        if ending_file:
            if len(previous_sub_namespace_list) > 0 and \
                saver.removed_last_line_if_same(opening_namespace(previous_sub_namespace_list[-1])):
                previous_sub_namespace_list.pop()
            while len(previous_sub_namespace_list) > 0:
                namespace = previous_sub_namespace_list.pop()
                saver.append(f'\' Closing namespace {namespace}\n}}' )    
            return   

        if len(previous_sub_namespace_list) == 0:
            previous_sub_namespace_list.extend(current_sub_namespace_list)
            for namespace in current_sub_namespace_list:
                saver.append(opening_namespace(namespace))
            return          
        
        root_index: int = 0
        index: int = 0
        if len(current_sub_namespace_list) == 0 or current_sub_namespace_list[0] not in previous_sub_namespace_list:
            if saver.removed_last_line_if_same(opening_namespace(previous_sub_namespace_list[-1])):
                previous_sub_namespace_list.pop()
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
                if saver.removed_last_line_if_same(opening_namespace(previous_sub_namespace_list[-1])):
                    previous_sub_namespace_list.pop()
                    index -= 1
                while len(previous_sub_namespace_list) > index:
                    namespace = previous_sub_namespace_list.pop()
                    saver.append(f'\' Closing namespace {namespace}\n}}' )
        
        for sub_index in range(index - root_index, len(current_sub_namespace_list)):
            namespace = current_sub_namespace_list[sub_index]
            previous_sub_namespace_list.append(namespace)
            saver.append(opening_namespace(namespace))
          
    @staticmethod
    def __create_puml_classes(class_tree: Dict[str, Dict[str, List[Dict[str, any]]]], detailed: bool, saver: Saver, from_dir: str) -> None:
        previous_sub_namespace_list: List[str] = []
        list_file_names = sorted(class_tree.keys())
        for file_name in list_file_names:
            classes = class_tree[file_name]
            current_sub_space_list = PyAnalysis.__get_package_name_from_filename(file_name, from_dir).split('.')[0:-1]
            PyAnalysis.__sub_namespace_handler(previous_sub_namespace_list, current_sub_space_list, saver, False)

            empty_spaces = '  ' * (max(len(current_sub_space_list) - 1, 0))
            for class_name, class_content in classes.items():
                is_abstract: str = ''
                if 'isabstract' in class_content.keys() and class_content['isabstract']:
                    is_abstract = 'abstract '
                saver.append(f'{empty_spaces}{is_abstract}class {class_name} [[{PyAnalysis.__get_file_name_from_class_name(detailed, class_name, True)}]]{{')
                if detailed:
                    if 'statics' in class_content:
                        for static_name, static_type in class_content['statics']:
                            saver.append(f'{empty_spaces}  + {{static}} {static_name}: {static_type}')
                        #pprint(class_content['members'])
                    if 'members' in class_content:
                        for member_name, member_type in class_content['members']:
                            saver.append(f'{empty_spaces}  - {member_name}: {member_type}' )
                    if 'methods' in class_content:
                        for method_name, member_type in class_content['methods']:
                            visible = '+'
                            if method_name.startswith('_'):
                                visible = '-'
                            saver.append(f'{empty_spaces}  {visible} {method_name}({member_type})' )

                saver.append('}')
        PyAnalysis.__sub_namespace_handler(previous_sub_namespace_list, None, saver, True)

        saver.append(' \' *************************************** ')
        saver.append(' \' *************************************** ')
        saver.append(' \' *************************************** ')

    @staticmethod
    def __reduce_member_type(member_type: str) -> Tuple[str, str, str]:
        connection: str = '*--'
        note: str = ''
        if member_type.startswith('List['):
            member_type=member_type[5:-1]
            connection = f'"many" {connection} "1"'
            note = ': (list)'
        if member_type.startswith('Set['):
            member_type=member_type[4:-1]
            connection = f'"many" {connection} "1"'
            note = ': (set)'
        return connection, member_type, note

    @staticmethod
    def __create_puml_connection(class_name: str, member_type: str, saver: Saver) -> None:
        connection, member_type, note = PyAnalysis.__reduce_member_type(member_type)
        if member_type not in PyAnalysis.SKIP_TYPES and class_name not in PyAnalysis.SKIP_TYPES:
            saver.append(f'{class_name} {connection} {member_type} {note}')

    @staticmethod
    def __create_puml_classes_relations(class_tree: Dict[str, Dict[str, List[Dict[str, any]]]], saver: Saver, create_all_relation: bool) -> None:
        for file_name, classes in class_tree.items():
            saver.append(f'\' Class relations extracted from file:\n\' {file_name}')
            for class_name, class_content in classes.items():
                for base in class_content['bases']:
                    if base not in PyAnalysis.SKIP_TYPES and class_name not in PyAnalysis.SKIP_TYPES:
                        if create_all_relation or PyAnalysis.__class_exists(class_tree, base):
                            saver.append(f'{base} <-- {class_name}')
                for _, member_type in class_content['statics']:
                    if create_all_relation or PyAnalysis.__class_exists(class_tree, member_type):
                        PyAnalysis.__create_puml_connection(class_name, member_type, saver)
            
                for _, member_type in class_content['members']:
                    if create_all_relation or PyAnalysis.__class_exists(class_tree, member_type):
                        PyAnalysis.__create_puml_connection(class_name, member_type, saver)
            

    @staticmethod
    def __create_full_diagram(class_tree: Dict[str, Dict[str, List[Dict[str, any]]]], detailed: bool, initial_saver: Saver, from_dir: str, class_name: str = None) -> None:
        saver: Saver = initial_saver.clone()
        filename, link_path_1, link_path_2 = PyAnalysis.__get_file_name(detailed, class_name)

        link_path: str = f'[[{link_path_1}]]'
        if link_path_2 is not None:
            link_path=f'{link_path} - [[{link_path_2}]]'

        saver.append(f'note "{link_path}" as Unused')
        PyAnalysis.__create_puml_classes(class_tree, detailed, saver, from_dir)
        create_all_relation: bool = class_name == None
        PyAnalysis.__create_puml_classes_relations(class_tree, saver, create_all_relation)
        saver.append('@enduml')
        saver.save(filename)

    def __create_puml_files(class_tree: Dict[str, Dict[str, List[Dict[str, any]]]], saver: Saver, from_dir: str, class_name: str = None) -> None:
        PyAnalysis.__create_full_diagram(class_tree, True, saver, from_dir, class_name)
        PyAnalysis.__create_full_diagram(class_tree, False, saver, from_dir, class_name)
        
    @staticmethod
    def __get_class_list(class_tree: Dict[str, Dict[str, List[Dict[str, any]]]]) -> List[str]:
        class_list: List[str] = []
        for classes in class_tree.values():
            class_list.extend(classes.keys())
        # print("Debug here !!!")
        # class_list.append('services.create_scene_service.CreateSceneService')
        return class_list

    @staticmethod
    def __class_exists(class_tree: Dict[str, Dict[str, List[Dict[str, any]]]], class_name: str) -> bool:
        for classes in class_tree.values():
            if class_name in classes.keys():
                return True
        return False

    @staticmethod
    def __add_class_to_tree_if_not_exist(classes: Dict[str, List[Dict[str, any]]], file_name: str, class_name: str, reduced_class_tree: Dict[str, Dict[str, List[Dict[str, any]]]]) -> bool:
        if class_name in classes.keys():

            if file_name not in reduced_class_tree.keys():
                reduced_class_tree[file_name] = {}
            if class_name not in reduced_class_tree[file_name].keys():
                reduced_class_tree[file_name][class_name] = classes[class_name].copy()
            return True

        return False
    
    @staticmethod
    def __add_class_to_tree(class_tree: Dict[str, Dict[str, List[Dict[str, any]]]], class_name: str, reduced_class_tree: Dict[str, Dict[str, List[Dict[str, any]]]]) -> None:
        for file_name, classes in class_tree.items():
            if class_name in classes.keys():
                if file_name not in reduced_class_tree.keys():
                    reduced_class_tree[file_name] = {}
                if class_name not in reduced_class_tree[file_name].keys():
                    reduced_class_tree[file_name][class_name] = classes[class_name].copy()
    
    @staticmethod
    def __get_reduced_class_list_from_class_name(class_tree: Dict[str, Dict[str, List[Dict[str, any]]]], class_name: str, class_list: List[str]) -> Dict[str, Dict[str, List[Dict[str, any]]]]:
        reduced_class_tree: Dict[str, Dict[str, List[Dict[str, any]]]] = {}
        for file_name, classes in class_tree.items():
            if PyAnalysis.__add_class_to_tree_if_not_exist(classes, file_name, class_name, reduced_class_tree):
                class_content = classes[class_name]
                for base in class_content['bases']:
                    PyAnalysis.__add_class_to_tree(class_tree, base, reduced_class_tree)
                for _, member_type in class_content['statics']:
                    _, reduced_member_type, _ = PyAnalysis.__reduce_member_type(member_type)
                    PyAnalysis.__add_class_to_tree(class_tree, reduced_member_type, reduced_class_tree)

                for _, member_type in class_content['members']:
                    _, reduced_member_type, _ = PyAnalysis.__reduce_member_type(member_type)
                    PyAnalysis.__add_class_to_tree(class_tree, reduced_member_type, reduced_class_tree)

            for iterated_class_name, class_content in classes.items():
                for base in class_content['bases']:
                    if base == class_name:
                        PyAnalysis.__add_class_to_tree_if_not_exist(classes, file_name, iterated_class_name, reduced_class_tree)
                for _, member_type in class_content['statics']:
                    _, reduced_member_type, _ = PyAnalysis.__reduce_member_type(member_type)
                    if reduced_member_type == class_name:
                        PyAnalysis.__add_class_to_tree_if_not_exist(classes, file_name, iterated_class_name, reduced_class_tree)

                for _, member_type in class_content['members']:
                    _, reduced_member_type, _ = PyAnalysis.__reduce_member_type(member_type)
                    if reduced_member_type == class_name:
                        PyAnalysis.__add_class_to_tree_if_not_exist(classes, file_name, iterated_class_name, reduced_class_tree)

        return reduced_class_tree

    def read_all_python_files(self, from_dir: str, out_dir: str) -> Dict[str, List[str]]:
        class_tree: Dict[str, Dict[str, List[Dict[str, any]]]] = {}
        saver: Saver = Saver(out_dir)
        saver.append('@startuml')
        for file in list(Path(from_dir).rglob("*.py")):
            file_name: str = os.path.join(from_dir, file)
            class_tree[file_name] = self.__read_python_ast(file_name, from_dir, saver)
        PyAnalysis.__create_puml_files(class_tree, saver, from_dir, None)

        class_list: List[str] = PyAnalysis.__get_class_list(class_tree)
        for class_name in class_list:
             reduced_class_list = PyAnalysis.__get_reduced_class_list_from_class_name(class_tree, class_name, class_list)
             PyAnalysis.__create_puml_files(reduced_class_list, saver, from_dir, class_name)


def main(from_dir: str, out_dir: str) -> None:
    program_name = os.path.basename(sys.argv[0])
    
    # create the top-level parser
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('--from_dir', type=str, help='Specify where to read the python files from')
    parser.add_argument('--out_dir', type=str, help='Specify where to store all puml files')
    #parser.add_argument('--verbose', action='store_true', help='Detailed logging')
    args = parser.parse_args()
    if args.from_dir: from_dir = args.from_dir
    if args.out_dir: out_dir = args.out_dir
    PyAnalysis().read_all_python_files(from_dir, out_dir)


if __name__ == "__main__":
    main('/Users/jean-philippe.ulpiano/development/pygame/candy_cat', '/Users/jean-philippe.ulpiano/development/pygame/tmp-out')

#PyAnalysis().read_all_python_files('/Users/jean-philippe.ulpiano/development/pygame/candy_cat')