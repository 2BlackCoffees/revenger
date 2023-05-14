#!/bin/bash
export REVENGER_LOCAL_PID=$$
# \rm -rf tmp-dotnet && mkdir tmp-dotnet && ./revenger.sh --from_dir dotnet-adapter/DotnetPreAdapter --out_dir tmp-dotnet --trace --from_language csharp --keep > out-csharp.log 2>&1
# \rm -rf tmp-java && mkdir tmp-java && ./revenger.sh --from_dir java-adapter/src/main/java/Example --out_dir tmp-java --trace --from_language java --keep > tmp/out-java.log 2>&1
function kill_script() {
      kill -9 $REVENGER_LOCAL_PID

}

function error() {
  echo -e "ERROR: $1"
  kill_script

  exit 1
}
function warning() {
  echo -e "WARNING: $1"
}
function info() {
  echo -e "INFO: $1"
}

function info_overwrite_line() {
  echo -ne "INFO: $1                  \033[0K\r"
}

list_file_to_parameters() {
  plant_uml=$1
  number_files=$2
  list_remaining_puml=$3

  file_type=".puml"
  export number_parameters_max=1500
  export number_groups=$(( number_files / number_parameters_max + 1 ))
  number_groups_int=$(printf "%.0f\n" $number_groups)
  if [[ $number_groups_int -gt $number_groups ]]; then
    number_groups=$number_groups_int
  fi
  command_file=$(mktemp)
  list_remaining_puml_tmp=$(mktemp)
  echo "function uml_to_svg_runner() {" >> $command_file
  group_nb=1
  while [[ $(wc -c $list_remaining_puml | awk '{print $1}' | xargs) -gt 1 ]]; do
    echo "# COMMENT: Preparing group $group_nb out of $number_groups (Total files: $(wc -l $list_remaining_puml) )" >> $command_file
    file_list=$(head -$number_parameters_max $list_remaining_puml  | xargs)
    tail -n +$((number_parameters_max + 1))  $list_remaining_puml > $list_remaining_puml_tmp
    cp $list_remaining_puml_tmp $list_remaining_puml
    echo "  echo \"INFO: Starting transforming from PUML to SVG the group $group_nb/$number_groups of $number_parameters_max files (Running in $command_file, PID: \$\$)\"" >> $command_file
    group_nb=$((group_nb + 1))
    echo "  $plantuml $file_list" >> $command_file
  done
  rm "$list_remaining_puml"
  echo "}" >> $command_file
  echo "uml_to_svg_runner" >> $command_file
  chmod 755 $command_file
  if [[ $group_nb -gt 1 ]]; then
    echo $command_file
  else
      error "No missing PUML files found to be processed."
  fi

}

get_list_puml_not_processed() {
  keep_old_svg_and_tmp_files=$1
  process_missing_puml_only=$2
  start_with_biggest_sizes=$3
  list_remaining_puml_init=$(mktemp)
  deadletter=DeadLetter
  if [[ $process_svg_only == 1 || $keep_old_svg_and_tmp_files == 1 ]]; then
    test -d $deadletter || mkdir $deadletter
    find . -name "*.svg" -size 0 -type f | perl -npe 's:svg$:puml:' | xargs -I '{}' mv {} $deadletter >/dev/null 2>&1
    find . -name "*.svg" -size 0 -type f | perl -npe 's:svg$:puml:' | xargs rm >/dev/null 2>&1
    find . -name "*.svg" -size 0 -type f | xargs rm 
    list_all_puml=$(mktemp)
    list_puml_done=$(mktemp)
    find . -type f -name "*.puml" | grep -v $deadletter | perl -npe 's:([\[\]]):\\\\$1:g;s:([<> ]):\\\\$1:g;' | sort > $list_all_puml 2>/dev/null
    find . -type f -name "*.svg" | grep -v $deadletter | sed 's:\.svg:\.puml:' | sort > $list_puml_done 2>/dev/null
    diff $list_puml_done $list_all_puml | grep '>' | sed 's:^[\> ]*::g' > $list_remaining_puml_init
    if [[ $keep_old_svg_and_tmp_files == 0 ]]; then
      rm $list_puml_done $list_all_puml
    else
      info "Keeping list_puml_done = $list_puml_done" >> dbg_info
      info "Keeping list_all_puml = $list_all_puml" >> dbg_info
    fi
  else
    find . -type f -name '*.svg' | xargs rm -f  > /dev/null
    find . -type f -name "*.puml" | grep -v $deadletter > $list_remaining_puml_init 2>/dev/null
  fi
  list_remaining_puml_sorted=$(mktemp)
  sort_option=nk1
  if [[ $start_with_biggest_sizes -eq 1 ]]; then
    sort_option="r${sort_option}"
  fi
  cat $list_remaining_puml_init | xargs ls -l | awk '{print $5 " " $9}' | sort -${sort_option} | awk '{print $2}' > $list_remaining_puml_sorted

  if [[ $keep_old_svg_and_tmp_files == 1 ]]; then
    rm $list_remaining_puml_init
  else
    info "Keeping list_remaining_puml_init = $list_remaining_puml_init"  >> dbg_info
  fi
  echo $list_remaining_puml_sorted
}

