from __future__ import annotations

import statistics

from domain.common import Common
from domain.datastructure import Datastructure
from domain.logger import Logger


class StatisticValues:
    class Values:
        child_classes: float = 0
        parent_classes: float = 0
        aggregations_to: float = 0
        aggregations_from: float = 0
        uses_to: float = 0
        uses_from: float = 0

    mean: Values
    variance: Values
    pvariance: Values
    max: Values

    def __init__(self):
        self.mean = StatisticValues.Values()
        self.variance = StatisticValues.Values()
        self.pvariance = StatisticValues.Values()
        self.max = StatisticValues.Values()


class ClassConnectionsDetails:
    _class_name: str = None
    _number_parent_classes: int = 0
    _number_child_classes: int = 0
    _number_aggregations_to: int = 0
    _number_aggregations_from: int = 0
    _number_uses_to: int = 0
    _number_uses_from: int = 0
    _skip_type: list[str] = []

    THRESHOLD_AGGREGATION_FROM = 20
    THRESHOLD_AGGREGATION_TO = 50
    THRESHOLD_USES_FROM = 20
    THRESHOLD_USES_TO = 50
    THRESHOLD_CHILD_CLASSES = 50
    THRESHOLD_PARENT_CLASSES = 5

    def filter_class_name(self, class_name_list: list[str]) -> list[str]:
        return [
            class_name
            for class_name in class_name_list
            if class_name not in self._skip_type
        ]

    def __init__(
        self,
        skip_types: list[str],
        sub_datastructure: Datastructure.SubDataStructure,
    ) -> None:
        self._skip_type = skip_types
        self._class_name = sub_datastructure.fqdn_class_name
        self._number_parent_classes = len(
            self.filter_class_name(sub_datastructure.get_base_classes())
        )
        self._number_aggregations_to = len(
            self.filter_class_name(sub_datastructure.get_static_fields())
        ) + len(
            self.filter_class_name(sub_datastructure.get_variable_fields())
        )
        self._number_uses_to = 0
        for method_field in sub_datastructure.get_method_fields():
            self._number_uses_to += len(
                self.filter_class_name(method_field.parameters)
            ) + len(
                method_field.variables
            )  # TODO: Filter as well variable types

    def get_class_name(self) -> str:
        return self._class_name

    def get_number_uses_to(self) -> int:
        return self._number_uses_to

    def get_number_parent_classes(self) -> int:
        return self._number_parent_classes

    def get_number_aggregations_to(self) -> int:
        return self._number_aggregations_to

    def get_number_uses_from(self) -> int:
        return self._number_uses_from

    def get_number_child_classes(self) -> int:
        return self._number_child_classes

    def get_number_aggregations_from(self) -> int:
        return self._number_aggregations_from

    def increment_number_child_classes(self) -> None:
        self._number_child_classes += 1

    def increment_aggregations_from(self) -> None:
        self._number_aggregations_from += 1

    def increment_uses_from(self) -> None:
        self._number_uses_from += 1

    def get_max_of_all(self) -> int:
        return max(
            self._number_uses_to / ClassConnectionsDetails.THRESHOLD_USES_TO,
            self._number_parent_classes
            / ClassConnectionsDetails.THRESHOLD_PARENT_CLASSES,
            self._number_aggregations_to
            / ClassConnectionsDetails.THRESHOLD_AGGREGATION_TO,
            self._number_uses_from
            / ClassConnectionsDetails.THRESHOLD_USES_FROM,
            self._number_child_classes
            / ClassConnectionsDetails.THRESHOLD_CHILD_CLASSES,
            self._number_aggregations_from
            / ClassConnectionsDetails.THRESHOLD_AGGREGATION_FROM,
        )

    @staticmethod
    def mean(points_list: list[int]) -> float:
        return (
            statistics.mean(points_list)
            if points_list is not None and len(points_list) > 0
            else 0
        )

    @staticmethod
    def variance(points_list: list[int]) -> float:
        return (
            statistics.variance(points_list)
            if points_list is not None and len(points_list) > 0
            else 0
        )

    @staticmethod
    def pvariance(points_list: list[int]) -> float:
        return (
            statistics.pvariance(points_list)
            if points_list is not None and len(points_list) > 0
            else 0
        )

    @staticmethod
    def max(points_list: list[int]) -> float:
        return (
            max(points_list)
            if points_list is not None and len(points_list) > 0
            else 0
        )

    @staticmethod
    def get_statistics(
        dict_class_connection_details: dict[str, ClassConnectionsDetails]
    ) -> StatisticValues:
        child_classes: list[int] = [
            connection.get_number_child_classes()
            for connection in dict_class_connection_details.values()
        ]
        aggregations_from: list[int] = [
            connection.get_number_aggregations_from()
            for connection in dict_class_connection_details.values()
        ]
        uses_from: list[int] = [
            connection.get_number_uses_from()
            for connection in dict_class_connection_details.values()
        ]
        parent_classes: list[int] = [
            connection.get_number_parent_classes()
            for connection in dict_class_connection_details.values()
        ]
        aggregations_to: list[int] = [
            connection.get_number_aggregations_to()
            for connection in dict_class_connection_details.values()
        ]
        uses_to: list[int] = [
            connection.get_number_uses_to()
            for connection in dict_class_connection_details.values()
        ]

        return_value: StatisticValues = StatisticValues()

        return_value.mean.child_classes = ClassConnectionsDetails.mean(
            child_classes
        )
        return_value.mean.aggregations_from = ClassConnectionsDetails.mean(
            aggregations_from
        )
        return_value.mean.uses_from = ClassConnectionsDetails.mean(uses_from)
        return_value.mean.parent_classes = ClassConnectionsDetails.mean(
            parent_classes
        )
        return_value.mean.aggregations_to = ClassConnectionsDetails.mean(
            aggregations_to
        )
        return_value.mean.uses_to = ClassConnectionsDetails.mean(uses_to)

        return_value.variance.child_classes = ClassConnectionsDetails.variance(
            child_classes
        )
        return_value.variance.aggregations_from = (
            ClassConnectionsDetails.variance(aggregations_from)
        )
        return_value.variance.uses_from = ClassConnectionsDetails.variance(
            uses_from
        )
        return_value.variance.parent_classes = (
            ClassConnectionsDetails.variance(parent_classes)
        )
        return_value.variance.aggregations_to = (
            ClassConnectionsDetails.variance(aggregations_to)
        )
        return_value.variance.uses_to = ClassConnectionsDetails.variance(
            uses_to
        )

        return_value.pvariance.child_classes = (
            ClassConnectionsDetails.pvariance(child_classes)
        )
        return_value.pvariance.aggregations_from = (
            ClassConnectionsDetails.pvariance(aggregations_from)
        )
        return_value.pvariance.uses_from = ClassConnectionsDetails.pvariance(
            uses_from
        )
        return_value.pvariance.parent_classes = (
            ClassConnectionsDetails.pvariance(parent_classes)
        )
        return_value.pvariance.aggregations_to = (
            ClassConnectionsDetails.pvariance(aggregations_to)
        )
        return_value.pvariance.uses_to = ClassConnectionsDetails.pvariance(
            uses_to
        )

        return_value.max.child_classes = ClassConnectionsDetails.max(
            child_classes
        )
        return_value.max.aggregations_from = ClassConnectionsDetails.max(
            aggregations_from
        )
        return_value.max.uses_from = ClassConnectionsDetails.max(uses_from)
        return_value.max.parent_classes = ClassConnectionsDetails.max(
            parent_classes
        )
        return_value.max.aggregations_to = ClassConnectionsDetails.max(
            aggregations_to
        )
        return_value.max.uses_to = ClassConnectionsDetails.max(uses_to)

        return return_value


