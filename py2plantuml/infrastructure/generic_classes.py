from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

class GenericSubDataStructure(ABC):
    @abstractmethod
    def set_abstract(self) -> None:
        """
        """

    @abstractmethod
    def add_base_class(self, base_class: str) -> None:
        """
        """

    @abstractmethod
    def add_static(self, static_name: str, static_type: str) -> None:
        """
        """

    @abstractmethod
    def add_method(self, method_name: str, arguments: List[Tuple[str, str]]) -> None:
        """
        """

    @abstractmethod
    def add_variable(self, variable_name: str, variable_type: str, is_member: bool) -> None:
        """
        """

    @abstractmethod
    def add_inner_class(self, inner_class_name: str) -> None:
        """
        """

class GenericDatastructure(ABC):
    @abstractmethod
    def get_package_name(self, parameters: List[str]):
        """
        """
    @abstractmethod
    def append_class(self, filename: str, filemodule: str, from_imports: Dict[str, str], fqdn_class_name: str) -> GenericSubDataStructure:
        """
        """

    @abstractmethod
    def get_skip_types(self) -> List[str]:
        """
        """

class GenericSaver(ABC):
    @abstractmethod
    def append(self, line: str):
        """
        """
class GenericLogger(ABC):
    @abstractmethod
    def log_debug(self, line: str):
        """
        """