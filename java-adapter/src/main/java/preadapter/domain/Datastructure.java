package preadapter.domain;

import org.javatuples.Triplet;
import preadapter.Logger;

import java.util.*;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;
import java.util.stream.Collectors;

public class Datastructure {
    final String NOT_EXTRACTED = "** Not extracted **";
    final String STATICS = "statics";
    final String METHODS = "methods";
    final String VARIABLES = "variables";
    final String NAMESPACE_FOR_NOT_YET_READFILE = "<not!yet?read}file>";

    public static class Method {
        public class ParameterType
        {
            public String parameter;
            public String userType;
            public String mostProbableNamespace;
            public ParameterType(String parameter_, String userType_, String mostProbableNamespace_)
            {
                parameter = parameter_;
                userType = userType_;
                mostProbableNamespace = mostProbableNamespace_;
            }
        }
        public class Variable
        {
            public String variableName ;
            public String variableType;
            public String mostProbableNamespace;
            public Variable(String variableName_, String variableType_, String mostProbableNamespace_)
            {
                variableName = variableName_;
                variableType = variableType_;
                mostProbableNamespace = mostProbableNamespace_;
            }
        }

        public String methodName;
        public List<Variable> variables;
        public List<ParameterType> parameters;
        public List<ParameterType> getParameters() {
            return parameters;
        }
        public Boolean IsPrivate;

        public Method(String methodName_, List<Triplet<String, String, String>> arguments_tuple_, Boolean IsPrivate_)
        {
            methodName = methodName_;
            List<ParameterType> parameters_ = new ArrayList<ParameterType>();
            for (var Argument : arguments_tuple_) {
                parameters_.add(new ParameterType(Argument.getValue0(), Argument.getValue1(), Argument.getValue2()));
            }

            parameters = new ArrayList<ParameterType>(parameters_);
            IsPrivate = IsPrivate_;
            variables = new ArrayList<Variable>();
        }
        public void AddVariable(String variableName_, String variableType_, String mostProbableNamespace_)
        {
            variables.add(new Variable(variableName_, variableType_, mostProbableNamespace_));
        }

    } // end of class Methods
    public static class Static
    {
        public String StaticName;
        public String StaticType;
        public  Static(String StaticName_, String StaticType_)
        {
            StaticName = StaticName_;
            StaticType = StaticType_;
        }
    }

    public static class Variable
    {
        public String variableName;
        public String variableType;
        public String mostProbableNamespace;
        public boolean IsMember;
        public Variable(String variableName_, String variableType_, String mostProbableNamespace_, boolean IsMember_)
        {
            variableName = variableName_;
            variableType = variableType_;
            mostProbableNamespace = mostProbableNamespace_;
            IsMember = IsMember_;
        }
    }

    public static class SubDataStructure
    {
        String fqdn_class_name;
        String filename;
        List<String> fromImport;
        String filemodule;
        List<String> nameSpaceList;

        List<String> bases = new ArrayList<>();
        List<String> inner_classes = new ArrayList<>();
        List<String> anonymousStaticInvocations = new ArrayList<>();
        List<String> anonymousInvocations = new ArrayList<>();
        List<String> genericTypes = new ArrayList<>();
        Boolean is_abstract_field = false;
        Boolean isInterface = false;
        List<Static> statics = new ArrayList<>();
        List<Variable> variables = new ArrayList<>();
        List<Method> methods = new ArrayList<>();
        boolean isInnerClass = false;

        public SubDataStructure(String filename_, String filemodule_, 
                                List<String> usings_, String fqdn_class_name_, 
                                List<String> nameSpaceList_) {
            fqdn_class_name = fqdn_class_name_;
            filename = filename_;
            fromImport = new ArrayList<String>(usings_);
            filemodule = filemodule_;
            nameSpaceList = new ArrayList<String>(nameSpaceList_);
                
        }

