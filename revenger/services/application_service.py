from __future__ import annotations

import os
from enum import Enum
from pathlib import Path

from domain.datastructure import (Datastructure, DatastructureHandler,
                                  LanguageDependent)
from domain.diagram_creation import DiagramCreation
from domain.logger import Logger
from domain.saver import Saver
from domain.statistics_compute import (ClassConnectionsDetails,
                                       StatisticsCompute)
from infrastructure.python_adapter import PythonAdapter
from infrastructure.statistics_html import StatisticsHtml
from infrastructure.yaml_adapter import YAMLAdapter


class SourceType(Enum):
    PYTHON_SOURCE = (1,)
    YAML_SOURCE = 2


class ApplicationService:
    @staticmethod
    def fill_datastructure_with_all_source_files(
        from_dir: str,
        diagram_creation: DiagramCreation,
        logger: Logger,
        saver: Saver,
        source_type: SourceType,
    ):
        file_types: tuple[str]
        if source_type == SourceType.PYTHON_SOURCE:
            file_types = ["*.py"]
            logger.log_info("Searching for python files")
        elif source_type == SourceType.YAML_SOURCE:
            file_types = ["*.yml", "*.yaml"]
            logger.log_info("Searching for yaml files")
        file_list = []
        for exentions in file_types:
            file_list.extend(list(Path(from_dir).rglob(exentions)))
        if file_list is None or len(file_list) == 0:
            logger.log_error(
                f"No file type {file_types} could be found in directory {from_dir}!"
            )
        else:
            for file in file_list:
                file_name: str = os.path.join(from_dir, file)
                if source_type == SourceType.PYTHON_SOURCE:
                    PythonAdapter(saver, logger).read_python_ast(
                        diagram_creation.get_data_structure(),
                        file_name,
                        from_dir,
                    )
                elif source_type == SourceType.YAML_SOURCE:
                    YAMLAdapter(saver, logger).read(
                        diagram_creation.get_data_structure(),
                        file_name,
                        from_dir,
                    )

    @staticmethod
    def generate_all_diagrams(
        from_dir: str,
        out_dir: str,
        logger: Logger,
        language_dependent: LanguageDependent,
        skip_uses_relation: bool,
        skip_not_defined_classes: bool,
        no_full_diagrams: bool,
        source_type: SourceType,
        line_type: str,
    ) -> DiagramCreation:
        saver: Saver = Saver(out_dir, logger)
        diagram_creation: DiagramCreation = DiagramCreation(
            Datastructure(language_dependent, logger), saver, logger
        )
        saver.append("@startuml")
        if line_type is not None and line_type != "" and line_type != "curve":
            saver.append(f"skinparam linetype {line_type}")

        logger.log_info("Reading source files")
        ApplicationService.fill_datastructure_with_all_source_files(
            from_dir, diagram_creation, logger, saver, source_type
        )
        if not skip_not_defined_classes:
            logger.log_info("Filling data structure with inexistent classes")
            diagram_creation.create_referenced_but_inexistent_classes(
                skip_uses_relation
            )
        # Create full diagrams
        if not no_full_diagrams:
            logger.log_info("Creating highest level of PUML files")
            diagram_creation.create_puml_files(
                from_dir, skip_uses_relation, skip_not_defined_classes, None
            )
        else:
            logger.log_info("Skipping full diagrams")
        # Create diagrams filtered out by class name
        class_list: list[
            str
        ] = diagram_creation.get_data_structure().get_classname_list()
        for class_name in class_list:
            reduced_class_list_datastructure = DatastructureHandler(
                diagram_creation.get_data_structure(), logger
            ).create_reduced_class_list_from_class_name_list([class_name])
            class_based_diagram_creation: DiagramCreation = DiagramCreation(
                reduced_class_list_datastructure, saver, logger
            )
            logger.log_info(f"Creating PUML diagram for class {class_name}")
            class_based_diagram_creation.create_puml_files(
                from_dir,
                skip_uses_relation,
                skip_not_defined_classes,
                class_name,
            )

        # Create diagrams filtered out by namespace
        class_name_list_grouped_by_namespaces: dict[
            list[str]
        ] = DatastructureHandler(
            diagram_creation.get_data_structure(), logger
        ).get_class_name_list_grouped_by_namespaces()
        for (
            namespace_name,
            class_name_list,
        ) in class_name_list_grouped_by_namespaces.items():
            reduced_namespace_list = DatastructureHandler(
                diagram_creation.get_data_structure(), logger
            ).create_reduced_class_list_from_class_name_list(class_name_list)
            namespace_based_diagram_creation: DiagramCreation = (
                DiagramCreation(reduced_namespace_list, saver, logger)
            )
            logger.log_info(
                f"Creating PUML diagram for namespace {namespace_name}"
            )
            namespace_based_diagram_creation.create_puml_files(
                from_dir,
                skip_uses_relation,
                skip_not_defined_classes,
                namespace_name,
            )

        return diagram_creation

    @staticmethod
    def create_summary_page(
        from_dir: str,
        out_dir: str,
        logger: Logger,
        language_dependent: LanguageDependent,
        source_type: SourceType,
        summary_page_title: str,
    ) -> str:
        saver_dummy: Saver = Saver(out_dir, logger)

        logger.log_info("Populating data structure")
        diagram_creation: DiagramCreation = DiagramCreation(
            Datastructure(language_dependent, logger), saver_dummy, logger
        )
        ApplicationService.fill_datastructure_with_all_source_files(
            from_dir, diagram_creation, logger, saver_dummy, source_type
        )
        diagram_creation.create_referenced_but_inexistent_classes(
            skip_uses_relation=False
        )

        logger.log_info("Computing statistics")
        connection_details: dict[str, ClassConnectionsDetails] = []
        statistics: ClassConnectionsDetails.StatisticValues = None
        statistics_compute = StatisticsCompute(
            diagram_creation.get_data_structure(), logger
        )
        (
            connection_details,
            statistics,
        ) = statistics_compute.get_all_classes_and_connections()

        logger.log_info("Generating html file")
        return StatisticsHtml.create(
            connection_details,
            statistics,
            summary_page_title,
            out_dir,
            language_dependent,
            saver_dummy,
            logger,
        )