create_svg_files() {
  plantuml=$1
  out_dir=$2
  keep_old_svg_and_tmp_files=$3
  start_with_biggest_sizes=$4
  process_missing_puml_only=$5
  info "Analyzing list of files to be processed"
  pushd $out_dir >/dev/null 
  list_remaining_puml=$(get_list_puml_not_processed $keep_old_svg_and_tmp_files $process_missing_puml_only $start_with_biggest_sizes)
  total_size_puml=$(cat $list_remaining_puml | xargs ls -l | awk '{sum+=$5;} END {print sum;}')

  number_files=$(wc -l $list_remaining_puml | perl -npe 's:^\s*::;s:\s+.*$::')
  info "Number files: $number_files, Total size: $((total_size_puml / 1024/1024)) MB"
  command_file=$(list_file_to_parameters "$plantuml" "$number_files" "$list_remaining_puml")
  grep COMMENT $command_file | perl -npe 's:\s*# COMMENT:INFO:'

  bash $command_file &

  pid_plant_uml=$!

  export previous_svg_list=previous_svg_list
  export latest_svg_list=latest_svg_list
  find . -name '*.svg' > $previous_svg_list
  number_seconds_since_last_processed_files=$(date +%s)
  started_time=$(date +%s)
  last_diff_epoch=$(date +%s)
  number_files_previously_processed=$(find . -type f -name '*.svg' 2>/dev/null | wc -l | sed 's:[ \s\t]::g')
  if [[ -z $number_files_previously_processed ]]; then
    number_files_previously_processed=0
  fi

  processed_size_puml=0
  last_processed_files_date_time=$(date '+%d/%m/%Y %H:%M:%S')
  need_carriage_return=0

  while [[ $(ps -edf | grep $pid_plant_uml | grep $command_file) ]]; do
    unix_epoch=$(date +%s)
    if [[ $((unix_epoch - last_printed_waiting_message_time)) -gt 10 ]]; then
      export latest_file_name_svg=$(ls -t | grep '\.svg'| head -1 | sed 's:svg$:puml:')
      latest_file_puml=""
      if [[ -n $latest_file_name_svg ]]; then
        latest_file_puml=$(ls -l  $latest_file_name_svg | awk '{print $9" (" $5/1024/1024" MB)"}')
      fi
      now_date_time=$(date '+%d/%m/%Y %H:%M:%S')
      info_overwrite_line "   -  ($now_date_time) Still processing $latest_file_puml since $((unix_epoch - number_seconds_since_last_processed_files)) seconds (Started $last_processed_files_date_time) - Processed $number_files_processed/$number_files puml files = $((number_files_processed * 100 / number_files))%  (PID: $pid_plant_uml)   "
      last_printed_waiting_message_time=$unix_epoch
      need_carriage_return=1

    fi
    sleep 1
    number_files_processed=$(find . -type f -name '*.svg' 2>/dev/null | wc -l | sed 's:[ \s\t]::g')
    if [[ -z $number_files_processed ]]; then
      number_files_processed=0
    fi
    number_files_processed=$(( number_files_processed - number_files_previously_processed ))
    find . -name '*.svg' > $latest_svg_list
    if [[ $(diff $previous_svg_list $latest_svg_list) ]]; then
      latest_processed_files=$(diff $previous_svg_list $latest_svg_list | grep "> " | sed 's/^/      /g')
      echo ""
      info "    Latest processed files:\n$latest_processed_files"
      cp $latest_svg_list $previous_svg_list
      number_seconds_since_last_processed_files=$(date +%s)
      last_processed_files_date_time=$(date '+%d/%m/%Y %H:%M:%S')
      last_printed_waiting_message_time=$unix_epoch
      processed_size_puml=0
      if [[ -e $latest_svg_list ]]; then 
        processed_size_puml=$(cat $latest_svg_list | sed 's:\.svg:\.puml:' | xargs ls -l 2>/dev/null | awk '{sum+=$5;} END {print sum;}')
      fi

      time_spent=$((number_seconds_since_last_processed_files - started_time))
      if [[ $need_carriage_return == 1 ]]; then echo ""; fi
      info " - Processed $number_files_processed/$number_files puml files = $(( number_files_processed * 100 / number_files ))% ($((processed_size_puml / 1024 / 1024 ))/$((total_size_puml / 1024 / 1024)) MB processed = $(( processed_size_puml * 100 / total_size_puml ))% )"

    fi
    # if [[ $number_files_processed == $number_files ]]; then
    #   break
    # fi
  done
  popd >/dev/null 
  if [[ $keep_old_svg_and_tmp_files == 0 ]]; then
    rm $command_file
  else
    info "Kept command file $command_file"
  fi

}
function usage() {
    echo "$(basename $0) options:"
    echo "               [ -i | --from_dir ]   Mandatory except when process_svg_only is set: Defines where the source files are located."
    echo "               [ -o | --out_dir ]    Mandatory: Where to store the puml and svg files"
    echo "               [ --init ]                       Run update on python dependencies (Run it at least the first time)"
    echo "               [ -d | --plantuml_install ]      Install plantuml (not graphviz however, you will have to install it yourself)"
    echo "               [ -p | --plantweb_dep_install ]  Uses plantweb server instead of local plantuml: Insecure DO NOT USE IT for sensitive data."
    echo "               [ --skip_uses_relation ]         Skip UML uses relations"
    echo "               [ --skip_not_defined_classes ]   If a class is referenced but not defined, it will not be displayed (reduces memory needs)"
    echo "               [ --info ]                       Info logs"
    echo "               [ --debug ]                      Debug logs"
    echo "               [ --trace ]                      Trace logs"
    echo "               [ --from_language lang_type ]    lang_type can be csharp, java, yaml or python. "
    echo "               [ --force_docker_adapter ]       If the adapter has a docker image use it as prio 1"
    echo "               [ --force_docker_plantuml ]      The script will prefer a local installed plantuml, force usage of docker image instead"
    echo "               [ --timeout ]                    Defines the timeout in seconds when generating svg files (Default is 900 seconds)"
    echo "               [ --process_svg_only ]           Skip puml generation and process (or continue processing svg generation)"
    echo "               [ --summary_page_only ]          Generate a summary page (This option will short circuit the analysis processing)"
    echo "               [ --force_python ]               Force a specific version of python"
    echo "               [ --force_pip ]                  Force a specific version of pip"

    echo "  PlantUML specific options for the local plantuml script:"
    echo "               [ --plantuml.java_heap_max_size ]    Defines the max size for the Java heap for plantuml/dotgraphviz ONLY if using the local script"
    echo "               [ --plantuml.graphvizdotpath ]       Defines the path to the application graphvizdot"
    echo "               [ --plantuml.plantumljarpath ]       Defines the path to plantuml jar file"
    echo "               [ --plantuml.javapath ]              Defines the path to java binary command"
    echo "  Misc options:"
    echo "               [ --no_full_diagrams ]               Generates no full diagrams (these digrams can be huge)"
    echo "               [ --profiler_output ]                Enable the python profiler: specify the filename for the output"
    echo "               [ --start_with_biggest_sizes ]       Processes by default smallest PUML files size first, with this option, start with biggest PUML files size"
    echo "               [ -h | --help ]                      This help"
}

