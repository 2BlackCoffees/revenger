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
python=python3
plantuml=/opt/homebrew/bin/plantuml
svg_dep=secure
function usage(){
    echo "$(basename $0) [-i | --from_dir ] [ -o | --out_dir] [-d | --dependency_install]  [-p | --plantweb_dep_install] [ --skip_uses_relation ] [ --info ] [ --debug ] [ --trace ] [-h | --help]"
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
        echo "Installing plantuml dependency for rendering SVC....."
        if java -version 2>&1 >/dev/null | grep -E "\S+\s+version" ; then
          wget -O plantuml.jar https://github.com/plantuml/plantuml/releases/download/v1.2022.13/plantuml.jar
          echo "Finished installing plantuml dependency for the script!!"
        else
          echo "Java is needed for using plantuml dependency...Please install Java first" && exit 1
        fi
        ;;
        -p | --plantweb_dep_install )
        echo "Installing plantweb dependency for rendering SVC....."
        echo "WARNING: Data will be sent to Planweb server, use only for non-sensitive code!!!!!"
        pip3 install plantweb
        svg_dep=insecure
        echo "Finished installing plantweb dependency for the script!!"
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

echo "Generating puml files"

$python py2plantuml --from_dir $from_dir --out_dir $out_dir $@ && \
  echo "Transforming puml to svg"


if [[ "$svg_dep" == "secure" ]]; then
    echo "Transforming with plantuml"
    create_svg_files "$plantuml" "$out_dir"

else
    echo "!!Transforming with plantweb!!"
    cd $out_dir && \
      plantweb --engine=plantuml ./*.puml && \
        echo "Open $out_dir/full-diagram-detailed.svg in your browser..."
fi

$python -m webbrowser $out_dir/full-diagram-detailed.svg
