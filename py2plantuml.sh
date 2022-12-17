#!/bin/sh
create_svg_files() {
  plantuml=$1
  out_dir=$2
  rm $out_dir/*.svg
  number_files=$(ls $out_dir/*.puml | wc -l | sed 's:[ \s\t]::g')
  # Much faster with one call
  $plantuml $out_dir/*.puml &
  plain_command_plantuml=$(echo $plantuml | sed "s/^\s*//; s/\s.*$//;")
  pid_plant_uml=$!
  while [[ $(ps -edf | grep $pid_plant_uml | grep $(basename $plain_command_plantuml)) ]]; do
    sleep 1
    number_files_processed=$(ls $out_dir/*.svg | wc -l | sed 's:[ \s\t]::g')
    echo " - Processed $number_files_processed/$number_files puml files = $((number_files_processed * 100 / number_files))%"
  done
  echo "Done!"
}

from_dir=$1
out_dir=$2
python=python3
plantuml=/opt/homebrew/bin/plantuml
svg_dep=secure
var_pip=pip
$var_pip -h >/dev/null 2>&1 || var_pip=pip3
$var_pip -h >/dev/null 2>&1 || error "Could not find pip and pip3, please make sure python3 and pip are installed"

function usage(){
    echo "$(basename $0) [-i | --from_dir ] [ -o | --out_dir] [-d | --dependency_install]  [-p | --plantweb_dep_install] [ --skip_uses_relation ] [ --info ] [ --debug ] [ --trace ] [-h | --help] [--from_language csharp]"
}

function error() {
  echo "ERROR: $1"
  exit 0
}
statements=""
from_language=""
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
            echo "Java is needed for using plantuml dependency...Please install Java and Graphviz first" && exit 1
          fi
          ;;
        -p | --plantweb_dep_install )
          echo "Installing plantweb dependency for rendering SVC....."
          echo "WARNING: Data will be sent to Planweb server, use only for non-sensitive code!!!!!"
          $var_pip install plantweb
          svg_dep=insecure
          echo "Finished installing plantweb dependency for the script!!"
          ;;   
        --from_language )
          shift
          from_language=$1
          echo "Transforming from language $from_language: Currently this requires Docker to be installed"
          docker -v || error "This feature requires docker to be installed. Please make sure it is installed and accessible."
          statements="$statements --yaml"
          ;;
        -h | --help )
          usage;
          exit;
          ;;
        --trace | --info | --debug | --skip_uses_relation)
         statements="$statements $1"
         ;;
        * )
          usage
          error "Parameter $1 is not know."
        ;;
    esac
    shift
done

case $from_language in
  csharp )
    echo "Currently only arn64 image is supported"
    rm $from_dir/*.yaml
    tmp_dir=$from_dir/tmp
    mkdir $tmp_dir || rm -rf $tmp_dir/*
    docker run -v $from_dir:/src -v $tmp_dir:/out 2blackcoffees/py2plantuml_csharpadapter:arm64_latest || error "Docker failed"
    from_dir=$tmp_dir
    ls $from_dir/*.yaml
    ;;
  * )
    error "Language $from_language is currently not supported please make a request if needed (No promise can be made on when it will be ready and if it will be done)"
    ;;
esac

# Set plantuml to java binary if it exists in current dir
if [[ -a plantuml.jar ]]; then
    plantuml="java -jar plantuml.jar"
fi

if [[ ! -d $out_dir ]]; then
    mkdir -p $out_dir
fi
$var_pip install -r py2plantuml/requirements.txt
echo "Generating puml files"

$python py2plantuml --from_dir $from_dir --out_dir $out_dir $(echo $statements) || error "Could not process source files"
echo "Transforming puml to svg"

if [[ "$svg_dep" == "secure" ]]; then
    plantuml -stdlib > /dev/null || error "Plantuml ($plantuml) is not installed or not accessible, please either try to use option -d or switch to the unsecure plantweb with option -p."
    echo "Transforming with plantuml"
    create_svg_files "$plantuml -tsvg -progress" "$out_dir"

else
    wait_time=15
    echo "!!WARNING: Transforming with plantweb: All the generated puml files related to your design are being transferred to the plantuml server,using a local installed (Option -d for example or with an already installed plantuml/graphviz) does not send your files on Internet!!"
    echo "Starting in $wait_time seconds, press ctrl-c to interrupt"
    while [[ $wait_time -ge 1 ]]; do
      echo -n "$wait_time ... ";
      wait_time=$((wait_time - 1));
      sleep 1;
    done
    cd $out_dir && \
      create_svg_files "plantweb --engine=plantuml" "."
fi

$python -m webbrowser $out_dir/full-diagram-detailed.svg
