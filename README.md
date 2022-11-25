# Py2plantuml
This program trnsforms a python program composed of many modules into a clickable svg class diagram of the whole application.
Classes can be filtered in just clicking on them to analyze and understand how the program is structured.

## Usage
`./py2plantuml.sh <directory-to-python-code> <output-directory>`

# TODOs
## Design improvement needed
The application was created to be quickly usable. It needs to be refactored as follows:
  * The AST is transformed in a very bad data sctructure thus not allowing an easy maintainance. It should be refactored to a hierarchy of data classes.
  * Use NodeVisitor and NodeTransformer instead of the current design (See https://docs.python.org/3/library/ast.html for more details)

## What features are missing
 * We should be able to have a view where all packages are properly separated in a hierarchical way.
  * The tool could be easily become language agnostic leveraging the hexagonal pattern:
    * The analysis of python code should be an adapater to the hexagon pattern that would take a generic dada type and transform it into a clickable set of svg files.
    * Adapters for other languages could be created.


