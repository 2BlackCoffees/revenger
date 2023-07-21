#!/bin/bash

java_heap_size=${PLANTUML_DOT_JAVA_HEAP_MAX_SIZE:-60G}

if [[ "$*" != *"-gui"* ]]; then
    VMARGS="-Djava.awt.headless=true  -Xmx${java_heap_size}"
fi
export GRAPHVIZ_DOT=${PLANTUML_GRAPHVIZ_DOT_PATH:-"/opt/homebrew/opt/graphviz/bin/dot"}
plant_uml_jar_path=${PLANTUML_JAR_PATH:-"/opt/homebrew/Cellar/plantuml/1.2023.0/libexec/plantuml.jar"}
java_path=${PLANTUML_JAVAPATH:-"/opt/homebrew/opt/openjdk/bin/java"}
exec $java_path $VMARGS -jar $plant_uml_jar_path "$@"
