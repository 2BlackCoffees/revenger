import os
import re
import sys
import argparse

from domain.datastructure import PythonLanguage
from domain.diagram_creation import DiagramCreation
from services.application_service import ApplicationService

                        

def main(from_dir: str, out_dir: str) -> None:
    program_name = os.path.basename(sys.argv[0])
    
    # create the top-level parser
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('--from_dir', type=str, help='Specify where to read the python files from')
    parser.add_argument('--out_dir', type=str, help='Specify where to store all puml files')
    args = parser.parse_args()
    if args.from_dir: from_dir = args.from_dir
    if args.out_dir: out_dir = args.out_dir

    ApplicationService.read_all_python_files(from_dir, out_dir, PythonLanguage())

    file_name: str = os.path.join(os.getcwd(), out_dir, re.sub('puml$', 'svg', f'full{DiagramCreation.DETAILED_FILENAME_SUFFIX}'))
    print(f'Please open {file_name} in your browser')



if __name__ == "__main__":
    main('/Users/jean-philippe.ulpiano/development/pygame/candy_cat', '/Users/jean-philippe.ulpiano/development/pygame/tmp-out')
