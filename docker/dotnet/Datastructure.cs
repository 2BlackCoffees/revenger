using System;
using System.Collections;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
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
                public string Parameter { get; set; }
                public string UserType { get; set; }
                public ParameterType(string Parameter_, string UserType_)
                {
                    Parameter = Parameter_;
                    UserType = UserType_;
                }
            }
            public string MethodName { get; set; }
            public List<ParameterType> Parameters { get; set; }
            public Boolean IsPrivate { get; set; }
            public Method(string MethodName_, List<ParameterType> Parameters_, Boolean IsPrivate_)
            {
                MethodName = MethodName_;
                Parameters = new List<ParameterType>(Parameters_);
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
            public string VariableName { get; set; }
            public string VariableType { get; set; }
            public Boolean IsMember { get; set; }
            public Variable(string VariableName_, string VariableType_, Boolean IsMember_)
            {
                VariableName = VariableName_;
                VariableType = VariableType_;
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
            List<string> name_space_list;

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


            public SubDataStructure(string filename_, string filemodule_, List<string> usings_, string fqdn_class_name_, List<string> name_space_list_)
            {
                fqdn_class_name = fqdn_class_name_;
                filename = filename_;
                usings = new List<string>(usings_);
                filemodule = filemodule_;
                name_space_list = new List<string>(name_space_list_);
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
            public void add_method(string method_name_, List<Tuple<string, string>> arguments_tuple_, Boolean is_private_)
            {
                List<ParameterType> Arguments_ = new List<ParameterType>();
                foreach (Tuple<string, string> Argument in arguments_tuple_)
                {
                    Arguments_.Add(new ParameterType(Argument.Item1, Argument.Item2));
                }
                methods.Add(new Method(method_name_, Arguments_, is_private_));
            }
            public void add_variable(string variable_name, string variable_type, Boolean is_member)
            {
                variables.Add(new Variable(variable_name, variable_type, is_member));
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
                return name_space_list;
            }
        }

        Dictionary<string, SubDataStructure> class_to_datastructure = new Dictionary<string, SubDataStructure>();
        Dictionary<string, List<SubDataStructure>> namespace_to_datastructures = new Dictionary<string, List<SubDataStructure>>();
        Dictionary<string, List<string>> namespace_to_namespace_list = new Dictionary<string, List<string>>();
        List<string> skip_types = new List<string> { "string", "Boolean" };

        public Datastructure()
        {

            skip_types.Add(NOT_EXTRACTED);
        }

        public void ResolveClassNames()
        {
            foreach(SubDataStructure subDataStructure in class_to_datastructure.Values)
            {
                var classNameList = subDataStructure.getAnonymousInvocation();
                for (int index = 0; index < classNameList.Count; ++index)
                {
                    classNameList[index] = GetFQDNForUsedClassName(subDataStructure, classNameList[index], true);
                }

                var baseClassNameList = subDataStructure.get_base_classes();
                for (int index = 0; index < baseClassNameList.Count; ++index)
                {
                    baseClassNameList[index] = GetFQDNForUsedClassName(subDataStructure, baseClassNameList[index], true);
                }

                var genericTypes = subDataStructure.getGenericTypes();
                for (int index = 0; index < genericTypes.Count; ++index)
                {
                    genericTypes[index] = GetFQDNForUsedClassName(subDataStructure, genericTypes[index], true);
                }


            }
        }
        public string GetFQDNForUsedClassName(SubDataStructure subDataStructure, string classUsage, bool isAnymousCall)
        {
            string className = "";
            if (!isAnymousCall || Regex.Match(classUsage, @"\(.*\)\s*$", RegexOptions.IgnoreCase).Success)
            {
                className = isAnymousCall ? classUsage.Split('(')[0] : classUsage;
                var classnameList = get_classname_list();
                if (!classnameList.Contains(className))
                {

                    var fittingClassNames = classnameList.Where(
                            p => Regex.Match(p, $".{className}$").Success
                        ).ToArray();
                    if (fittingClassNames.Length == 1)
                    {
                        className = fittingClassNames[0];
                    }
                    else if (fittingClassNames.Length > 1)
                    {
                        string classNameNamespace = className.Remove(className.LastIndexOf('.'));
                        var foundNamespaces = subDataStructure.getUsings().Where(
                                p => p == classNameNamespace
                            ).ToArray().Count();
                        if (foundNamespaces >= 1)
                        {
                            subDataStructure.addImport(className, classNameNamespace);
                        }
                    }
                    else
                    {
                        className = $"{subDataStructure.get_filemodule()}.{className}";
                    }
                } else
                {
                    className = $"{subDataStructure.get_filemodule()}.{className}";
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


        public void append_class(string filename, string filemodule, List<string> usings, string fqdn_class_name, List<string> name_space_list)
        {
            SubDataStructure sub_datastructure = new SubDataStructure(filename, filemodule, usings, fqdn_class_name, name_space_list);
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
            Console.WriteLine($"Requested class {class_name} was not found in the datastructure");
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