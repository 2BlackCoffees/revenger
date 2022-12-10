#!/bin/sh
from_dir=$1
out_dir=$2
shift
shift
plantuml=/opt/homebrew/bin/plantuml
python=python3
if [[ ! -d $out_dir ]]; then
    mkdir -p $out_dir
fi
$python py2plantuml --from_dir $from_dir --out_dir $out_dir $@ && \
  echo "Transforming puml to svg" && \
    $plantuml -tsvg $out_dir/*.puml && \
      $python -m webbrowser $out_dir/full-diagram-detailed.svg

