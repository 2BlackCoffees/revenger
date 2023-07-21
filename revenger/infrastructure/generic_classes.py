from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class LanguageDependent(ABC):
    @abstractmethod
    def get_skip_types(self) -> List[str]:
        """ """

    @abstractmethod
    def clean_type(self, type: str) -> str:
        """ """


class GenericSubDataStructure(ABC):
    @abstractmethod
    def set_abstract(self) -> None:
        """ """

    def set_interface(self) -> None:
        """ """

    @abstractmethod
    def add_base_class(
        self, base_class: str, add_no_module: bool = False
    ) -> None:
        """ """

    @abstractmethod
    def add_static(self, static_name: str, static_type: str) -> None:
        """ """

    @abstractmethod
    def add_method(
        self,
        method_name: str,
        arguments: List[Tuple[str, str]],
        is_private: bool,
        method_variables: List[Tuple[str, str]],
    ) -> None:
        """ """

    @abstractmethod
    def add_variable(
        self, variable_name: str, variable_type: str, is_member: bool
    ) -> None:
        """ """

    @abstractmethod
    def add_inner_class(self, inner_class_name: str) -> None:
        """ """


class GenericDatastructure(ABC):
    @abstractmethod
    def append_class(
        self,
        filename: str,
        filemodule: str,
        from_imports: Dict[str, str],
        fqdn_class_name: str,
        name_space_list: List[str],
    ) -> GenericSubDataStructure:
        """ """

    @abstractmethod
    def get_skip_types(self) -> List[str]:
        """ """

    @abstractmethod
    def get_language_dependent(self) -> LanguageDependent:
        """ """


class GenericSaver(ABC):
    @abstractmethod
    def append(self, line: str):
        """ """


class GenericLogger(ABC):
    @abstractmethod
    def log_debug(self, line: str):
        """ """

    @abstractmethod
    def log_trace(self, line: str):
        """ """
