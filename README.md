# Py2plantuml
This program trnsforms a python program composed of many modules into a clickable svg class diagram of the whole application.
Classes can be filtered in just clicking on them to analyze and understand how the program is structured.

See here for a quick introduction what this tool is used for and how to use it: https://www.youtube.com/watch?v=u4VpfKfgr7Q 

Currently the application requires:
1. All user defined modules to be imported one per line
2. When importing a user module, the whole module path must be specified from the entry point
3. All declarations and method parameters must be properly annotated with their type

## Usage
`./py2plantuml.sh <directory-to-python-code> <output-directory>`

# TODOs
## Design improvement needed
The application was created to be quickly usable. It needs to be refactored as follows:
  * The AST is transformed in a very bad data sctructure thus not allowing an easy maintainance. It should be refactored to a hierarchy of data classes.
  * Use NodeVisitor and NodeTransformer instead of the current design (See https://docs.python.org/3/library/ast.html for more details)
  * The application should be able to extract their type from the instantiated type (and not necessarily the annotation)
  * The whole module path should not be absolutely mandatory
  * More than one user defined types shoud be usable
  

## What features are missing
  * The tool could be easily become language agnostic leveraging the hexagonal pattern:
    * The analysis of python code should be an adapater to the hexagon pattern that would take a generic dada type and transform it into a clickable set of svg files.
    * Adapters for other languages could be created.


