# Revenger
Revenger stands for REVerse ENGineER.

This program transforms source code into a clickable class diagram of the whole application: The supported languages are Python, C# and Java.

The goal of having a clickable class diagram consists in filtering out class of interest together with their direct dependencies and thus increasing tremendously the effort of analyzing and understanding the structure of a program.

Because the tool is started from a command line it can easily be integrated in a CI/CD pipline thus allowing to have a class diagram constantly up to date.

The program is based on the hexagonal pattern where languages are adapters. 
At the moment adapters exist only for Python, Java and C#.

See here for a quick introduction what this tool is used for and how to use it (Outdated presentation): https://www.youtube.com/watch?v=u4VpfKfgr7Q 

Please note that not all features of the languages ae supported. This program is mostly designed to help:

1. Approaching unkown source code much faster thus reducing the effort for refactoring.
2. Creating a very low level documentation allowing developers to increase their coordination.

## Dependencies
* You will need to have either plantuml installed or at least Docker.
  * One option of the script allows to install plantuml partially or use a PlantUML Web server.
* If you need to reverse engineer C#, the script will try to use a locally accessible dotnet program. 
  * If no dotnet can be found a Docker image can be used to run the adapter: The script will take care to try it. 
* If Docker and dotnet are both not installed, the csharp reverse engineering will not be running. 
* To reverse engineer Java you will need to have maven and at least Java 8 properly installed.
  * Remember to set properly the JAVA_HOME
  * This is an example: 
  
       ```export JAVA_HOME=$(/usr/libexec/java_home)```

## Usage
```
/revenger.sh -h
revenger.sh options:
               [ -i | --from_dir ]   Mandatory except when process_svg_only is set: Defines where the source files are located.
               [ -o | --out_dir ]    Mandatory: Where to store the puml and svg files
               [ --init ]                       Run update on python dependencies (Run it at least the first time)
               [ -d | --plantuml_install ]      Install plantuml (not graphviz however, you will have to install it yourself)
               [ -p | --plantweb_dep_install ]  Uses plantweb server instead of local plantuml: Insecure DO NOT USE IT for sensitive data.
               [ --skip_uses_relation ]         Skip UML uses relations
               [ --skip_not_defined_classes ]   If a class is referenced but not defined, it will not be displayed (reduces memory needs)
               [ --info ]                       Info logs
               [ --debug ]                      Debug logs
               [ --trace ]                      Trace logs
               [ --from_language lang_type ]    lang_type can be csharp, java or python.
               [ --force_docker_adapter ]       If the adapter has a docker image use it as prio 1
               [ --force_docker_plantuml ]      The script will prefer a local installed plantuml, force usage of docker image instead
               [ --timeout ]                    Defines the timeout in seconds when generating svg files (Default is 900 seconds)
               [ --process_svg_only ]           Skip puml generation and process (or continue processing svg generation)
  PlantUML specific options for the local plantuml script:
               [ --plantuml.java_heap_max_size ]    Defines the max size for the Java heap for plantuml/dotgraphviz ONLY if using the local script
               [ --plantuml.graphvizdotpath ]       Defines the path to the application graphvizdot
               [ --plantuml.plantumljarpath ]       Defines the path to plantuml jar file
               [ --plantuml.javapath ]              Defines the path to java binary command
  Misc options:
               [ --only_full_diagrams ]             Generate only full diagrams (for debug purpose)
               [ --start_with_biggest_sizes ]       Processes by default smallest PUML files size first, with this option, start with biggest PUML files size
               [ -h | --help ]                      This help
```

Revenger can be easily tested reverse engineering its own code. Once you cloned this repository, you can reverse engineer different parts of the tool. Assuming your are in the directory where the script `./revenger.sh` is located:

* Python code can be reversed engineered as follows (please not that the Python adapter is being refactored because of some wrongly generated inconsistencies):

    `./revenger.sh --from_dir revenger --out_dir out-revenger-python-uses`

* CSharp code can be reversed engineered as follows:

    `./revenger.sh --from_dir dotnet-adapter/DotnetPreAdapter --out_dir out-revenger-csharp-uses  --from_language csharp`

* Java code can be reversed engineered as follows:

    `./revenger.sh --from_dir java-adapter/ --out_dir out-revenger-java-uses  --from_language java`

# TODOs

Currently the Python adapter requires:
1. All user defined modules to be imported one per line
2. When importing a user module, the whole module path must be specified from the entry point
3. All declarations and method parameters must be properly annotated with their type

## Architecture
See below a high level architecture of the application:
![High level Architecture](./revenger-architecture.png?raw=true "Architecture of Revenger")
## Design improvement needed
The application was created to be quickly usable. The Python adapeter needs to be refactored as follows:
  * On going: Python Adapter needs to be improved (See https://docs.python.org/3/library/ast.html for more details)
  * The application should be able to extract their type from the instantiated type (and not necessarily the annotation)
  * The whole module path should not be absolutely mandatory
  * More than one user defined types shoud be usable
  

## What features are missing
  We have a Trello Board here: https://trello.com/b/ExI3XPoO/candycat-py2plantuml.


