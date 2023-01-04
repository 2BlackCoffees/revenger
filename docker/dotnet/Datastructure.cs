using System;
using System.Collections;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Reflection;
using System.Reflection.Metadata;
using System.Text.RegularExpressions;
using static DotNetPreAdapter.Datastructure;
using static DotNetPreAdapter.Datastructure.Method;

namespace DotNetPreAdapter
{
    public class Datastructure
    {
        const string NOT_EXTRACTED = "** Not extracted **";
        const string STATICS = "statics";
        const string METHODS = "methods";
        const string VARIABLES = "variables";

        public class Method
        {

            public class ParameterType
            {
                public string parameter { get; set; }
                public string userType { get; set; }
                public string mostProbableNamespace { get; set; }
                public ParameterType(string parameter_, string userType_, string mostProbableNamespace_)
                {
                    parameter = parameter_;
                    userType = userType_;
                    mostProbableNamespace = mostProbableNamespace_;
                }
            }
            public string methodName { get; set; }
            public List<ParameterType> parameters { get; set; }
            public Boolean IsPrivate { get; set; }
            public Method(string methodName_, List<ParameterType> parameters_, Boolean IsPrivate_)
            {
                methodName = methodName_;
                parameters = new List<ParameterType>(parameters_);
                IsPrivate = IsPrivate_;
            }

        }
        public class Static
        {
            public string StaticName { get; set; }
            public string StaticType { get; set; }
            public Static(string StaticName_, string StaticType_)
            {
                StaticName = StaticName_;
                StaticType = StaticType_;
            }
        }
        public class Variable
        {
            public string variableName { get; set; }
            public string variableType { get; set; }
            public string mostProbableNamespace { get; set; }
            public bool IsMember { get; set; }
            public Variable(string variableName_, string variableType_, string mostProbableNamespace_, bool IsMember_)
            {
                variableName = variableName_;
                variableType = variableType_;
                mostProbableNamespace = mostProbableNamespace_;
                IsMember = IsMember_;
            }
        }

        public class SubDataStructure
        {
            string fqdn_class_name;
            string filename;
            List<string> usings;
            Dictionary<string, string> from_imports = new();
            string filemodule;
            List<string> nameSpaceList;

            List<string> bases = new();
            List<string> inner_classes = new();
            List<string> anonymousStaticInvocations = new();
            List<string> anonymousInvocations = new();
            List<string> genericTypes = new();
            Boolean is_abstract_field = false;
            Boolean isInterface = false;
            List<Static> statics = new();
            List<Variable> variables = new();
            List<Method> methods = new();


            public SubDataStructure(string filename_, string filemodule_, List<string> usings_, string fqdn_class_name_, List<string> nameSpaceList_)
            {
                fqdn_class_name = fqdn_class_name_;
                filename = filename_;
                usings = new List<string>(usings_);
                filemodule = filemodule_;
                nameSpaceList = new List<string>(nameSpaceList_);
            }


            public void set_abstract()
            {
                is_abstract_field = true;
            }
            public void setInterface()
            {
                isInterface = true;
            }
            public List<string> getUsings()
            {
                return usings;
            }
            public void addImport(string fqdnClassName, string namespaceName)
            {
                from_imports[fqdnClassName] = namespaceName;
            }
            public Dictionary<string, string> getImports()
            {
                return from_imports;
            }
            public void addGenericType(string genericType)
            {
                genericTypes.Add(genericType);
            }
            public void addAnonymousInvocation(string className)
            {
                anonymousInvocations.Add(className);
            }
            public void addAnonymousStaticInvocation(string className)
            {
                anonymousStaticInvocations.Add(className);
            }
            public void add_base_class(string base_class)
            {
                bases.Add(base_class);
            }

            public void add_static(string static_name, string static_type)
            {
                statics.Add(new Static(static_name, static_type));
            }
            public void add_method(string method_name_, List<Tuple<string, string, string>> arguments_tuple_, Boolean is_private_)
            {
                List<ParameterType> Arguments_ = new List<ParameterType>();
                foreach (var Argument in arguments_tuple_)
                {
                    Arguments_.Add(new ParameterType(Argument.Item1, Argument.Item2, Argument.Item3));
                }
                methods.Add(new Method(method_name_, Arguments_, is_private_));
            }
            public void add_variable(string variableName, string variableType, string mostProbableNamespace, Boolean is_member)
            {
                variables.Add(new Variable(variableName, variableType, mostProbableNamespace, is_member));
            }
            public void add_inner_class(string inner_class_name)
            {
                inner_classes.Add(inner_class_name);
            }

            public Boolean is_abstract()
            {
                return is_abstract_field;
            }
            public bool IsInterface()
            {
                return isInterface;
            }
            public Boolean has_static_fields()
            {
                return statics.Count > 0;
            }
            public Boolean has_method_fields()
            {
                return methods.Count > 0;
            }
            public Boolean has_variables_fields()
            {
                return variables.Count > 0;
            }