function run_dotnet_java_locally() {
  language=$1
  from_dir=$2
  tmp_dir=$3
  shift
  shift
  shift
  statements=$@
  pushd $basepath/${language}-adapter >/dev/null 2>&1
  info "Running ./run.sh $from_dir $tmp_dir $(echo $statements)"
  ./run.sh $from_dir $tmp_dir $(echo $statements) || info "Running $(pwd)/run.sh $from_dir $tmp_dir $(echo $statements) failed"
  status=$?
  popd >/dev/null 2>&1
  return $status
}
function run_dotnet_in_docker() {
  from_dir=$1
  tmp_dir=$2
  shift
  shift
  statements=$@
  docker run -v $from_dir:/src -v $tmp_dir:/out \
    2blackcoffees/revenger_csharpadapter:latest --from_dir /src --out_dir /out \
    $(echo $statements) 
  return $?
}
from_dir=$1
out_dir=$2
python=python3
from_language=python
svg_dep=secure
var_pip=pip3
tmp_dir=
force_docker_adapter=0
force_docker_plantuml=0
process_svg_only=0
summary_page_only=0
force_init=0
statements=""
keep_old_svg_and_tmp_files=0
PLANTUML_DOT_JAVA_HEAP_MAX_SIZE=16G
plantuml_timeout=900
start_with_biggest_sizes=0
while [[ "$1" != "" ]]; do
    case $1 in
        --force_python )
          python=$2
          shift;
          ;;
        --force_pip )
          var_pip=$2
          shift;
          ;;
        --init )
          force_init=1
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
        --process_svg_only)
          process_svg_only=1
          ;;
        --summary_page_only)
          summary_page_only=1
          ;;
        --force_docker_adapter)
          force_docker_adapter=1
          ;;
        --force_docker_plantuml)
          force_docker_plantuml=1
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
          info "Transforming from language $from_language: This requires either dotnet for C# or Docker to be installed: When using dotnet make sure the project is compiled."
          dotnet -h > /dev/null 2>&1 || docker -v > /dev/null 2>&1 || error "This feature requires either dotnet or docker to be installed. Please make sure it is installed and accessible."
          statements="$statements --yaml"
          ;;
        -h | --help )
          usage;
          exit;
          ;;
        --plantuml.java_heap_max_size )
          PLANTUML_DOT_JAVA_HEAP_MAX_SIZE=$2
          shift
          ;;
        --timeout )
          plantuml_timeout=$2
          shift
          ;;
        --plantuml.graphvizdotpath )
          PLANTUML_GRAPHVIZ_DOT_PATH=$2
          shift
          ;;
        --plantuml.plantumljarpath )
          PLANTUML_JAR_PATH=$2
          shift
          ;;
        --plantuml.javapath ) 
          PLANTUML_JAVAPATH=$2
          shift
          ;;
        --profiler_output )
         statements="$statements $1 $2"
         shift
         ;;
        --trace | --info | --debug | --skip_uses_relation | --skip_not_defined_classes | --no_full_diagrams )
         statements="$statements $1"
         ;;
        --keep )
          keep_old_svg_and_tmp_files=1
          ;;
        --start_with_biggest_sizes )
          start_with_biggest_sizes=1
          ;;
        * )
          usage
          error "Parameter $1 is not know."
        ;;
    esac
    shift
