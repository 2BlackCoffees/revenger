from __future__ import annotations
from typing import List, Dict, Tuple
import os

from pathlib import Path

from domain.saver import Saver
from domain.logger import Logger

from domain.datastructure import Datastructure
from domain.datastructure import DatastructureHandler
from domain.datastructure import LanguageDependent
from domain.diagram_creation import DiagramCreation                        

from infrastructure.python_adapter import PythonAdapter

class ApplicationService:

    @staticmethod
    def read_all_python_files(from_dir: str, out_dir: str, logger: Logger, language_dependent: LanguageDependent) -> Dict[str, List[str]]:
        saver: Saver = Saver(out_dir, logger)
        diagram_creation: DiagramCreation = DiagramCreation(Datastructure(language_dependent, logger), saver, logger)
        saver.append('@startuml')
        for file in list(Path(from_dir).rglob("*.py")):
            file_name: str = os.path.join(from_dir, file)
            PythonAdapter(saver, logger).read_python_ast(\
                diagram_creation.get_data_structure(), file_name, from_dir)
        diagram_creation.create_puml_files(from_dir, None)

        class_list: List[str] = diagram_creation.get_data_structure().get_classname_list()
        for class_name in class_list:
             reduced_class_list_datastructure = \
                DatastructureHandler(diagram_creation.get_data_structure(), logger)\
                    .create_reduced_class_list_from_class_name_list([class_name])
             class_based_diagram_creation: DiagramCreation = \
                DiagramCreation(reduced_class_list_datastructure, saver, logger)
             class_based_diagram_creation.create_puml_files(from_dir, class_name)

        class_name_list_grouped_by_namespaces: Dict[List[str]] = \
            DatastructureHandler(diagram_creation.get_data_structure(), logger)\
                .get_class_name_list_grouped_by_namespaces()
        for namespace_name, class_name_list in class_name_list_grouped_by_namespaces.items():
             reduced_namespace_list = \
                DatastructureHandler(diagram_creation.get_data_structure(), logger).\
                    create_reduced_class_list_from_class_name_list(class_name_list)
             namespace_based_diagram_creation: DiagramCreation = \
                DiagramCreation(reduced_namespace_list, saver, logger)
             namespace_based_diagram_creation.create_puml_files(from_dir, namespace_name)