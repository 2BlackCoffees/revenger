// Refactor https://github.com/2BlackCoffees/revenger/blob/main/dotnet-adapter/DotnetPreAdapter/CreateYml.cs to java

package preadapter.infrastructure;


import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.error.Mark;
import org.yaml.snakeyaml.nodes.*;
import preadapter.Logger;
import preadapter.domain.Datastructure;

import java.io.PrintWriter;
import java.util.*;

public class CreateYML {

    private final DumperOptions.FlowStyle dummperOptions = DumperOptions.FlowStyle.AUTO;
    private final Mark startMark = null;
    private final Mark endMark = null;

    private boolean appendTupleNodeValueSequenceNode(MappingNode mappingNode, String key, SequenceNode value) {

        return mappingNode.getValue().add( new NodeTuple(
                new ScalarNode(Tag.STR, key, startMark, endMark, DumperOptions.ScalarStyle.PLAIN),
                value
        ));
    }

    private boolean appendTupleNodeValueString(MappingNode mappingNode, String key, String value) {

        return mappingNode.getValue().add( new NodeTuple(
                new ScalarNode(Tag.STR, key, startMark, endMark, DumperOptions.ScalarStyle.PLAIN),
                new ScalarNode(Tag.STR, value, startMark, endMark, DumperOptions.ScalarStyle.PLAIN)
        ));
    }
    private boolean appendTupleNodeValueStringToSequenceNode(SequenceNode sequenceNode, String key, String value) {
        var mappingNode = new MappingNode(
                Tag.MAP, new ArrayList<>(), dummperOptions);
        mappingNode.getValue().add( new NodeTuple(
                new ScalarNode(Tag.STR, key, startMark, endMark, DumperOptions.ScalarStyle.PLAIN),
                new ScalarNode(Tag.STR, value, startMark, endMark, DumperOptions.ScalarStyle.PLAIN)
        ));
        return sequenceNode.getValue().add(mappingNode);
    }

