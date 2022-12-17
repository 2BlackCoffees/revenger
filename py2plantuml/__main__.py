import os
import re
import sys
import argparse

from domain.datastructure import PythonLanguage
from domain.diagram_creation import DiagramCreation
from domain.logger import Logger
from services.application_service import ApplicationService
from services.application_service import SourceType

    

def main(from_dir: str, out_dir: str) -> None:
    program_name = os.path.basename(sys.argv[0])
    
    # create the top-level parser
    source_type: SourceType = SourceType.PYTHON_SOURCE
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('--from_dir', type=str, help='Specify where to read the python files from', required=True)
    parser.add_argument('--out_dir', type=str, help='Specify where to store all puml files', required=True)
    parser.add_argument('--skip_uses_relation', action="store_true", help='Do not create use relationship')
    parser.add_argument('--info', action="store_true", help='Set logging to info')
    parser.add_argument('--debug', action="store_true", help='Set logging to debug')
    parser.add_argument('--trace', action="store_true", help='Set logging to trace')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--python', action='store_true', help='Use python code as source')
    group.add_argument('--yaml', action='store_true', help='Use yaml code as source')
    args = parser.parse_args()
    if args.from_dir: from_dir = args.from_dir
    if args.out_dir: out_dir = args.out_dir
    if args.yaml:
        source_type = SourceType.YAML_SOURCE
    print(f"source_type: {source_type}")

    logger: Logger = Logger(args.info, args.debug, args.trace)
    if not from_dir.startswith('/'):
        logger.log_error(f'Source directory ({from_dir}) is invalid, it requires an absolute path! Exiting!')
        exit(1)

    ApplicationService.read_all_source_files(from_dir, out_dir, logger, PythonLanguage(logger), args.skip_uses_relation, source_type)

    file_name: str = os.path.join(os.getcwd(), out_dir, re.sub('puml$', 'svg', f'full{DiagramCreation.DETAILED_FILENAME_SUFFIX}'))
    logger.log_warn(f'Please open {file_name} in your browser')



if __name__ == "__main__":
    main('/Users/jean-philippe.ulpiano/development/pygame/candy_cat', '/Users/jean-philippe.ulpiano/development/pygame/tmp-out')
