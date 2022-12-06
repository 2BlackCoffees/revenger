from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
import re

from pprint import pprint

from domain.saver import Saver
from domain.logger import Logger
from domain.common import Common
from domain.datastructure import Datastructure



class DiagramCreation:
    DETAILED_FILENAME_SUFFIX: str           = '-diagram-detailed.puml'
    SIMPLIFIED_FILENAME_SUFFIX: str         = '-diagram-simplified.puml'
    DETAILED_PER_NS_FILE_NAME_SUFFIX: str   = '-diagram-detailed-grouped-per-namespace.puml'
    SIMPLIFIED_PER_NS_FILE_NAME_SUFFIX: str = '-diagram-simplified-grouped-per-namespace.puml'

    def __init__(self, datastructure: Datastructure):
        self.datastructure: Datastructure = datastructure
    
    def get_data_structure(self) -> Datastructure:
        return self.datastructure

    @staticmethod
    def __get_file_name_from_class_namespace_name(detailed: bool, grouped_per_ns: bool, class_name: str, want_svg_file: bool) -> str:
        file_name: str = ''
        if detailed:
            if grouped_per_ns:
                file_name = f'{class_name}{DiagramCreation.DETAILED_PER_NS_FILE_NAME_SUFFIX}'
            else:
                file_name = f'{class_name}{DiagramCreation.DETAILED_FILENAME_SUFFIX}'
        else:
            if grouped_per_ns:
                file_name = f'{class_name}{DiagramCreation.SIMPLIFIED_PER_NS_FILE_NAME_SUFFIX}'
            else:
                file_name = f'{class_name}{DiagramCreation.SIMPLIFIED_FILENAME_SUFFIX}'            

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
        full_detailed_file_name: str            = f'full{DiagramCreation.DETAILED_FILENAME_SUFFIX}'
        full_simplified_file_name: str          = f'full{DiagramCreation.SIMPLIFIED_FILENAME_SUFFIX}'
        full_detailed_file_name_per_ns: str     = f'full{DiagramCreation.DETAILED_PER_NS_FILE_NAME_SUFFIX}'
        full_simplified_file_name_per_ns: str   = f'full{DiagramCreation.SIMPLIFIED_PER_NS_FILE_NAME_SUFFIX}'
        
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

        user_info_puml_file: str = DiagramCreation.__get_user_info(detailed, grouped_per_ns, class_namespace_name)
        puml_file: str = DiagramCreation.__get_file_name_from_class_namespace_name(detailed, grouped_per_ns, class_namespace_name, False)

        user_info_opposite_detailed_svg: str = DiagramCreation.__get_user_info(not detailed, grouped_per_ns, class_namespace_name)
        svg_file_name_opposite_detailed: str = DiagramCreation.__get_file_name_from_class_namespace_name(not detailed, grouped_per_ns, class_namespace_name, True)

        full_file_name: str = full_file_name_simplified_per_ns
        user_info_full_file_name: str = f"Full diagram **simplified** and **grouped per namespace**"

        if detailed:
            full_file_name: str = full_file_name_detailed_per_ns
            user_info_full_file_name = f"Full diagram **detailed** and **grouped per namespace**"

        return user_info_puml_file, puml_file, \
            user_info_opposite_detailed_svg, svg_file_name_opposite_detailed, \
                user_info_full_file_name, full_file_name




    @staticmethod
    def __get_namespace_name(namespace_list: List[str], index: int, detailed: bool, grouped_per_ns: bool) -> str:
        namespace_name: str = '.'.join([ namespace for namespace in namespace_list[0: index]])

        namespace_filtered_filename: str = DiagramCreation.__get_file_name_from_class_namespace_name(detailed, grouped_per_ns, namespace_name, True)

        return f'namespace {namespace_name} [[{namespace_filtered_filename}]] {{'

    @staticmethod
    def __sub_namespace_handler(previous_sub_namespace_list: List[str], current_sub_namespace_list: List[str], detailed: bool, grouped_per_ns: bool, saver: Saver, ending_file: bool) -> None:
        
        if ending_file:

            if len(previous_sub_namespace_list) > 0 and \
                saver.removed_last_line_if_same(DiagramCreation.__get_namespace_name(previous_sub_namespace_list, len(previous_sub_namespace_list), detailed, grouped_per_ns)):
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
                saver.append(DiagramCreation.__get_namespace_name(current_sub_namespace_list, index + 1, detailed, grouped_per_ns))
            return          
        
        root_index: int = 0
        index: int = 0
        if len(current_sub_namespace_list) == 0 or current_sub_namespace_list[0] not in previous_sub_namespace_list:
            if saver.removed_last_line_if_same(DiagramCreation.__get_namespace_name(previous_sub_namespace_list, len(previous_sub_namespace_list), detailed, grouped_per_ns)):
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
                if saver.removed_last_line_if_same(DiagramCreation.__get_namespace_name(previous_sub_namespace_list, len(previous_sub_namespace_list), detailed, grouped_per_ns)):
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
            saver.append(DiagramCreation.__get_namespace_name(current_sub_namespace_list, sub_index + 1, detailed, grouped_per_ns))

    @staticmethod
    def __create_puml_classes(datastructure: Datastructure, detailed: bool, grouped_per_ns: bool, saver: Saver, from_dir: str) -> None:
        previous_sub_namespace_list: List[str] = []
        list_file_names = datastructure.get_sorted_list_filenames()
        for file_name in list_file_names:
            classes: List[Datastructure.SubDataStructure] = datastructure.get_datastructures_from_filename(file_name)
            current_sub_namespace_list = datastructure.get_language_dependent().get_package_name_from_filename(file_name, from_dir).split('.')[0:-1]
            if grouped_per_ns:
                DiagramCreation.__sub_namespace_handler(previous_sub_namespace_list, current_sub_namespace_list, detailed, grouped_per_ns, saver, False)

            empty_spaces = '  ' * (max(len(current_sub_namespace_list) - 1, 0))
            for sub_datastructure in classes:
                fqdn_class_name: str = sub_datastructure.get_fqdn_class_name()
                is_abstract: str = 'abstract ' if sub_datastructure.is_abstract() else ''
                    
                saver.append(f'{empty_spaces}{is_abstract}class {fqdn_class_name} [[{DiagramCreation.__get_file_name_from_class_namespace_name(detailed, grouped_per_ns, fqdn_class_name, True)}]]{{')
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
                DiagramCreation.__sub_namespace_handler(previous_sub_namespace_list, None, detailed, grouped_per_ns, saver, True)

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
                            saver.append(f'{base} <|-- {class_name}')
                        else:
                            Logger.log_debug(f'  Relation skipped: {base} <|-- {class_name} (create_all_relation: {create_all_relation}, datastructure.class_exists({base}): {datastructure.class_exists(base)})')
                static_field: Datastructure.Static
                for static_field in sub_datastructure.get_static_fields():
                    _, naked_type, _ = Common.reduce_member_type(static_field.static_type)
                    if create_all_relation or datastructure.class_exists(naked_type):
                        DiagramCreation.__create_puml_connection(datastructure, class_name, static_field.static_type, True, saver)
                    else:
                        Logger.log_debug(f'  Relation skipped: {class_name} ?-- {naked_type} (create_all_relation: {create_all_relation}, datastructure.class_exists({naked_type}): {datastructure.class_exists(naked_type)})')
                variable_field: Datastructure.Variable
                for variable_field in sub_datastructure.get_variable_fields():
                    _, naked_type, _ = Common.reduce_member_type(variable_field.variable_type)
                    if create_all_relation or datastructure.class_exists(naked_type):
                        DiagramCreation.__create_puml_connection(datastructure, class_name, variable_field.variable_type, variable_field.is_member, saver)
                    else:
                        Logger.log_debug(f'  Relation skipped: {class_name} ?-- {naked_type} (create_all_relation: {create_all_relation}, datastructure.class_exists({naked_type}): {datastructure.class_exists(naked_type)})')
                for method_field in sub_datastructure.get_method_fields():
                    for parameter in method_field.parameters:
                        _, naked_type, _ = Common.reduce_member_type(parameter.user_type)
                        if create_all_relation or datastructure.class_exists(naked_type):
                            DiagramCreation.__create_puml_connection(datastructure, class_name, parameter.user_type, False, saver)
                        else:
                            Logger.log_debug(f'  Relation skipped: {class_name} ?-- {naked_type} (create_all_relation: {create_all_relation}, datastructure.class_exists({naked_type}): {datastructure.class_exists(naked_type)})')
            
    @staticmethod
    def __create_full_diagram(datastructure: Datastructure, detailed: bool, grouped_per_ns: bool, initial_saver: Saver, from_dir: str, class_namespace_name: str = None) -> None:
        saver: Saver = initial_saver.clone()
        user_info_filename, filename, user_info_link_1, link_path_1, user_info_link_2, link_path_2 = \
            DiagramCreation.__get_file_name(detailed, grouped_per_ns, class_namespace_name)
        saver.append(f'title <size:20>{user_info_filename}</size>')
        saver.append( f'note "Your are analyzing:\\n{user_info_filename}\\n\\n' +
                      '==Filter==\\n' +
                      'You can click either the namespaces \\n' + 
                      'or class names for filtering them and their\\n' +
                      'direct dependencies.\\n\\n' +
                      '==Select other==\\n' +
                      f'* {user_info_link_1}:\\n   [[{link_path_1}]]\\n* {user_info_link_2}:\\n   [[{link_path_2}]]" as FloatingNote')
        DiagramCreation.__create_puml_classes(datastructure, detailed, grouped_per_ns, saver, from_dir)
        create_all_relation: bool = class_namespace_name == None
        DiagramCreation.__create_puml_classes_relations(datastructure, saver, create_all_relation)
        saver.append('@enduml')
        saver.save(filename)

    @staticmethod
    def create_puml_files(datastructure: Datastructure, saver: Saver, from_dir: str, class_name: str = None) -> None:
        DiagramCreation.__create_full_diagram(datastructure, True,  False,  saver, from_dir, class_name)
        DiagramCreation.__create_full_diagram(datastructure, True,  True,   saver, from_dir, class_name)
        DiagramCreation.__create_full_diagram(datastructure, False, False,  saver, from_dir, class_name)
        DiagramCreation.__create_full_diagram(datastructure, False, True,   saver, from_dir, class_name)
