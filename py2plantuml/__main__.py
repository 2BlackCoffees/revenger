import os
import re
import sys
import argparse

from domain.datastructure import PythonLanguage
from domain.diagram_creation import DiagramCreation
from domain.logger import Logger
from services.application_service import ApplicationService

                        

def main(from_dir: str, out_dir: str) -> None:
    program_name = os.path.basename(sys.argv[0])
    
    # create the top-level parser
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('--from_dir', type=str, help='Specify where to read the python files from')
    parser.add_argument('--out_dir', type=str, help='Specify where to store all puml files')
    parser.add_argument('--skip_uses_relation', action="store_true", help='Do not create use relationship')
    parser.add_argument('--info', action="store_true", help='Set logging to info')
    parser.add_argument('--debug', action="store_true", help='Set logging to debug')
    parser.add_argument('--trace', action="store_true", help='Set logging to trace')
    args = parser.parse_args()
    if args.from_dir: from_dir = args.from_dir
    if args.out_dir: out_dir = args.out_dir
    logger: Logger = Logger(args.info, args.debug, args.trace)

    ApplicationService.read_all_python_files(from_dir, out_dir, logger, PythonLanguage(logger), args.skip_uses_relation)

    file_name: str = os.path.join(os.getcwd(), out_dir, re.sub('puml$', 'svg', f'full{DiagramCreation.DETAILED_FILENAME_SUFFIX}'))
    logger.log_warn(f'Please open {file_name} in your browser')



if __name__ == "__main__":
    main('/Users/jean-philippe.ulpiano/development/pygame/candy_cat', '/Users/jean-philippe.ulpiano/development/pygame/tmp-out')