            public List<string> getAnonymousInvocation()
            {
                return anonymousInvocations;
            }
            public List<string> getAnonymousStaticInvocation()
            {
                return anonymousStaticInvocations;
            }
            public List<string> getGenericTypes()
            {
                return genericTypes;
            }
            public Dictionary<string, string> get_from_imports()
            {
                return from_imports;
            }
            public string get_fqdn_class_name()
            {
                return fqdn_class_name;
            }
            public List<string> get_base_classes()
            {
                return bases;
            }
            public List<Static> get_static_fields()
            {
                return statics;
            }
            public List<Method> get_method_fields()
            {
                return methods;
            }
            public List<Variable> get_variable_fields()
            {
                return variables;
            }
            public List<string> get_inner_class_name()
            {
                return inner_classes;
            }
            public string get_filename()
            {
                return filename;
            }
            public string get_filemodule()
            {
                return filemodule;
            }
            public List<string> get_name_space_list()
            {
                return nameSpaceList;
            }
        }

        Dictionary<string, SubDataStructure> class_to_datastructure = new Dictionary<string, SubDataStructure>();
        Dictionary<string, List<SubDataStructure>> namespace_to_datastructures = new Dictionary<string, List<SubDataStructure>>();
        Dictionary<string, List<string>> namespace_to_namespace_list = new Dictionary<string, List<string>>();
        List<string> skip_types = new List<string> { "string", "Boolean" };
        Logger logger;
        public Datastructure(Logger logger_)
        {

            skip_types.Add(NOT_EXTRACTED);
            logger = logger_;
        }

        public void ResolveClassNames()
        {
            foreach(SubDataStructure subDataStructure in class_to_datastructure.Values)
            {
                CorrectClassScope(subDataStructure, subDataStructure.getAnonymousInvocation(), true);
                CorrectClassScope(subDataStructure, subDataStructure.getAnonymousStaticInvocation(), true);
                CorrectClassScope(subDataStructure, subDataStructure.get_base_classes(), false);
                CorrectClassScope(subDataStructure, subDataStructure.getGenericTypes(), false);
                var variables = subDataStructure.get_variable_fields();
                for (int index = 0; index < variables.Count; ++index)
                {
                    Variable variable = variables[index];
                    logger.LogDebug($"  ResolveClassNames: Variable: name {variable.variableName}, current type: {variable.variableType}, most probable NS: {variable.mostProbableNamespace}.");
                    variables[index].variableType = GetFQDNForUsedClassName(
                            subDataStructure,
                            variables[index].variableType,
                            false,
                            variables[index].mostProbableNamespace);
                }
                foreach(Method method in subDataStructure.get_method_fields())
                {
                    for (int index = 0; index < method.parameters.Count; ++index)
                    {
                        logger.LogDebug($"  ResolveClassNames: Method: {method.methodName} Resolving parameter name {method.parameters[index].parameter}, current type: {method.parameters[index].userType}, most probable NS: {method.parameters[index].mostProbableNamespace}.");
                        method.parameters[index].userType = GetFQDNForUsedClassName(
                                subDataStructure,
                                method.parameters[index].userType,
                                false,
                                method.parameters[index].mostProbableNamespace);

                    }

                }
            }
        }
        void CorrectClassScope(SubDataStructure subDataStructure, List<string> classNameList, bool isAnymousCall)
        {
            if (classNameList != null)
            {
                for (int index = 0; index < classNameList.Count; ++index)
                {
                    classNameList[index] = GetFQDNForUsedClassName(subDataStructure, classNameList[index], isAnymousCall);
                }
            }

        }
        string GetFQDNForUsedClassName(SubDataStructure subDataStructure, string classUsage, bool isAnymousCall, string mostProbableNamespace = "")
        {
            string className = "";
            if (!isAnymousCall || Regex.Match(classUsage, @"\(.*\)\s*$", RegexOptions.IgnoreCase).Success)
            {
                className = isAnymousCall ? classUsage.Split('(')[0] : classUsage;
                var classnameList = get_classname_list();
                if (!classnameList.Contains(className) ||
                    (mostProbableNamespace.Length > 0 && !classnameList.Contains($"{mostProbableNamespace}.{className}")))
                {
                    try
                    {
                        foreach (char regexChar in "[]{}/\\-()")
                        {
                            className = className.Replace(regexChar.ToString(), $"\\{regexChar}");

                        }
                        var fittingClassNames = classnameList.Where(
                                p => Regex.Match(p, $"\\.{className}$").Success
                            ).ToArray();
                        if (fittingClassNames.Length == 1)
                        {
                            logger.LogDebug($"GetFQDNForUsedClassName: Found class {className} as {fittingClassNames[0]}");
                            className = fittingClassNames[0];
                        }
                        else if (fittingClassNames.Length > 1)
                        {

                            var bestFittingClassNames = classnameList.Where(
                                p => Regex.Match(p, $"{mostProbableNamespace}\\.{className}$").Success
                                ).ToArray();
                            if (bestFittingClassNames.Length > 0)
                            {
                                fittingClassNames = bestFittingClassNames;
                                logger.LogDebug($"GetFQDNForUsedClassName: Found class {className} with multiple better fitting variants: {String.Join(", ", fittingClassNames)}");
                            }
                            logger.LogWarning($"GetFQDNForUsedClassName: Found class {className} with multiple variants: {String.Join(", ", fittingClassNames)}");
                            logger.LogWarning($"GetFQDNForUsedClassName: Will be defaulting to the first one: {className} as {fittingClassNames[0]}");
                            className = fittingClassNames[0];
                        }
                        else
                        {
                            logger.LogWarning($"GetFQDNForUsedClassName: Class {className} not found in the whole list of classes! Class will be left as is.");
                        }
                    } catch (System.Text.RegularExpressions.RegexParseException e)
                    {
                        logger.LogError($"GetFQDNForUsedClassName: Class {className} could not be regexe parsed (Class will be left as is):\n{e.ToString()}");

                    }
                } else
                {
                    logger.LogDebug($"GetFQDNForUsedClassName: OK: Class {className} found in the list of classes! Class will be left as is.");
                }
            }
            return className;
        }


