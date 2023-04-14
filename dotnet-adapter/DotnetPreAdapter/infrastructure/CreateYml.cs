using System;
using System.Xml;
using System;
using YamlDotNet.RepresentationModel;
using YamlDotNet.Serialization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using static DotNetPreAdapter.Domain.Datastructure;
using System.Collections;
using YamlDotNet.Core.Tokens;
using System.IO;

// dotnet add package YamlDotNet --version 12.2.0
namespace DotNetPreAdapter
{
    namespace Infrastructure
    {
        public class CreateYml
        {
            public void Create(Domain.Datastructure datastructure, string toDir, Utils.Logger logger)
            {

                var subDatastructureYmlNode = new YamlSequenceNode();
                foreach (string classname in datastructure.get_classname_list())
                {
                    SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(classname);
                    if (subDataStructure != null)
                    {
                        var fromImports = new YamlSequenceNode();
                        foreach (var (imported_class_name, namespace_path) in subDataStructure.get_from_imports())
                        {
                            fromImports.Add(
                                new YamlMappingNode(
                                    new YamlScalarNode("imported_class_name"),
                                        new YamlScalarNode(imported_class_name),
                                    new YamlScalarNode("namespace_path"),
                                        new YamlScalarNode(namespace_path)
                                    )
                                );
                        }

                        var innerClasses = new YamlSequenceNode();
                        foreach (string class_name in subDataStructure.get_inner_class_name())
                        {
                            innerClasses.Add(new YamlScalarNode(class_name));
                        }
                        var anonymousCalls = new YamlSequenceNode();
                        foreach (string anonymousCall in subDataStructure.getAnonymousInvocation())
                        {
                            if (anonymousCall.Length > 0)
                            {
                                anonymousCalls.Add(
                                            new YamlScalarNode(anonymousCall)
                                    );
                            }
                            else
                            {
                                logger.LogWarning($"Skipping empty anonymous call found while creating YML file from class {subDataStructure.get_fqdn_class_name()}");
                            }
                        }
                        var baseClasses = new YamlSequenceNode();
                        foreach (string baseClass in subDataStructure.get_base_classes())
                        {
                            baseClasses.Add(
                                        new YamlScalarNode(baseClass)
                                );
                        }
                        var statics = new YamlSequenceNode();
                        foreach (Static staticTypes in subDataStructure.get_static_fields())
                        {
                            statics.Add(
                                new YamlMappingNode(
                                    new YamlScalarNode("static_name"),
                                        new YamlScalarNode(staticTypes.StaticName),
                                    new YamlScalarNode("static_type"),
                                        new YamlScalarNode(staticTypes.StaticType)
                                    )
                                );
                        }
                        var variables = new YamlSequenceNode();
                        foreach (Variable variable in subDataStructure.get_variable_fields())
                        {
                            variables.Add(
                                    new YamlMappingNode(
                                        new YamlScalarNode("variable_name"),
                                            new YamlScalarNode(variable.variableName),
                                        new YamlScalarNode("variable_type"),
                                            new YamlScalarNode(variable.variableType),
                                        new YamlScalarNode("is_member"),
                                            new YamlScalarNode(variable.IsMember ? "True" : "False")
                                    )
                            );
                        }

                        var methods = new YamlSequenceNode();
                        foreach (Method method in subDataStructure.get_method_fields())
                        {
                            var parameters = new YamlSequenceNode();
                            foreach (var parameter in method.parameters)
                            {
                                parameters.Add(new YamlMappingNode(
                                        new YamlScalarNode("parameter_name"),
                                            new YamlScalarNode(parameter.parameter),
                                        new YamlScalarNode("parameter_type"),
                                            new YamlScalarNode(parameter.userType)));
                            }
                            var methodVariables = new YamlSequenceNode();
                            foreach (var variable in method.variables)
                            {
                                methodVariables.Add(new YamlMappingNode(
                                        new YamlScalarNode("variable_name"),
                                            new YamlScalarNode(variable.variableName),
                                        new YamlScalarNode("variable_type"),
                                            new YamlScalarNode(variable.variableType)));
                            }

                            methods.Add(
                                    new YamlMappingNode(
                                        new YamlScalarNode("method_name"),
                                        new YamlScalarNode(method.methodName),
                                        new YamlScalarNode("parameters"),
                                        parameters,
                                        new YamlScalarNode("method_variables"),
                                        methodVariables,
                                        new YamlScalarNode("is_private"),
                                        new YamlScalarNode(method.IsPrivate ? "True" : "False")
                                        )
                                    );
                        }


                        subDatastructureYmlNode.Add(new YamlMappingNode(
                            new YamlScalarNode("sub_datastructure"),
                            new YamlMappingNode(
                                new YamlScalarNode("fqdn_class_name"),
                                    new YamlScalarNode(subDataStructure.get_fqdn_class_name()),

                                new YamlScalarNode("filename"),
                                    new YamlScalarNode(subDataStructure.get_filename()),
                                new YamlScalarNode("from_imports"),
                                    fromImports,
                                new YamlScalarNode("anonymous_calls"),
                                    anonymousCalls,
                                new YamlScalarNode("inner_classes"),
                                    innerClasses,
                                new YamlScalarNode("variables"),
                                    variables,
                                new YamlScalarNode("is_abstract"),
                                    new YamlScalarNode(subDataStructure.is_abstract() ? "True" : "False"),
                                new YamlScalarNode("is_interface"),
                                    new YamlScalarNode(subDataStructure.IsInterface() ? "True" : "False"),
                                new YamlScalarNode("is_inner_class"),
                                    new YamlScalarNode(subDataStructure.IsInnerClass() ? "True" : "False"),

                                new YamlScalarNode("base_classes"),
                                    baseClasses,

                                new YamlScalarNode("statics"),
                                    statics,
                                new YamlScalarNode("methods"),
                                    methods,

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

                