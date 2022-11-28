# Py2plantuml
This program trnsforms a python program composed of many modules into a clickable svg class diagram of the whole application.
Classes can be filtered in just clicking on them to analyze and understand how the program is structured.

## Usage
`./py2plantuml.sh <directory-to-python-code> <output-directory>`

# TODOs
## Design improvement needed
The application was created to be quickly usable. It needs to be refactored as follows:
  * The AST is transformed in a very bad data sctructure thus not allowing an easy maintainance. It should be refactored to a hierarchy of data classes.
  * Currently non member variables are generating a Composition dependency whereas they should be generating a Use dependency.
  * Parameters of methods using classes should generate a use dependency unless class members are taking the paramter to generate a Composition dependency.
  * Use NodeVisitor and NodeTransformer instead of the current design (See https://docs.python.org/3/library/ast.html for more details)

## What features are missing
  * The tool could be easily become language agnostic leveraging the hexagonal pattern:
    * The analysis of python code should be an adapater to the hexagon pattern that would take a generic dada type and transform it into a clickable set of svg files.
    * Adapters for other languages could be created.


