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
    summary_page_only = False

    #Debug entries:
    # from_dir = '/Users/jean-philippe.ulpiano/development/revenger/out-tmp'
    # out_dir = '/Users/jean-philippe.ulpiano/development/revenger/out-tmp'
    # summary_page_only = True
    # source_type = SourceType.YAML_SOURCE

    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('--from_dir', type=str, help='Specify where to read the python files from', required=False)
    parser.add_argument('--out_dir', type=str, help='Specify where to store all puml files', required=False)
    parser.add_argument('--skip_uses_relation', action="store_true", help='Do not create use relationship')
    parser.add_argument('--skip_not_defined_classes', action="store_true", help='If a class is referenced but not defined, it will not be displayed (reduces memory needs)')
    parser.add_argument('--only_full_diagrams', action="store_true", help='Generate only full diagrams (Useful for debug)')
    parser.add_argument('--summary_page_only', action="store_true", help='Use with care: Generate a summary page only (This option will short circuit the processing)')
    parser.add_argument('--info', action="store_true", help='Set logging to info')
    parser.add_argument('--debug', action="store_true", help='Set logging to debug')
    parser.add_argument('--trace', action="store_true", help='Set logging to trace')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--python', action='store_true', help='Use python code as source')
    group.add_argument('--yaml', action='store_true', help='Use yaml code as source')
    args = parser.parse_args()
    if args.from_dir: from_dir = args.from_dir
    if args.out_dir: out_dir = args.out_dir
    if args.summary_page_only: summary_page_only = args.summary_page_only
    if args.yaml:
        source_type = SourceType.YAML_SOURCE

    logger: Logger = Logger(args.info, args.debug, args.trace)
    if not from_dir.startswith('/'):
        logger.log_error(f'Source directory ({from_dir}) is invalid, it requires an absolute path! Exiting!')
        exit(1)

    if not summary_page_only:
        logger.log_info('Generating all PUML diagrams')
        ApplicationService.generate_all_diagrams(from_dir, out_dir, logger, PythonLanguage(logger), \
                                                args.skip_uses_relation, args.skip_not_defined_classes,
                                                args.only_full_diagrams, source_type)

    else:
        logger.log_info('Generating HTML files')
        file_name = ApplicationService.create_summary_page(from_dir, out_dir, logger, PythonLanguage(logger), source_type)
        logger.log_warn(f'Please open {file_name} in your browser')



if __name__ == "__main__":
    main('/Users/jean-philippe.ulpiano/development/pygame/candy_cat', '/Users/jean-philippe.ulpiano/development/pygame/tmp-out')
