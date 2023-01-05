# Revenger
Revenger stands for REVerse ENGineER.

This program transforms either a python or a C# program into a clickable class diagram of the whole application.
Classes can be filtered in just clicking on them to analyze and understand how the program is structured.

The program is based on the hexagonal pattern where languages are adapters. 
At the moment adapters exist only for Python and C#.

See here for a quick introduction what this tool is used for and how to use it (Outdated presentation): https://www.youtube.com/watch?v=u4VpfKfgr7Q 


## Dependencies
* You will need to have either plantuml installed or at least Docker.
  * One option of the script allows to install plantuml partially or use a PlantUML Web server.
* If you need to reverse engineer C#, the script will try to use a locally accessible dotnet program. 
  * If no dotnet can be found a Docker image can be used to run the adapter: The script will take care to try it. 
* If Docker and dotnet are both not installed, the csharp reverse engineering will not be running. 

## Usage
```
./revenger.sh -h

revenger.sh [ -i | --from_dir ]   Mandatory: Where the source files are located.
               [ -o | --out_dir ]    Mandatory: Where to store the puml and svg files
               [ --init ]                       Run update on python dependencies (Run it at least the first time)
               [ -d | --plantuml_install ]      Install plantuml (not graphviz however, you will have to install it yourself)
               [ -p | --plantweb_dep_install ]  Uses plantweb server instead of local plantuml: Insecure DO NOT USE IT for sensitive data.
               [ --skip_uses_relation ]         Skip UML uses relations
               [ --info ]                       Info logs
               [ --debug ]                      Debug logs
               [ --trace ]                      Trace logs
               [ --from_language csharp ]       Currently only python (default) or csharp adapter exist
               [ --force_docker_adapter ]       If the adapter has a docker image use it as prio 1
               [ --force_docker_plantuml ]      The script will prefer a local installed plantuml, force usage of docker image instead
               [ -h | --help ]                  This help
```

It can be easily tested against itself. Once you cloned this repository, you can check how to reverse engineer CSharp code as follows:

`./revenger.sh --from_dir dotnet-adapter/DotnetPreAdapter --out_dir out-revenger-csharp-uses  --from_language csharp`

Python code can be reversed engineered as follows (please not that the Python adapter is being refactored because of some wrongly generated inconsistencies):

`./revenger.sh --from_dir revenger --out_dir out-revenger-python-uses`

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


