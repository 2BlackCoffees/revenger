from __future__ import annotations
from typing import List, Dict, Tuple
import os
from domain.logger import Logger

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
        Logger.log_info(f'INFO: Creating file {filename}')
        with open(filename, 'w', encoding="utf-8") as file:
            file.write('\n'.join(self.lines_to_save))

    def clone(self) -> Saver:
        return Saver(self.out_dir, self)

    def removed_last_line_if_same(self, line: str) -> bool:
        return_value = False
        old_value = None if len(self.lines_to_save) == 0 else self.lines_to_save[-1]

        if len(self.lines_to_save) > 0 and line == self.lines_to_save[-1]:
            self.lines_to_save.pop()
            return_value = True
        self.lines_to_save.append(f'\'Compared {line} with last element of {old_value}' )
        return return_value