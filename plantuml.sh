#!/bin/bash
if [[ "$*" != *"-gui"* ]]; then
  VMARGS="-Djava.awt.headless=true  -Xmx8G"
fi
GRAPHVIZ_DOT="/opt/homebrew/opt/graphviz/bin/dot" exec "/opt/homebrew/opt/openjdk/bin/java" $VMARGS -jar /opt/homebrew/Cellar/plantuml/1.2022.13/libexec/plantuml.jar "$@"