class StatisticsCompute:
    def __init__(self, datastructure: Datastructure, logger: Logger):
        self.datastructure: Datastructure = datastructure
        self.logger = logger

    def get_all_classes_and_connections(
        self,
    ) -> tuple[
        dict[str, ClassConnectionsDetails],
        ClassConnectionsDetails.StatisticValues,
    ]:
        list_file_namespaces = self.datastructure.get_sorted_name_spaces()
        dict_class_connection_details: dict[str, ClassConnectionsDetails] = {}
        # Fill all known list_class_connection_details
        for namespace_name in list_file_namespaces:
            classes: list[
                Datastructure.SubDataStructure
            ] = self.datastructure.get_datastructures_from_namespace(
                namespace_name
            )
            for sub_datastructure in classes:
                dict_class_connection_details[
                    sub_datastructure.get_fqdn_class_name()
                ] = ClassConnectionsDetails(
                    self.datastructure.get_skip_types(), sub_datastructure
                )
        # By default data structure knows the dependencies to other classes
        # For statistics we need dependencies from other classes
        # this is computed here
        for namespace_name in list_file_namespaces:
            sub_datastructure: Datastructure.SubDataStructure
            for (
                sub_datastructure
            ) in self.datastructure.get_datastructures_from_namespace(
                namespace_name
            ):
                class_name: str = sub_datastructure.get_fqdn_class_name()
                if class_name not in self.datastructure.get_skip_types():
                    for base in sub_datastructure.get_base_classes():
                        if (
                            base not in self.datastructure.get_skip_types()
                            and base in dict_class_connection_details.keys()
                        ):
                            dict_class_connection_details[
                                base
                            ].increment_number_child_classes()

                static_field: Datastructure.Static
                for static_field in sub_datastructure.get_static_fields():
                    _, naked_type, _ = Common.reduce_member_type(
                        static_field.static_type
                    )
                    if naked_type in dict_class_connection_details.keys():
                        dict_class_connection_details[
                            naked_type
                        ].increment_aggregations_from()

                variable_field: Datastructure.Variable
                for variable_field in sub_datastructure.get_variable_fields():
                    _, naked_type, _ = Common.reduce_member_type(
                        variable_field.variable_type
                    )
                    if naked_type in dict_class_connection_details.keys():
                        dict_class_connection_details[
                            naked_type
                        ].increment_aggregations_from()

                for method_field in sub_datastructure.get_method_fields():
                    for parameter in method_field.parameters:
                        _, naked_type, _ = Common.reduce_member_type(
                            parameter.user_type
                        )
                        if naked_type in dict_class_connection_details.keys():
                            dict_class_connection_details[
                                naked_type
                            ].increment_uses_from()
                    for variable in method_field.variables:
                        _, naked_type, _ = Common.reduce_member_type(
                            variable.variable_type
                        )
                        if naked_type in dict_class_connection_details.keys():
                            dict_class_connection_details[
                                naked_type
                            ].increment_uses_from()

        return (
            dict_class_connection_details,
            ClassConnectionsDetails.get_statistics(
                dict_class_connection_details
            ),
        )