        public void set_abstract()
        {
            is_abstract_field = true;
        }
        public void setInterface()
        {
            isInterface = true;
        }
        public List<String> getFromImports()
        {
            return fromImport;
        }
        public void addGenericType(String genericType)
        {
            genericTypes.add(genericType);
        }
        public void addAnonymousInvocation(String className)
        {
            anonymousInvocations.add(className);
        }
        public void addAnonymousStaticInvocation(String className)
        {
            anonymousStaticInvocations.add(className);
        }
        public void add_base_class(String base_class)
        {
            bases.add(base_class);
        }
        public void add_static(String static_name, String static_type) {
            statics.add(new Static(static_name, static_type));
        }
        public void add_method(String method_name_, List<Triplet<String, String, String>> arguments_tuple_, Boolean is_private_) {
            methods.add(new Method(method_name_, arguments_tuple_, is_private_));
        }
        public Method getMethod(String methodName)
        {
            for (var method : methods)
            {
                if(method.methodName.equals(methodName))
                {
                    return method;
                }
            }
            return null;
        }
        public void add_variable(String variableName, String variableType, String mostProbableNamespace, Boolean is_member) {
            variables.add(new Variable(variableName, variableType, mostProbableNamespace, is_member));
        }
        public void add_inner_class(String inner_class_name) {
            inner_classes.add(inner_class_name);
        }
        public Boolean is_abstract()
        {
            return is_abstract_field;
        }
        public boolean IsInterface()
        {
            return isInterface;
        }
        public boolean isInnerClass()
        {
            return isInnerClass;
        }
        public Boolean has_static_fields()
        {
            return statics.size() > 0;
        }
        public Boolean has_method_fields()
        {
            return methods.size() > 0;
        }
        public Boolean has_variables_fields()
        {
            return variables.size() > 0;
        }

        public List<String> getAnonymousInvocation()
        {
            return anonymousInvocations;
        }
        public List<String> getAnonymousStaticInvocation()
        {
            return anonymousStaticInvocations;
        }
        public List<String> getGenericTypes(){
            return genericTypes;
        }
        public String get_fqdn_class_name(){
            return fqdn_class_name;
        }
        public List<String> get_base_classes()
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
        public List<String> get_inner_class_name()
        {
            return inner_classes;
        }
        public String get_filename()
        {
            return filename;
        }
        public String get_filemodule()
        {
            return filemodule;
        }
        public List<String> get_name_space_list()
        {
            return nameSpaceList;
        }

        public void setInnerClass(boolean isInnerClass_) {
            isInnerClass = isInnerClass_;
        }
    } // end of class SubDataStructure

    Map<String, SubDataStructure> class_to_datastructure = new HashMap<String, SubDataStructure>();
    Map<String, List<SubDataStructure>> namespace_to_datastructures = new HashMap<String, List<SubDataStructure>>();
    Map<String, List<String>> namespace_to_namespace_list = new HashMap<String, List<String>>();
    List<String> skip_types = new ArrayList<String>(Arrays.asList("String", "Boolean", "boolean", "int", "float", "double", "Integer", "byte", "short", "char"));
    Logger logger;
    public Datastructure(Logger logger_)
    {

        skip_types.add(NOT_EXTRACTED);
        logger = logger_;
    }

