#!/bin/sh
from_dir=$1
out_dir=$2
plantuml=/opt/homebrew/bin/plantuml
python=python3

function usage(){
    echo "$(basename $0) [-i | --from_dir ] [ -o | --out_dir] [-d | --dependency_install] [-h | --help]"
}

while [[ "$1" != "" ]]; do
    case $1 in
        -i | --from_dir )
        from_dir=$2;
        shift;
        ;;
        -o | --out_dir )
        out_dir=$2;
        shift;
        ;;
        -d | --dependency_install )
        echo "Downloading plantuml java binary in the current dir from github......"
        wget -O plantuml.jar https://github.com/plantuml/plantuml/releases/download/v1.2022.13/plantuml.jar
        echo "Finished installing plantuml dependency for the script!!"
        ;;                            
        -h | --help )
        usage;
        exit;
        ;;
    esac
    shift
done

# Set plantuml to java binary if it exists in current dir
if [[ -a plantuml.jar ]]; then
    plantuml="java -jar plantuml.jar"
fi

if [[ ! -d $out_dir ]]; then
    mkdir -p $out_dir
fi
$python py2plantuml.py --from_dir $from_dir --out_dir $out_dir && \
  echo "Transforming puml to svg" && \
    $plantuml -tsvg $out_dir/*.puml && \
      $python -m webbrowser $out_dir/full-diagram-detailed.svg
