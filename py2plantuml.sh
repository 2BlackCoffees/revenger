#!/bin/sh
create_svg_files() {
  plantuml=$1
  out_dir=$2
  rm $out_dir/*.svg
  number_files=$(ls $out_dir/*.puml | wc -l | sed 's:[ \s\t]::g')
  # Much faster with one call
  $plantuml -tsvg $out_dir/*.puml &
  pid_plant_uml=$!
  while [[ $(ps -edf | grep $pid_plant_uml | grep $(basename $plantuml)) ]]; do
    sleep 1
    number_files_processed=$(ls $out_dir/*.svg | wc -l | sed 's:[ \s\t]::g')
    echo "Processed $number_files_processed/$number_files puml files = $((number_files_processed * 100 / number_files))%"
  done
  echo "Done!"
}

from_dir=$1
out_dir=$2
shift
shift
plantuml=/opt/homebrew/bin/plantuml
python=python3
if [[ ! -d $out_dir ]]; then
    mkdir -p $out_dir
fi
echo "Generating puml files"
$python py2plantuml --from_dir $from_dir --out_dir $out_dir $@ && \
  echo "Transforming puml to svg" && \
    create_svg_files $plantuml $out_dir && \
      $python -m webbrowser $out_dir/full-diagram-detailed.svg