    public void ResolveClassNames()
    {
        for (SubDataStructure subDataStructure : class_to_datastructure.values()) {
            CorrectClassScope(subDataStructure, subDataStructure.getAnonymousInvocation(), true);
            CorrectClassScope(subDataStructure, subDataStructure.getAnonymousStaticInvocation(), true);
            CorrectClassScope(subDataStructure, subDataStructure.get_base_classes(), false);
            CorrectClassScope(subDataStructure, subDataStructure.getGenericTypes(), false);
            List<Variable> variables = subDataStructure.get_variable_fields();
            for (int index = 0; index < variables.size(); index++) {
                Variable variable = variables.get(index);
                logger.logDebug(String.format("  ResolveClassNames: Variable: name %s, current type: %s, most probable NS: %s.", variable.variableName, variable.variableType, variable.mostProbableNamespace));
                variables.get(index).variableType = GetFQDNForUsedClassName(
                        subDataStructure,
                        variable.variableType,
                        false,
                        variable.mostProbableNamespace);
            }
            for (Method method : subDataStructure.get_method_fields()) {
                for (int index = 0; index < method.parameters.size(); ++index) {
                    logger.logDebug(String.format("  ResolveClassNames: Method: %s Resolving parameter name %s, current type: %s, most probable NS: %s.", method.methodName, method.parameters.get(index).parameter, method.parameters.get(index).userType, method.parameters.get(index).mostProbableNamespace));
                    method.parameters.get(index).userType = GetFQDNForUsedClassName(
                            subDataStructure,
                            method.parameters.get(index).userType,
                            false,
                            method.parameters.get(index).mostProbableNamespace);
                }
                for (int index = 0; index < method.variables.size(); ++index) {
                    logger.logDebug(String.format("  ResolveClassNames: Method: %s Resolving variable name %s, current type: %s, most probable NS: %s.", method.methodName, method.variables.get(index).variableName, method.variables.get(index).variableType, method.variables.get(index).mostProbableNamespace));
                    method.variables.get(index).variableType = GetFQDNForUsedClassName(
                                                subDataStructure,
                                                method.variables.get(index).variableType,
                                                false,
                                                method.variables.get(index).mostProbableNamespace);
                }
            }
        }
    }
    private void CorrectClassScope(SubDataStructure subDataStructure, List<String> classNameList, boolean isAnymousCall)
    {
        if (classNameList != null)
        {
            for (int index = 0; index < classNameList.size(); ++index)
            {
                classNameList.set(index, GetFQDNForUsedClassName(subDataStructure, classNameList.get(index), isAnymousCall, ""));
            }
        }
    }
    public String GetFQDNForUsedClassName(SubDataStructure subDataStructure, String classUsage, boolean isAnonymousCall, String mostProbableNamespace) {
        String className = "";
        if(classUsage.startsWith(NAMESPACE_FOR_NOT_YET_READFILE, 0)) {
            classUsage = classUsage.substring(NAMESPACE_FOR_NOT_YET_READFILE.length());
        }
        if (!isAnonymousCall || Pattern.compile("\\(.*\\)\\s*$", Pattern.CASE_INSENSITIVE).matcher(classUsage).find()) {
            className = isAnonymousCall ? classUsage.split("\\(")[0] : classUsage;
            List<String> classnameList = get_classname_list();
            if (!classnameList.contains(className) || 
                (mostProbableNamespace.length() > 0 && !classnameList.contains(mostProbableNamespace + "." + className))) {
                try {
                    final String finalClassName = className;
                    List<String> fittingClassNames = classnameList.stream()
                            .filter(p -> Pattern.compile("\\." + finalClassName + "$").matcher(p).find())
                            .collect(Collectors.toList());
                    if (fittingClassNames.size() == 1) {
                        logger.logDebug("GetFQDNForUsedClassName: Found class " + className + " as " + fittingClassNames.get(0));
                        className = fittingClassNames.get(0);
                    } else if (fittingClassNames.size() > 1) {
                        logger.logDebug("GetFQDNForUsedClassName: Found class " + className + " with multiple better fitting variants: " + String.join(", ", fittingClassNames));
                        // First check if we find one option as imported class
                        List<String> classNameFromImports = subDataStructure.getFromImports().stream()
                            .filter(currentImportName -> fittingClassNames.contains(currentImportName))
                            .collect(Collectors.toList());
                        if(classNameFromImports.size() == 1) {
                            logger.logDebug("GetFQDNForUsedClassName: Found class " + classNameFromImports.get(0) + " in the import list: " + String.join(", ", classNameFromImports));
                            className = classNameFromImports.get(0);
                        } else {
                            List<String> classNameEndingInPackageImport = classNameFromImports.stream()
                                .filter(currentImportName -> currentImportName.endsWith("." + finalClassName))
                                .collect(Collectors.toList());    
                            logger.logDebug("GetFQDNForUsedClassName: classNameEndingInPackageImport: " + String.join(", ", classNameEndingInPackageImport));
                            String fqdnClassName = mostProbableNamespace + "." + finalClassName;
                            if(classNameEndingInPackageImport.size() == 1) {
                                className = classNameEndingInPackageImport.get(0);
                                logger.logDebug("GetFQDNForUsedClassName: Only class found in classNameEndingInPackageImport is " + className);
                            } else if(classNameEndingInPackageImport.size() > 1 && classNameEndingInPackageImport.contains(fqdnClassName)) {
                                className = fqdnClassName;
                                logger.logDebug("GetFQDNForUsedClassName: Filtered class out using mostProbableNamespace = " + mostProbableNamespace + " to " + className);
                            } else {
                                // Take the multi import
                                List<String> fqdnFromPackageImport = classNameFromImports.stream()
                                        .filter(p -> Pattern.compile("\\*\\s*$").matcher(p).find())
                                        .map(classNameFromImport -> {
                                            return classNameFromImport.replaceFirst("\\*\\s*$", "") + finalClassName;
                                        })
                                        .collect(Collectors.toList());
                                
                                List<String> bestFittingClassNames = classnameList.stream()
                                        .filter(currentClassName -> fqdnFromPackageImport.contains(currentClassName))
                                        .collect(Collectors.toList());
                                
                                if (bestFittingClassNames.size() == 1) {
                                    className = bestFittingClassNames.get(0);
                                    logger.logDebug("GetFQDNForUsedClassName: Found class " + className + " from bestFittingClassNames: " + String.join(", ", bestFittingClassNames));

                                } else if (bestFittingClassNames.size() > 1) {
                                    if(bestFittingClassNames.contains(fqdnClassName)) {
                                        className = fqdnClassName;
                                        logger.logDebug("GetFQDNForUsedClassName: Found class " + className + " with multiple better fitting variants: " + String.join(", ", bestFittingClassNames));
                                    } else {
                                        className = NAMESPACE_FOR_NOT_YET_READFILE + className;
                                        logger.logWarning("GetFQDNForUsedClassName: the file defining the class might not have been read yet, using temporary namespace:" + className );

                                    }
                                } else {
                                    className = NAMESPACE_FOR_NOT_YET_READFILE + className;
                                    logger.logWarning("GetFQDNForUsedClassName: the file defining the class might not have been read yet, using temporary namespace:" + className );
                                }
                            }
                        }
                    } else {
                        logger.logWarning("GetFQDNForUsedClassName: Class " + className + " not found in the whole list of classes! Class will be left as is.");
                    }
                } catch (PatternSyntaxException e) {
                    logger.logError("GetFQDNForUsedClassName: Class " + className + " could not be regex parsed (Class will be left as is):\n" + e.toString());
                }
            } else {
                logger.logDebug("GetFQDNForUsedClassName: OK: Class " + className + " found in the list of classes! Class will be left as is.");
            }
        }
        return className;
    }