done

$var_pip -h >/dev/null 2>&1 || var_pip=pip
$var_pip -h >/dev/null 2>&1 || error "Could not find $var_pip, please make sure $python and $var_pip are installed (See https://www.python.org/downloads/)."
$var_pip --version | grep $python >/dev/null 2>&1 || error "$var_pip does not support $python! Install $python and $pip."

if [[ $force_init == 1 ]]; then
  info "Installing python librairies: $var_pip install -r revenger/requirements.txt"
  $var_pip install -r revenger/requirements.txt
fi
basepath=$( dirname -- "$( readlink -f -- "$0" )" )

if [[ $summary_page_only == 0 ]]; then
  # Set plantuml to java binary if it exists in current dir
  if [[ $force_docker_plantuml == 0 ]]; then  
    plantuml=$basepath/plantuml.sh
  else
    plantuml="docker run -v $out_dir:/data ghcr.io/plantuml/plantuml"
  fi
  if [[ $svg_dep == "secure" ]]; then
      info "Checking accessibility of $plantuml" 
      $plantuml -h > /dev/null 2>&1 
      if [[ $? != 0 ]];then 
          info "$plantuml not found trying plantuml."
          plantuml=plantuml
          $plantuml -h > /dev/null 2>&1 
          if [[ $? != 0 ]];then 
              info "$plantuml not found trying /opt/homebrew/bin/plantuml."
              plantuml=/opt/homebrew/bin/plantuml
              $plantuml -h > /dev/null 2>&1 
              if [[ $? != 0 ]];then 
                  info "$plantuml not found searching for an alternative."
                  if [[ $force_docker_plantuml == 0 ]]; then  
                    plantuml="docker run -v $out_dir:/data ghcr.io/plantuml/plantuml"
                  else
                    plantuml=plantuml
                  fi
                  bash -c $plantuml -h > /dev/null 2>&1 
                  if [[ $? != 0 ]]; then
                      info "$plantuml not found searching trying with the jar file."
                      if [[ -f plantuml.jar ]];then 
                        plantuml="java -Djava.awt.headless=true  -Xmx8G -jar plantuml.jar"
                        bash -c $plantuml -h > /dev/null 2>&1 || error "None of the possible local plantuml or plantuml docker are not accessible on your system, either install docker or try to install plantuml with brew or with the option --plantuml_install."
                      else
                        error "Local installed plantuml or plantuml docker are not accessible on your system, either install docker or try to install plantuml with brew or with the option --plantuml_install."
                      fi
                  fi
              fi
          fi
      fi
  fi
  info "Using plantuml from $plantuml"
