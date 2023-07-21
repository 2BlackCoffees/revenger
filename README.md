![RevEngEr](./assets/revenger.png?raw=true "Revenger")

Revenger stands for REVerse ENGineER.

This program transforms source code into a clickable class diagram of the
whole application: The supported languages are Python, C# and Java.

The goal of having a clickable class diagram consists in filtering out
classes of interest together with their direct dependencies and thus
reducing tremendously the effort of analyzing and understanding the
structure of a program.

Because the tool is executed from a command line and generates html and svg
files, it can easily be integrated in a CI/CD pipeline thus allowing to
have a class diagrams constantly up to date with any change in the code.

The program is based on the hexagonal pattern where languages are adapters.
At the moment adapters exist only for Python, Java and C#.

Please note that not all features of the languages are supported. This
program is mostly designed to help:

1. Approaching unknown source code much faster thus reducing the effort for
   refactoring.
2. Creating a very low level documentation allowing developers to increase
   their coordination.

## Dependencies

- You will need to have either plantuml installed or at least Docker.
  - One option of the script allows to install plantuml partially or use a
    PlantUML Web server.
- If you need to reverse engineer C#, the script will try to use a locally
  accessible dotnet program.
  - If no dotnet can be found a Docker image can be used to run the
    adapter: The script will take care to try it.
- If Docker and dotnet are both not installed, the csharp reverse
  engineering will not be running.
- To reverse engineer Java you will need to have maven and at least Java 8
  properly installed.
  - Remember to set properly the JAVA_HOME

  - This is an example:

    `export JAVA_HOME=$(/usr/libexec/java_home)`

# Examples

Revenger can be easily tested reverse engineering its own code. Once you
cloned this repository, you can reverse engineer different parts of the
tool. Assuming your are in the directory where the script `./revenger.sh`
is located:

- Python code can be reversed engineered as follows (please note that the
  Python adapter is being refactored because of some wrongly generated
  inconsistencies):

  `./revenger.sh --from_dir revenger --out_dir out-revenger-python-uses`

- CSharp code can be reversed engineered as follows:

  `./revenger.sh --from_dir dotnet-adapter/DotnetPreAdapter --out_dir revenger.csharp.out  --from_language csharp`

- Java code can be reversed engineered as follows:

  `./revenger.sh --from_dir java-adapter/ --out_dir revenger.java.out  --from_language java`

- PlantUML itself can be reverse engineered, assuming it is cloned in the
  directory plantuml:

  `./revenger.sh --from_dir plantuml/ --out_dir plantuml.out  --from_language java --timeout 9000`

  `--timeout 9000` is needed because some files are very big and would
  prevent plantUML to generate diagrams within the default 15 minutes
  timeout.

# Summary example

The tool is able to provide a comprehensive summary that will be
automatically generated at the end of the reverse engineering process.
Because sometime the process can take hours or days, it can be useful to
see some parts of the result, the summary can easily be created with the
option `--summary_page_only`:

`./revenger.sh --from_dir ~plantuml/ --out_dir plantuml.out  --from_language java --summary_page_only`

The creation of the summary can take a couple of minutes.

See here
[Reversed enginnering of the java adapter](https://htmlpreview.github.io/?https://github.com/2BlackCoffees/revenger/blob/main/revenger-java-adapter.out/index.html)

# TODOs

Currently the Python adapter requires:

1. All user defined modules to be imported one per line
2. When importing a user module, the whole module path must be specified
   from the entry point
3. All declarations and method parameters must be properly annotated with
   their type

## Architecture

See below a high level architecture of the application:
![High level Architecture](./revenger-architecture.png?raw=true "Architecture of Revenger")

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
               [ --from_language lang_type ]    lang_type can be csharp, java, yaml or python.
               [ --force_docker_adapter ]       If the adapter has a docker image use it as prio 1
               [ --force_docker_plantuml ]      The script will prefer a local installed plantuml, force usage of docker image instead
               [ --timeout ]                    Defines the timeout in seconds when generating svg files (Default is 900 seconds)
               [ --process_svg_only ]           Skip puml generation and process (or continue processing svg generation)
               [ --summary_page_only ]          Generate a summary page (This option will short circuit the analysis processing)
               [ --force_python ]               Force a specific version of python
               [ --force_pip ]                  Force a specific version of pip
  PlantUML specific options for the local plantuml script:
               [ --plantuml.java_heap_max_size ]    Defines the max size for the Java heap for plantuml/dotgraphviz ONLY if using the local script
               [ --plantuml.graphvizdotpath ]       Defines the path to the application graphvizdot
               [ --plantuml.plantumljarpath ]       Defines the path to plantuml jar file
               [ --plantuml.javapath ]              Defines the path to java binary command
  Misc options:
               [ --no_full_diagrams ]               Generates no full diagrams (these digrams can be huge)
               [ --profiler_output ]                Enable the python profiler: specify the filename for the output
               [ --start_with_biggest_sizes ]       Processes by default smallest PUML files size first, with this option, start with biggest PUML files size
               [ -h | --help ]                      This help
```

## Design improvement needed

The application was created to be quickly usable. The Python adapeter needs
to be refactored as follows:

- On going: Python Adapter needs to be improved (See
  https://docs.python.org/3/library/ast.html for more details)
- The application should be able to extract their type from the
  instantiated type (and not necessarily the annotation)
- The whole module path should not be absolutely mandatory
- More than one user defined types should be usable

## What features are missing

We have a Trello Board here: https://trello.com/b/KjH1OYzK/revenger.
