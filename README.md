# Py2plantuml
This program transforms either a python or a C# program into a clickable class diagram of the whole application.
Classes can be filtered in just clicking on them to analyze and understand how the program is structured.

The program is based on the hexagonal pattern where languages are adapters. 
At the moment adapters exist only for Python and C#.

See here for a quick introduction what this tool is used for and how to use it (Outdated presentation): https://www.youtube.com/watch?v=u4VpfKfgr7Q 

Currently the Python adapter requires:
1. All user defined modules to be imported one per line
2. When importing a user module, the whole module path must be specified from the entry point
3. All declarations and method parameters must be properly annotated with their type

## Usage
`./py2plantuml.sh -h`
```
py2plantuml.sh [ -i | --from_dir ]   Mandatory: Where the source files are located.
               [ -o | --out_dir ]    Mandatory: Where to store the puml and svg files
               [ --init ]                       Run update on python dependencies (Run it at least the first time)
               [ -d | --plantuml_install ]      Install plantuml (not graphviz however, you will have to install it yourself)
               [ -p | --plantweb_dep_install ]  Uses plantweb server instead of local plantuml: Insecure DO NOT USE IT for sensitive data.
               [ --skip_uses_relation ]         Skip UML uses relations
               [ --info ]                       Info logs
               [ --debug ]                      Debug logs
               [ --trace ]                      Trace logs
               [ --from_language csharp ]       Currently only python (default) or csharp adapter exist
               [ -h | --help ]                  This help
```
# TODOs
## Design improvement needed
The application was created to be quickly usable. The Python adapeter needs to be refactored as follows:
  * On going: Python Adapter needs to be improved (See https://docs.python.org/3/library/ast.html for more details)
  * The application should be able to extract their type from the instantiated type (and not necessarily the annotation)
  * The whole module path should not be absolutely mandatory
  * More than one user defined types shoud be usable
  

## What features are missing
  We have a Trello Board here: https://trello.com/b/ExI3XPoO/candycat-py2plantuml.