fi
if [[ $process_svg_only == 0 && $summary_page_only == 0 ]]; then
  info "Using adapter from language $from_language"
  if [[ $keep_old_svg_and_tmp_files == 0 ]]; then
    info "Cleaning output directory"
    find $out_dir -type f | xargs rm -f  > /dev/null
  fi
  case $from_language in
    csharp )
      if [[ $keep_old_svg_and_tmp_files == 0 ]]; then
        rm $out_dir/*.yaml > /dev/null 2>&1
      fi
      tmp_dir=$(mktemp -d)
      if [[ $force_docker_adapter == 0 ]]; then
        info "Running CSharp adapter locally or as docker image"
        run_dotnet_java_locally dotnet $from_dir $tmp_dir $statements|| run_dotnet_in_docker $from_dir $tmp_dir $statements || error "Dotnet adapter could not be used both local or from the docker image: Make sure either dotnet is installed and the adapter is compiled or docker is installed."
      else
        info "Running CSharp adapter as Docker image"
        run_dotnet_in_docker $from_dir $tmp_dir $statements || error "Dotnet adapter could not be used from the docker image: Make sure docker is installed or try to run dotnet locally."
      fi
      from_dir=$tmp_dir
      cp -r $tmp_dir/* $out_dir || error "no files could be found in the temporary directory $tmp_dir"

      ;;
    java )
       if [[ $keep_old_svg_and_tmp_files == 0 ]]; then
         rm $out_dir/*.yaml > /dev/null 2>&1
       fi
       tmp_dir=$(mktemp -d)
       if [[ $force_docker_adapter == 0 ]]; then
         info "Running Java adapter locally or as docker image"
         run_dotnet_java_locally java $from_dir $tmp_dir $statements || run_dotnet_in_docker $from_dir $tmp_dir $statements || error "Java adapter could not be used both local or from the docker image: Make sure either maven is installed or docker is installed."
       else
         info "Running Java adapter as Docker image"
         #run_dotnet_in_docker $from_dir $tmp_dir $statements || error "Dotnet adapter could not be used from the docker image: Make sure docker is installed or try to run dotnet locally."
       fi
       from_dir=$tmp_dir
       cp -r $tmp_dir/* $out_dir || error "no files could be found in the temporary directory $tmp_dir"

      ;;
    python )
      ;;
    yaml )
      ;;
    * )
      error "Language $from_language is currently not supported please make a request if needed (No promise can be made on when it will be ready and if it will be done)"
      ;;
  esac


  info "Generating puml files"
  info "$python revenger --from_dir $from_dir --out_dir $out_dir $(echo $statements)"
  $python revenger --from_dir $from_dir --out_dir $out_dir $(echo $statements) || error "Could not process source files"
fi

if [[ $summary_page_only == 0 ]]; then
  info "Transforming puml to svg"
  if [[ $svg_dep == "secure" ]]; then
      info "Transforming with plantuml ($plantuml)"
      create_svg_files "$plantuml -timeout $plantuml_timeout -tsvg -enablestats -realtimestats -htmlstats " "$out_dir" "$keep_old_svg_and_tmp_files" "$start_with_biggest_sizes" "$process_svg_only"

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
        create_svg_files "plantweb --engine=plantuml" "." "$keep_old_svg_and_tmp_files" "$start_with_biggest_sizes"
  fi
fi

info "$python revenger --from_dir $out_dir --out_dir $out_dir --summary_page_only $(echo $statements)"
$python revenger --from_dir $out_dir --out_dir $out_dir --summary_page_only $(echo $statements) || error "Could not process source files"

if [[ ! -z $tmp_dir ]]; then
  if [[ $keep_old_svg_and_tmp_files == 0 ]]; then
    rm -rf $tmp_dir
  else
    info "Kept tmp_dir: $tmp_dir and $command_file"
  fi
fi
$python -m webbrowser $out_dir/index.html
