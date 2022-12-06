from __future__ import annotations
from typing import List, Dict, Tuple
import os

from pathlib import Path

from domain.saver import Saver
from domain.datastructure import Datastructure
from domain.datastructure import DatastructureHandler
from domain.datastructure import LanguageDependent
from infrastructure.python_adapter import PythonAdapter
from domain.diagram_creation import DiagramCreation                        

class ApplicationService:
    @staticmethod
    def read_all_python_files(from_dir: str, out_dir: str, language_dependent: LanguageDependent) -> Dict[str, List[str]]:
        saver: Saver = Saver(out_dir)
        diagram_creation: DiagramCreation = DiagramCreation(Datastructure(language_dependent))
        saver.append('@startuml')
        for file in list(Path(from_dir).rglob("*.py")):
            file_name: str = os.path.join(from_dir, file)
            PythonAdapter.read_python_ast(diagram_creation.get_data_structure(), file_name, from_dir, saver)
        DiagramCreation.create_puml_files(diagram_creation.get_data_structure(), saver, from_dir, None)

        class_list: List[str] = diagram_creation.get_data_structure().get_classname_list()
        for class_name in class_list:
             reduced_class_list = DatastructureHandler.create_reduced_class_list_from_class_name_list(\
                diagram_creation.get_data_structure(), [class_name])
             DiagramCreation.create_puml_files(reduced_class_list, saver, from_dir, class_name)

        class_name_list_grouped_by_namespaces: Dict[List[str]] = \
            DatastructureHandler.get_class_name_list_grouped_by_namespaces(diagram_creation.get_data_structure())
        for namespace_name, class_name_list in class_name_list_grouped_by_namespaces.items():
             reduced_namespace_list = DatastructureHandler.create_reduced_class_list_from_class_name_list(\
                diagram_creation.get_data_structure(), class_name_list)
             DiagramCreation.create_puml_files(reduced_namespace_list, saver, from_dir, namespace_name)