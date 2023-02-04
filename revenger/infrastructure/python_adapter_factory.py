import os

from infrastructure.generic_classes import GenericLogger, GenericPythonAdapter, GenericSaver
from infrastructure.python_adapter import PythonAdapter
from infrastructure.python_adapter_v2 import PythonAdapterV2

from os import environ
class PythonAdapterFactory:
    PY_ADAPTER_LATEST_ENV_VAR = "PY_ADAPTER_LATEST"

    def __init__(self, saver: GenericSaver, logger: GenericLogger):
        self.saver = saver
        self.logger = logger

    def create_adapter(self) -> GenericPythonAdapter:

        if self.PY_ADAPTER_LATEST_ENV_VAR in environ:
            return PythonAdapterV2(self.saver, self.logger)

        return PythonAdapter(self.saver, self.logger)


