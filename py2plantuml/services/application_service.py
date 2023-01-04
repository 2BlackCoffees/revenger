from __future__ import annotations
from typing import List, Dict, Tuple
import os
from enum import Enum
from pathlib import Path

from domain.saver import Saver
from domain.logger import Logger

from domain.datastructure import Datastructure
from domain.datastructure import DatastructureHandler
from domain.datastructure import LanguageDependent
from domain.diagram_creation import DiagramCreation                        

from infrastructure.python_adapter import PythonAdapter
from infrastructure.yaml_adapter import YAMLAdapter
 
class SourceType(Enum):
    PYTHON_SOURCE = 1,
    YAML_SOURCE = 2

class ApplicationService:

    @staticmethod
    def fill_datastructure_with_all_source_files(from_dir: str, diagram_creation: DiagramCreation, logger: Logger, saver: Saver, source_type: SourceType):
        file_types: Tuple[str]
        if source_type == SourceType.PYTHON_SOURCE:
            file_types = ["*.py"]
            logger.log_info("Searching for python files")
        elif source_type == SourceType.YAML_SOURCE:
            file_types = ["*.yml", "*.yaml"]
            logger.log_info("Searching for yaml files")
        file_list = []
        for exentions in file_types:
            file_list.extend(list(Path(from_dir).rglob(exentions)))
        for file in file_list:
            file_name: str = os.path.join(from_dir, file)
            if source_type == SourceType.PYTHON_SOURCE:
                PythonAdapter(saver, logger).read_python_ast(\
                    diagram_creation.get_data_structure(), file_name, from_dir)
            elif source_type == SourceType.YAML_SOURCE:
                YAMLAdapter(saver, logger).read(\
                    diagram_creation.get_data_structure(), file_name, from_dir)

    @staticmethod
    def read_all_source_files(from_dir: str, out_dir: str, \
            logger: Logger, language_dependent: LanguageDependent, \
                skip_uses_relation: bool, source_type: SourceType) -> Dict[str, List[str]]:
        saver: Saver = Saver(out_dir, logger)
        diagram_creation: DiagramCreation = DiagramCreation(Datastructure(language_dependent, logger), saver, logger)
        saver.append('@startuml')

        ApplicationService.fill_datastructure_with_all_source_files(from_dir, diagram_creation, logger, saver, source_type)
        diagram_creation.create_referenced_but_inexistent_classes()
        # Create full diagrams
        diagram_creation.create_puml_files(from_dir, skip_uses_relation, None)

        # Create diagrams filtered out by class name
        class_list: List[str] = diagram_creation.get_data_structure().get_classname_list()
        for class_name in class_list:
             reduced_class_list_datastructure = \
                DatastructureHandler(diagram_creation.get_data_structure(), logger)\
                    .create_reduced_class_list_from_class_name_list([class_name])
             class_based_diagram_creation: DiagramCreation = \
                DiagramCreation(reduced_class_list_datastructure, saver, logger)
             class_based_diagram_creation.create_puml_files(from_dir, skip_uses_relation, class_name)

        # Create diagrams filtered out by namespace
        class_name_list_grouped_by_namespaces: Dict[List[str]] = \
            DatastructureHandler(diagram_creation.get_data_structure(), logger)\
                .get_class_name_list_grouped_by_namespaces()
        for namespace_name, class_name_list in class_name_list_grouped_by_namespaces.items():
             reduced_namespace_list = \
                DatastructureHandler(diagram_creation.get_data_structure(), logger).\
                    create_reduced_class_list_from_class_name_list(class_name_list)
             namespace_based_diagram_creation: DiagramCreation = \
                DiagramCreation(reduced_namespace_list, saver, logger)
             namespace_based_diagram_creation.create_puml_files(from_dir, skip_uses_relation, namespace_name)