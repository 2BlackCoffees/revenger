#!/bin/sh
from_dir=$1
out_dir=$2
plantuml=/opt/homebrew/bin/plantuml
python=python3
if [[ ! -d $2 ]]; then
    mkdir -p $out_dir
fi
$python py2plantuml.py --from_dir $from_dir --out_dir $out_dir && \
  $plantuml -tsvg $out_dir/*.puml && \
    $python -m webbrowser $out_dir/full-diagram-detailed.svg

