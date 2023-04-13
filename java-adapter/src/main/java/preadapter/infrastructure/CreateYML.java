package preadapter.infrastructure;

import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.error.Mark;
import org.yaml.snakeyaml.nodes.*;
import preadapter.Logger;
import preadapter.domain.Datastructure;

import java.io.File;
import java.io.FileNotFoundException;
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
                appendTupleNodeValueString(subDataStructureMappingYmlNode, "is_inner_class", subDataStructure.isInnerClass() ? "True" : "False");
                appendTupleNodeValueString(subDataStructureMappingYmlNode, "filemodule", subDataStructure.get_filemodule());
                var fromImportsSequenceNode = new SequenceNode(
                        Tag.SEQ, new ArrayList<>(), dummperOptions);
                subDataStructure.get_from_imports().forEach((fqdnClassName, namespaceName) -> {
                    var fromImportsMappingNode = new MappingNode(
                            Tag.MAP, new ArrayList<>(), dummperOptions);
                    appendTupleNodeValueString(fromImportsMappingNode, "imported_class_name", fqdnClassName);
                    appendTupleNodeValueString(fromImportsMappingNode, "namespace_path", namespaceName);
                    fromImportsSequenceNode.getValue().add(fromImportsMappingNode);
                });
                appendTupleNodeValueSequenceNode(subDataStructureMappingYmlNode, "from_imports", fromImportsSequenceNode);

                appendSequence(subDataStructureMappingYmlNode,
                        subDataStructure.get_inner_class_name(),
                        "inner_classes");

                appendSequence(subDataStructureMappingYmlNode,
                        subDataStructure.getAnonymousInvocation(),
                        "anonymous_calls");

                appendSequence(subDataStructureMappingYmlNode,
                        subDataStructure.get_base_classes(),
                        "base_classes");

                var staticsSequenceNode = new SequenceNode(
                        Tag.SEQ, new ArrayList<>(), dummperOptions);
                subDataStructure.get_static_fields().forEach(staticType -> {
                    var staticsMappingNode = new MappingNode(
                            Tag.MAP, new ArrayList<>(), dummperOptions);
                    appendTupleNodeValueString(staticsMappingNode, "static_name", staticType.StaticName);
                    appendTupleNodeValueString(staticsMappingNode, "static_type", staticType.StaticType);
                    staticsSequenceNode.getValue().add(staticsMappingNode);
                });
                appendTupleNodeValueSequenceNode(subDataStructureMappingYmlNode, "statics", staticsSequenceNode);

                var variablesSequenceNode = new SequenceNode(
                        Tag.SEQ, new ArrayList<>(), dummperOptions);
                subDataStructure.get_variable_fields().forEach(variable -> {
                    var variablesMappingNode = new MappingNode(
                            Tag.MAP, new ArrayList<>(), dummperOptions);
                    appendTupleNodeValueString(variablesMappingNode, "variable_name", variable.variableName);
                    appendTupleNodeValueString(variablesMappingNode, "variable_type", variable.variableType);
                    appendTupleNodeValueString(variablesMappingNode, "is_member", variable.IsMember ? "True" : "False");
                    variablesSequenceNode.getValue().add(variablesMappingNode);
                });
                appendTupleNodeValueSequenceNode(subDataStructureMappingYmlNode, "variables", variablesSequenceNode);


                var methodsSequenceNode = new SequenceNode(
                        Tag.SEQ, new ArrayList<>(), dummperOptions);
                subDataStructure.get_method_fields().forEach(method -> {
                    var parameters = new SequenceNode(
                            Tag.SEQ, new ArrayList<>(), dummperOptions);
                    method.getParameters().forEach(parameter -> {
                        var methodParametersMappingNode = new MappingNode(
                                Tag.MAP, new ArrayList<>(), dummperOptions);
                        appendTupleNodeValueString(methodParametersMappingNode, "parameter_name", parameter.parameter);
                        appendTupleNodeValueString(methodParametersMappingNode, "parameter_type", parameter.userType);
                        parameters.getValue().add(methodParametersMappingNode);
                    });

                    var methodVariables = new SequenceNode(
                            Tag.SEQ, new ArrayList<>(), dummperOptions);
                    method.variables.forEach(variable -> {
                        var methodVariablesMappingNode = new MappingNode(
                                Tag.MAP, new ArrayList<>(), dummperOptions);
                        appendTupleNodeValueString(methodVariablesMappingNode, "variable_name", variable.variableName);
                        appendTupleNodeValueString(methodVariablesMappingNode, "variable_type", variable.variableType);
                        methodVariables.getValue().add(methodVariablesMappingNode);

                    });

                    var methodNode = new MappingNode(
                            Tag.MAP, new ArrayList<>(), dummperOptions);
                    appendTupleNodeValueString(methodNode, "method_name", method.methodName);
                    appendTupleNodeValueSequenceNode(methodNode, "parameters", parameters);
                    appendTupleNodeValueSequenceNode(methodNode, "method_variables", methodVariables);
                    appendTupleNodeValueString(methodNode, "is_private", method.IsPrivate ? "True" : "False");
                    methodsSequenceNode.getValue().add(methodNode);
                });
                appendTupleNodeValueSequenceNode(subDataStructureMappingYmlNode, "methods", methodsSequenceNode);

                var tmpMappingNode = new MappingNode( Tag.MAP, new ArrayList<>(), dummperOptions);
                tmpMappingNode.getValue().add(
                        new NodeTuple(
                                new ScalarNode(Tag.STR, "sub_datastructure",
                                        startMark, endMark, DumperOptions.ScalarStyle.PLAIN),
                                subDataStructureMappingYmlNode)
                );
                subDataStructureSequenceYmlNode.getValue().add(tmpMappingNode);
            } // if subDataStructure != null
        }); // for each classname

        Yaml yaml = new Yaml();
        try {
            logger.logInfo("Writing YAML file: " + toFile);
            PrintWriter writer = new PrintWriter(toFile);
            yaml.serialize(subDataStructureSequenceYmlNode, writer);
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e);
        }

    }
}