    private void appendSequence(MappingNode mappingNode, List<String> list, String nodeName) {

        SequenceNode subSequenceNode = new SequenceNode(
                Tag.SEQ, new ArrayList<>(), dummperOptions);
        list.forEach(element -> {
            subSequenceNode.getValue().add(new ScalarNode(Tag.STR, element, startMark, endMark,
                    DumperOptions.ScalarStyle.PLAIN));
        });

        mappingNode.getValue().add(new NodeTuple(
                new ScalarNode(Tag.STR, nodeName,
                        startMark, endMark, DumperOptions.ScalarStyle.PLAIN
                ), subSequenceNode));
    }
    public void Create(Datastructure datastructure, String toFile, Logger logger) {
        var subDataStructureSequenceYmlNode = new SequenceNode(
                Tag.SEQ, new ArrayList<>(), dummperOptions);

        datastructure.get_classname_list().forEach(className -> {

            var subDataStructureMappingYmlNode = new MappingNode(
                    Tag.MAP, new ArrayList<>(), dummperOptions);
            Datastructure.SubDataStructure subDataStructure = datastructure.get_datastructures_from_class_name(className);
            if (subDataStructure != null) {
                appendTupleNodeValueString(subDataStructureMappingYmlNode, "fqdn_class_name", subDataStructure.get_fqdn_class_name());
                appendTupleNodeValueString(subDataStructureMappingYmlNode, "filename", subDataStructure.get_filename());
                appendTupleNodeValueString(subDataStructureMappingYmlNode, "is_abstract", subDataStructure.is_abstract() ? "True" : "False");
                appendTupleNodeValueString(subDataStructureMappingYmlNode, "is_interface", subDataStructure.IsInterface() ? "True" : "False");
                appendTupleNodeValueString(subDataStructureMappingYmlNode, "filemodule", subDataStructure.get_filemodule());
                var fromImports = new SequenceNode(
                        Tag.SEQ, new ArrayList<>(), dummperOptions);
                subDataStructure.get_from_imports().forEach((fqdnClassName, namespaceName) -> {
                    appendTupleNodeValueStringToSequenceNode(fromImports, "imported_class_name", fqdnClassName);
                    appendTupleNodeValueStringToSequenceNode(fromImports, "namespace_path", namespaceName);
                });
                appendTupleNodeValueSequenceNode(subDataStructureMappingYmlNode, "from_imports", fromImports);

                appendSequence(subDataStructureMappingYmlNode,
                        subDataStructure.get_inner_class_name(),
                        "inner_classes");

                appendSequence(subDataStructureMappingYmlNode,
                        subDataStructure.getAnonymousInvocation(),
                        "anonymous_calls");

                appendSequence(subDataStructureMappingYmlNode,
                        subDataStructure.get_base_classes(),
                        "base_classes");

                subDataStructure.get_static_fields().forEach(staticType -> {
                    var statics = new SequenceNode(
                            Tag.SEQ, new ArrayList<>(), dummperOptions);
                    appendTupleNodeValueStringToSequenceNode(statics, "static_name", staticType.StaticName);
                    appendTupleNodeValueStringToSequenceNode(statics, "static_type", staticType.StaticType);
                    appendTupleNodeValueSequenceNode(subDataStructureMappingYmlNode, "statics", statics);
                });

                var variables = new SequenceNode(
                        Tag.SEQ, new ArrayList<>(), dummperOptions);
                subDataStructure.get_variable_fields().forEach(variable -> {
                    appendTupleNodeValueStringToSequenceNode(variables, "variable_name", variable.variableName);
                    appendTupleNodeValueStringToSequenceNode(variables, "variable_type", variable.variableType);
                    appendTupleNodeValueStringToSequenceNode(variables, "is_member", variable.IsMember ? "True" : "False");
                });

                var methods = new SequenceNode(
                        Tag.SEQ, new ArrayList<>(), dummperOptions);
                subDataStructure.get_method_fields().forEach(method -> {
                    var parameters = new SequenceNode(
                            Tag.SEQ, new ArrayList<>(), dummperOptions);
                    method.getParameters().forEach(parameter -> {

                        appendTupleNodeValueStringToSequenceNode(parameters, "parameter_name", parameter.parameter);
                        appendTupleNodeValueStringToSequenceNode(parameters, "parameter_type", parameter.userType);
                    });

                    var methodVariables = new SequenceNode(
                            Tag.SEQ, new ArrayList<>(), dummperOptions);
                    method.variables.forEach(variable -> {
                        appendTupleNodeValueStringToSequenceNode(methodVariables, "variable_name", variable.variableName);
                        appendTupleNodeValueStringToSequenceNode(methodVariables, "variable_type", variable.variableType);
                    });

                    var methodNode = new MappingNode(
                            Tag.SEQ, new ArrayList<>(), dummperOptions);
                    appendTupleNodeValueString(methodNode, "method_name", method.methodName);
                    appendTupleNodeValueSequenceNode(methodNode, "parameters", parameters);
                    appendTupleNodeValueSequenceNode(methodNode, "method_variables", methodVariables);
                    appendTupleNodeValueString(methodNode, "is_private", method.IsPrivate ? "True" : "False");
                    methods.getValue().add(methodNode);
                });





            }

            var tmpMappingNode = new MappingNode( Tag.MAP, new ArrayList<>(), dummperOptions);
            tmpMappingNode.getValue().add(
                    new NodeTuple(
                            new ScalarNode(Tag.STR, "sub_datastructure",
                                    startMark, endMark, DumperOptions.ScalarStyle.PLAIN),
                            subDataStructureMappingYmlNode)
            );
            subDataStructureSequenceYmlNode.getValue().add(tmpMappingNode);
        });

        Yaml yaml = new Yaml();
        yaml.serialize(subDataStructureSequenceYmlNode, new PrintWriter(System.out));
    }




}
/*
        var subDatastructureYmlNode = new MappingNode(
                Tag.MAP, new ArrayList<NodeTuple>, DumperOptions.FlowStyle.BLOCK);
        datastructure.get_classname_list().forEach(className -> {});
        {
            SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(classname);
            if (subDataStructure != null)
            {



                ///// C# code

    
                            subDatastructureYmlNode.Add(new YamlMappingNode(
                                new YamlScalarNode("sub_datastructure"),
                                new YamlMappingNode(

    

                                    new YamlScalarNode("filemodule"),
                                        new YamlScalarNode(subDataStructure.get_filemodule())
    
                                        )
                                    )
                                );
                        }
                    }
    
                    var stream = new YamlStream(
                        new YamlDocument(subDatastructureYmlNode
    
                            )
                        );
                    using (TextWriter writer = File.CreateText(toDir + "/output.yaml"))
                    {
                        stream.Save(writer, false);
                    }
                }
            }
        }
    }
    
*/