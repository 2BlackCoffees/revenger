#!/bin/sh
from_dir=$1
out_dir=$2
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
        echo "Installing plantweb dependency for rendering SVC....."
        pip3 install plantweb
        echo "Finished installing plantweb dependency for the script!!"
        ;;                            
        -h | --help )
        usage;
        exit;
        ;;
    esac
    shift
done


if [[ ! -d $out_dir ]]; then
    mkdir -p $out_dir
fi
$python py2plantuml.py --from_dir $from_dir --out_dir $out_dir && \
  echo "Transforming puml to svg" && \
    cd $out_dir && \
    plantweb --engine=plantuml ./*.puml && \
    echo "Open $out_dir/full-diagram-detailed.svg in your browser..."
      $python -m webbrowser $out_dir/full-diagram-detailed.svg