    public List<String> get_skip_types()
    {
        return skip_types;
    }

    void append_sub_datastructure(SubDataStructure sub_datastructure)
    {
        String fqdn_class_name = sub_datastructure.get_fqdn_class_name();
        if (!class_to_datastructure.containsKey(fqdn_class_name))
        {
            class_to_datastructure.put(fqdn_class_name, sub_datastructure);
            String namespace_name = String.join(".", sub_datastructure.get_name_space_list());
            if (!namespace_to_datastructures.containsKey(namespace_name))
            {
                namespace_to_datastructures.put(namespace_name, new ArrayList<SubDataStructure>());
            }
            namespace_to_datastructures.get(namespace_name).add(sub_datastructure);
            namespace_to_namespace_list.put(namespace_name, sub_datastructure.get_name_space_list());
        }
        else
        {
            System.out.println("WARNING: Class " + fqdn_class_name +" is being registered a second time \n" +
              "   -> First time content is from file " + 
              class_to_datastructure.get(fqdn_class_name).get_filename() +
              ", from class: " + class_to_datastructure.get(fqdn_class_name).get_fqdn_class_name() + ": Ignoring.");
        }
    }
    public SubDataStructure append_class(String filename, String filemodule, List<String> usings, String fqdn_class_name, List<String> nameSpaceList) {
        SubDataStructure sub_datastructure = new SubDataStructure(filename, filemodule, usings, fqdn_class_name, nameSpaceList);
        append_sub_datastructure(sub_datastructure);
        return sub_datastructure;
    }

    public List<String> get_classname_list() {
        return new ArrayList<String>(class_to_datastructure.keySet());
    }

    public SubDataStructure get_datastructures_from_class_name(String class_name) {
        if (class_to_datastructure.containsKey(class_name)) {
            return class_to_datastructure.get(class_name);
        }
        logger.logWarning("Requested class "+ class_name + " was not found in the datastructure");
        return null;
    }

}