        public List<string> get_skip_types()
        {
            return skip_types;
        }
        void append_sub_datastructure(SubDataStructure sub_datastructure)
        {
            string fqdn_class_name = sub_datastructure.get_fqdn_class_name();
            if (!class_to_datastructure.ContainsKey(fqdn_class_name))
            {
                class_to_datastructure[fqdn_class_name] = sub_datastructure;
                string namespace_name = String.Join(".", sub_datastructure.get_name_space_list().ToArray());
                if (!namespace_to_datastructures.ContainsKey(namespace_name))
                {
                    namespace_to_datastructures[namespace_name] = new List<SubDataStructure>();
                }
                namespace_to_datastructures[namespace_name].Add(sub_datastructure);
                namespace_to_namespace_list[namespace_name] = sub_datastructure.get_name_space_list();
            }
            else
            {
                Console.WriteLine($"WARNING: Class {fqdn_class_name} is being registered a second time \n" +
                  $"   -> First time content is from file {class_to_datastructure[fqdn_class_name].get_filename()}, from class: {class_to_datastructure[fqdn_class_name].get_fqdn_class_name()}: Ignoring.");
            }
        }


        public void append_class(string filename, string filemodule, List<string> usings, string fqdn_class_name, List<string> nameSpaceList)
        {
            SubDataStructure sub_datastructure = new SubDataStructure(filename, filemodule, usings, fqdn_class_name, nameSpaceList);
            append_sub_datastructure(sub_datastructure);
        }

        public List<string> get_classname_list()
        {
            return new List<string>(class_to_datastructure.Keys);
        }

        public SubDataStructure? get_datastructures_from_class_name(string class_name)
        {
            if (class_to_datastructure.ContainsKey(class_name))
            {
                return class_to_datastructure[class_name];
            }
            logger.LogWarning($"Requested class {class_name} was not found in the datastructure");
            return null;
        }
    }
}

/*    def get_sorted_name_spaces(self) -> List[str]:
        return sorted(self.namespace_to_datastructures.keys())

    def get_datastructures_from_namespace(self, namespace) -> List[Datastructure.SubDataStructure]:
        return self.namespace_to_datastructures[namespace]

    def get_namespace_list_from_namespace_name(self, namespace_name) -> List[str]:
        return self.namespace_to_namespace_list[namespace_name]

    def class_exists(self, class_name) -> bool:
        return class_name in self.class_to_datastructure.keys()

    def filename_exists(self, filename) -> bool:
        return filename in self.filename_to_datastructure.keys()

    def append_sub_datastructure(self, sub_datastructure: Datastructure.SubDataStructure) -> None:
        fqdn_class_name = sub_datastructure.get_fqdn_class_name()
        if fqdn_class_name not in self.class_to_datastructure.keys():
            self.class_to_datastructure[fqdn_class_name] = sub_datastructure
            namespace = ".".join(sub_datastructure.get_name_space_list())
            if namespace not in self.namespace_to_datastructures:
                self.namespace_to_datastructures[namespace] = []
    self.namespace_to_datastructures[namespace].append(sub_datastructure)
            self.namespace_to_namespace_list[namespace] = sub_datastructure.get_name_space_list()
        else:
            self.logger.log_debug(f"WARNING: Class {fqdn_class_name} is being registered a second time \n" + \
                  f"   -> First time content is from file {self.class_to_datastructure[fqdn_class_name].get_filename()}, from class: {self.class_to_datastructure[fqdn_class_name].get_fqdn_class_name()}: Ignoring.")
            #traceback.print_stack()

		public Datastructure()
		{
		}
	}
}
*/