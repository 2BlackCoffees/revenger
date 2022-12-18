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
    echo -n " - Processed $number_files_processed/$number_files puml files = $((number_files_processed * 100 / number_files))%        "
  done
}
function usage() {
    echo "$(basename $0) [ -i | --from_dir ]   Mandatory: Where the source files are located."
    echo "               [ -o | --out_dir ]    Mandatory: Where to store the puml and svg files"
    echo "               [ --init ]                       Run update on python dependencies (Run it at least the first time)"
    echo "               [ -d | --plantuml_install ]      Install plantuml (not graphviz however, you will have to install it yourself)"
    echo "               [ -p | --plantweb_dep_install ]  Uses plantweb server instead of local plantuml: Insecure DO NOT USE IT for sensitive data."
    echo "               [ --skip_uses_relation ]         Skip UML uses relations"
    echo "               [ --info ]                       Info logs"
    echo "               [ --debug ]                      Debug logs"
    echo "               [ --trace ]                      Trace logs"
    echo "               [ --from_language csharp ]       Currently only python (default) or csharp adapter exist"
    echo "               [ -h | --help ]                  This help"
}
function error() {
  echo "ERROR: $1"
  exit 0
}
function warning() {
  echo "WARNING: $1"
}
function info() {
  echo "INFO: $1"
}
from_dir=$1
out_dir=$2
python=python3

svg_dep=secure
var_pip=pip3
$var_pip -h >/dev/null 2>&1 || var_pip=pip
$var_pip -h >/dev/null 2>&1 || error "Could not find pip and pip3, please make sure python3 and pip are installed (See https://www.python.org/downloads/)."
$var_pip --version | grep python3 >/dev/null 2>&1 || error "$var_pip does not support python3! Install python3 and pip3."

statements=""
from_language=""
while [[ "$1" != "" ]]; do
    case $1 in
        --init )
          $var_pip install -r py2plantuml/requirements.txt
          ;;
        -i | --from_dir | --from-dir | --from )
          from_dir=$2;
          shift;
          ;;
        -o | --out_dir | --out-dir | --to-dir )
          out_dir=$2;
          shift;
          ;;
        -d | --plantuml_install )
          info "Installing plantuml dependency for rendering SVC....."
          if java -version 2>&1 >/dev/null | grep -E "\S+\s+version" ; then
            wget -O plantuml.jar https://github.com/plantuml/plantuml/releases/download/v1.2022.13/plantuml.jar
            info "Finished installing plantuml dependency for the script!!"
            info "Graphviz is needed, please make sure it is present or install it for your OS from https://graphviz.org/download/."
          else
            info "Java is needed for using plantuml dependency...Please install Java and Graphviz first" && exit 1
          fi
          ;;
        -p | --plantweb_dep_install )
          info "Installing plantweb dependency for rendering SVC....."
          warning "WARNING: Data will be sent to Planweb server, use only for non-sensitive code!!!!!"
          $var_pip install plantweb
          svg_dep=insecure
          info "Finished installing plantweb dependency for the script!!"
          ;;   
        --from_language )
          shift
          from_language=$1
          info "Transforming from language $from_language: This requires either dotnet or Docker to be installed: When using dotnet make sure the project is compiled."
          dotnet -h || docker -v || error "This feature requires either dotnet or docker to be installed. Please make sure it is installed and accessible."
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

# Set plantuml to java binary if it exists in current dir
plantuml=plantuml
if [[ $svg_dep == "secure" ]]; then
  $plantuml -h > /dev/null || plantuml=/opt/homebrew/bin/plantuml && info "Using plantuml from $plantuml"
  $plantuml -h > /dev/null|| plantuml="docker run ghcr.io/plantuml/plantuml" && info "Using plantuml from $plantuml"
  $plantuml -h > /dev/null || test -f plantuml.jar && plantuml="java -jar plantuml.jar" && $plantuml -h > /dev/null || echo "plantuml or plantuml docker are not accessible on your system, either install docker or try to install plantuml with brew or with the option --plantuml_install."
fi

case $from_language in
  csharp )
    rm $from_dir/*.yaml
    tmp_dir=$from_dir/tmp
    mkdir $tmp_dir || rm -rf $tmp_dir/*

    dotnet-prj/run.sh $from_dir $tmp_dir || docker run -v $from_dir:/src -v $tmp_dir:/out 2blackcoffees/py2plantuml_csharpadapter:latest || error "Dotnet adapter could not be used both local or from the docker image: Make sure either dotnet is installed and the adapeter is compiled or docker is installed."
    from_dir=$tmp_dir
    ls $from_dir/*.yaml
    ;;
  * )
    error "Language $from_language is currently not supported please make a request if needed (No promise can be made on when it will be ready and if it will be done)"
    ;;
esac



if [[ ! -d $out_dir ]]; then
    mkdir -p $out_dir
fi
info "Generating puml files"
$python py2plantuml --from_dir $from_dir --out_dir $out_dir $(echo $statements) || error "Could not process source files"

info "Transforming puml to svg"
if [[ $svg_dep == "secure" ]]; then
    plantuml -stdlib > /dev/null || error "Plantuml ($plantuml) is not installed or not accessible, please either try to use option -d or switch to the unsecure plantweb with option -p."
    info "Transforming with plantuml ($plantuml)"
    create_svg_files "$plantuml -tsvg -progress" "$out_dir"

else
    wait_time=5
    warning "Transforming with plantweb: All the generated puml files related to your design are being transferred to the plantuml server,using a local installed (Option -d for example or with an already installed plantuml/graphviz) does not send your files on Internet!!"
    info "Starting in $wait_time seconds, press ctrl-c to interrupt if you prefer avoiding sending files on the Internet."
    while [[ $wait_time -ge 1 ]]; do
      info -n "$wait_time ... ";
      wait_time=$((wait_time - 1));
      sleep 1;
    done
    cd $out_dir && \
      create_svg_files "plantweb --engine=plantuml" "."
fi

$python -m webbrowser $out_dir/full-diagram-detailed.svg
