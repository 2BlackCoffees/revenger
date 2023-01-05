#!/bin/bash
create_svg_files() {
  plantuml=$1
  out_dir=$2

  find $out_dir -type f -name '*.svg' | xargs rm -f  > /dev/null

  number_files=$(find $out_dir -type f -name '*.puml' 2>/dev/null | wc -l  | sed 's:[ \s\t]::g')
  # Much faster with one call
  pushd $out_dir >/dev/null 
  files=*.puml
  # echo "$plantuml $files"
  bash -c "$plantuml $files" &
  pid_plant_uml=$!
  plain_command_plantuml=plantuml
  echo $plantuml | grep plantuml > /dev/null 2>&1 || plain_command_plantuml=plantweb
  while [[ $(ps -edf | grep $pid_plant_uml | grep $plain_command_plantuml) ]]; do
    sleep 1
    number_files_processed=$(find $out_dir -type f -name '*.svg' 2>/dev/null | wc -l | sed 's:[ \s\t]::g')
    echo " - Processed $number_files_processed/$number_files puml files = $((number_files_processed * 100 / number_files))%        "
  done
  popd >/dev/null 
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
from_language=python
svg_dep=secure
var_pip=pip3
tmp_dir=
$var_pip -h >/dev/null 2>&1 || var_pip=pip
$var_pip -h >/dev/null 2>&1 || error "Could not find pip and pip3, please make sure python3 and pip are installed (See https://www.python.org/downloads/)."
$var_pip --version | grep python3 >/dev/null 2>&1 || error "$var_pip does not support python3! Install python3 and pip3."

statements=""
keep_tmp_files=0
while [[ "$1" != "" ]]; do
    case $1 in
        --init )
          $var_pip install -r py2plantuml/requirements.txt
          ;;
        -i | --from_dir | --from-dir | --from )
          tmp_from=$2
          if [[ ! -d $tmp_from ]]; then
            error "Source directory $tmp_from does not exist!"
          fi
          from_dir=$(readlink -f $tmp_from);
          shift;
          ;;
        -o | --out_dir | --out-dir | --to-dir )
          tmp_out=$2
          if [[ ! -d $tmp_out ]]; then
            info "Creating dorectory output non existing directory $tmp_out"
            mkdir -p $tmp_out
          fi
          out_dir=$(readlink -f $tmp_out);
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
          dotnet -h > /dev/null 2>&1 || docker -v > /dev/null 2>&1 || error "This feature requires either dotnet or docker to be installed. Please make sure it is installed and accessible."
          statements="$statements --yaml"
          ;;
        -h | --help )
          usage;
          exit;
          ;;
        --trace | --info | --debug | --skip_uses_relation)
         statements="$statements $1"
         ;;
        --keep )
          keep_tmp_files=1
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
  $plantuml -h > /dev/null 2>&1 
  if [[ $? != 0 ]];then 
      echo "INFO: $plantuml not found searching for an alternative."
      plantuml=/opt/homebrew/bin/plantuml
      $plantuml -h > /dev/null 2>&1 
      if [[ $? != 0 ]];then 
          echo "INFO: $plantuml not found searching for an alternative."
          plantuml="docker run -v $out_dir:/data ghcr.io/plantuml/plantuml"
          bash -c $plantuml -h > /dev/null 2>&1 
          if [[ $? != 0 ]]; then
              echo "INFO: $plantuml not found searching for an alternative."
              if [[ -f plantuml.jar ]];then 
                plantuml="java -jar plantuml.jar"
                bash -c $plantuml -h > /dev/null 2>&1 || error "plantuml or plantuml docker are not accessible on your system, either install docker or try to install plantuml with brew or with the option --plantuml_install."
              else
                error "plantuml or plantuml docker are not accessible on your system, either install docker or try to install plantuml with brew or with the option --plantuml_install."
              fi
          fi
      fi
  fi
fi

info "Using plantuml from $plantuml"
info "Using adapter from language $from_language"
if [[ $keep_tmp_files == 0 ]]; then
  info "Cleaning output directory"
  find $out_dir -type f | xargs rm -f  > /dev/null
fi

case $from_language in
  csharp )
    if [[ $keep_tmp_files == 0 ]]; then
      rm $out_dir/*.yaml > /dev/null 2>&1
    fi
    tmp_dir=$(mktemp -d)
    basepath=$( dirname -- "$( readlink -f -- "$0" )" )
    pushd $basepath/dotnet-prj >/dev/null 2>&1
    info "Running CSharp adapter"
    ./run.sh $from_dir $tmp_dir $(echo $statements) || docker run -v $from_dir:/src -v $tmp_dir:/out 2blackcoffees/py2plantuml_csharpadapter:latest $(echo $statements) >/dev/null 2>&1 || error "Dotnet adapter could not be used both local or from the docker image: Make sure either dotnet is installed and the adapeter is compiled or docker is installed."
    popd >/dev/null 2>&1
    from_dir=$tmp_dir
    cp -r $tmp_dir/* $out_dir

    ;;
  python )
    ;;
  * )
    error "Language $from_language is currently not supported please make a request if needed (No promise can be made on when it will be ready and if it will be done)"
    ;;
esac


info "Generating puml files"
$python py2plantuml --from_dir $from_dir --out_dir $out_dir $(echo $statements) || error "Could not process source files"

info "Transforming puml to svg"
if [[ $svg_dep == "secure" ]]; then
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
if [[ ! -z $tmp_dir ]]; then
  if [[ $keep_tmp_files == 0 ]]; then
    rm -rf $tmp_dir
  else
    echo "DEBUG: Kept tmp_dir: $tmp_dir"
  fi
fi
$python -m webbrowser $out_dir/full-diagram-detailed.svg
