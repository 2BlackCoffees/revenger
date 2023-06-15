package preadapter.domain;

import java.io.File;
import java.util.*;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.*;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.ClassExpr;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.MethodReferenceExpr;
import com.github.javaparser.ast.stmt.WhileStmt;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.type.Type;
import com.github.javaparser.ast.type.VoidType;
import com.github.javaparser.ast.type.WildcardType;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import org.javatuples.Triplet;
import preadapter.Logger;

/**
 * This is a little hand cranked, perhaps hacked together util to take a Java
 * file and dump a trace of where the visitor goes. Helpful for debugging and
 * getting an idea on how to manipulate the AST.
 */
public class ASTVisitor extends VoidVisitorAdapter<Void> {

    private Logger logger = null;
    private boolean extended = true;
    Datastructure datastructure;
    String filename;
    List<String> activeMethodList = new ArrayList<>();
    List<String> activeClassnameList = new ArrayList<>();
    List<String> namespaceList = new ArrayList<>();
    List<String> allUsing = new ArrayList<>();
    Map<String, String> usingDict = new HashMap<>();
    private final HandleDeepness deepness = new HandleDeepness(namespaceList, activeClassnameList, activeMethodList);
    List<String> ignoreType = new ArrayList<>(Arrays.asList("String", "int", "Integer", "float", "boolean", "Boolean", "list[string]",
            "list[int]", "list[bool]", "String[]", "int[]"));
    private String NO_CLASS_FOUND = "##NoClass##";

    public ASTVisitor(Datastructure datastructure, String filename, Logger logger)
    {
        super();
        this.datastructure = datastructure;
        this.filename = filename.replace("\n", "").replace("\r", "");
        this.logger = logger;
    }

    public String SimplifyType(String type)
    {
        return type.replace("List", "list")
                .replace("Map", "dict")
                .replace("HashMap", "dict")
                .replace("TreeMap", "dict")
                .replace("Tuple", "tuple")
                .replace("Pair", "tuple")
                .replace("Triplet", "tuple")
                .replace("List", "list")
                .replace("ArrayList", "list")
                .replace("<", "[")
                .replace(">", "]");
    }

    String CreateClassInterface(ClassOrInterfaceDeclaration node)
    {
        String fqdnCurrentClassName = deepness.GetFQDNCurrentClassName(node);
        final String fqdnParentClassName = deepness.GetFQDNParentClassName(node);

        Datastructure.SubDataStructure parentSubDataStructure =
                datastructure.get_datastructures_from_class_name(fqdnParentClassName);
        if (parentSubDataStructure != null) {
            logger.logDebug(String.format("    CreateClassInterface: %s is an inner class of %s", 
                            fqdnCurrentClassName, 
                            fqdnParentClassName),
                            deepness.getDeepness());
            parentSubDataStructure.add_inner_class(fqdnCurrentClassName);
        }
        final Datastructure.SubDataStructure subDataStructure =
                datastructure.append_class(filename, deepness.getCurrentNamespace(),
                        allUsing, fqdnCurrentClassName, namespaceList);
        subDataStructure.setInnerClass(parentSubDataStructure != null);

        final String fqdnCurrentClassNameFinal = fqdnCurrentClassName;
        node.getExtendedTypes().forEach(extendedType -> {
            String extendedTypeStr = datastructure.GetFQDNForUsedClassName(
                subDataStructure, extendedType.asString(), 
                false, fqdnParentClassName);
            
            if (extendedTypeStr != null && extendedTypeStr.length() > 0) {
                    logger.logDebug(String.format("    Class %s inherits from %s", fqdnCurrentClassNameFinal, extendedTypeStr),
                            deepness.getDeepness());
                    subDataStructure.add_base_class(extendedTypeStr);
            }
        });
        if(subDataStructure.get_base_classes().size() == 0) {
            logger.logDebug(String.format("    Class %s is a top level class", fqdnCurrentClassName),
                    deepness.getDeepness());
        }

        if(node.isInterface()) {
            subDataStructure.setInterface();
            logger.logDebug(String.format("    Class %s is an interface", fqdnParentClassName),
                    deepness.getDeepness());
        }

        if(node.isAbstract()) {
            subDataStructure.set_abstract();
            logger.logDebug(String.format("    Class %s is an abstract class", fqdnParentClassName),
                    deepness.getDeepness());
        }

        return  fqdnCurrentClassName;
    }

    enum ObjectType {
        CLASS,
        METHOD,
        NONE
    }
    class HandleDeepness {
        private final List<String> activeClassnameList;
        private final List<String> namespaceList;
        private final List<String> activeMethodList;
        private final List<ObjectType> listObjectType = new ArrayList<>();
        int deepness = 0;
        String fqdn = "";

        HandleDeepness(List<String> activeClassnameList, List<String> namespaceList, List<String> activeMethodList) {
            this.activeClassnameList = activeClassnameList;
            this.namespaceList = namespaceList;
            this.activeMethodList = activeMethodList;

        }
        public String getCurrentNamespace() {
            return String.join(".", namespaceList);
        }
        private String getCurrentNamespaceWithClasses(Node node) {
            String currentNS = getCurrentNamespace();
            List<String> classList = new ArrayList<>();
            while (node != null) {
                String nameClass = null;
                if (node instanceof ClassOrInterfaceDeclaration ||
                        node instanceof EnumDeclaration) {
                    nameClass = ((TypeDeclaration<?>) node).getNameAsString();
                } else if(node instanceof ClassOrInterfaceType) {
                    nameClass = ((ClassOrInterfaceType) node).getNameAsString();
                }
                if(nameClass != null) {
                    classList.add(nameClass);
                }
                node = node.getParentNode().orElse(null);
            }
            Collections.reverse(classList);
            if (classList.size() > 0) {
                String currentClassList = String.join(".", classList);
                if (currentNS.length() > 0) {
                    return currentNS + "." + currentClassList;
                }
                return currentClassList;
            }
            return currentNS;
        }

        ObjectType getCurrentActiveObjectType() {
            if(listObjectType.size() > 0) {
                return listObjectType.get(listObjectType.size() - 1);
            }
            return ObjectType.NONE;
        }
        String GetFQDNParentClassName(Node node)
        {
            if(node.hasParentNode() && node.getParentNode().isPresent()) {
                return getCurrentNamespaceWithClasses(node.getParentNode().get());
            }
            return NO_CLASS_FOUND;
        }
        String GetFQDNCurrentClassName(Node node)
        {
            return getCurrentNamespaceWithClasses(node);
        }
        private String GetCurrentMethodName()
        {
            if (activeMethodList.size() > 0) return activeMethodList.get(activeMethodList.size() - 1);
            return "##NoMethod##";
        }
        String getCurrentContext(Node node) {
            return GetFQDNCurrentClassName(node);
                    /*"ns:<" + getCurrentNamespace() + ">.clss:<" + String.join(".", activeClassnameList) + ">." +
                    "mthd:<" + String.join(".", activeMethodList) + ">";*/

        }
        private void increase() {
            deepness++;
        }

        private void appendObjectName(String objectName) {
            increase();
            if(this.fqdn.isBlank()) {
                this.fqdn = objectName;
            } else {
                this.fqdn = this.fqdn + "." + objectName;
            }
        }

        void appendPackageName(String packageName) {
            appendObjectName("ns:" + packageName);
            namespaceList.add(packageName);
        }

        void appendClassName(String className) {
            appendObjectName("class:" + className);
            activeClassnameList.add(className);
            listObjectType.add(ObjectType.CLASS);
        }

        void appendMethodName(String methodName) {
            appendObjectName("method:" + methodName);
            activeMethodList.add(methodName);
            listObjectType.add(ObjectType.METHOD);
        }

        private void removeLastObject() {
            decrease();
            if(this.fqdn.contains(".")) {
                this.fqdn = this.fqdn.substring(0, this.fqdn.lastIndexOf("."));
            } else {
                this.fqdn = "";
            }
            if (listObjectType.size() > 0) {
                listObjectType.remove(listObjectType.size() - 1);
            }
        }
        void removeLastClassName() {
            removeLastObject();
            activeClassnameList.remove(activeClassnameList.size() - 1);
        }


        void removeLastMethodName() {
            removeLastObject();
            activeMethodList.remove(activeMethodList.size() - 1);
        }
        public void decrease() {
            if(deepness > 0) deepness--;
        }

        public String getDeepness() {
            return " ".repeat(deepness);
        }
    }

    private void addArgumentType(String methodName, String fqdnParentClassName, Type parameterType, String parameterName,
                                 List<Triplet<String, String, String>> argumentsTuple) {
        String argumentTypeString = SimplifyType(parameterType.getElementType().asString());

        String mostProbableNS = argumentTypeString.contains(".") ?
                "" :
                deepness.getCurrentNamespace();

        argumentsTuple.add(new Triplet<>(parameterName,
                argumentTypeString,
                mostProbableNS)
        );
        logger.logTrace(String.format("  Method: %s, Adding parameter name: %s, type: %s, (Most probable NS: %s), fqdnParentClassName: %s",
                methodName,
                parameterName,
                argumentTypeString,
                mostProbableNS,
                fqdnParentClassName));
    }
    @Override
    public void visit(MethodDeclaration n, Void arg) {
        String methodName = n.getNameAsString();
        String fqdnParentClassName = deepness.GetFQDNParentClassName(n);
        logger.logDebug(String.format("Entering MethodDeclaration: %s (%s)",
                     n.getDeclarationAsString(), methodName),
                deepness.getDeepness());
        deepness.appendMethodName(methodName);
        Datastructure.SubDataStructure subDataStructure =
                datastructure.get_datastructures_from_class_name(fqdnParentClassName);
        if(subDataStructure != null) {
            List<Triplet<String, String, String>> argumentsTuple = new ArrayList<>();
            addArgumentType(methodName, fqdnParentClassName, n.getType(), "!_return_value_!", argumentsTuple);

            for (var argument : n.getParameters()) {
                addArgumentType(methodName, fqdnParentClassName, argument.getType(), argument.getNameAsString(), argumentsTuple);

            }
            subDataStructure.add_method(methodName,
                                        argumentsTuple,
                                        n.isPrivate());
        }

        super.visit(n, arg);
        deepness.removeLastMethodName();
    }


    @Override
    public void visit(ClassOrInterfaceDeclaration n, Void arg) {
        logger.logDebug("Entering VisitInterfaceDeclaration", deepness.getDeepness());
        logger.logTrace("with node:" + n.getNameAsString(), deepness.getDeepness() + "  ");
        logger.logDebug("  VisitInterfaceDeclaration: Context=" + deepness.getCurrentContext(n), deepness.getDeepness());

        String className = CreateClassInterface(n);
        deepness.appendClassName(className);

        super.visit(n, arg);
        deepness.removeLastClassName();
        logger.logDebug("Leaving VisitInterfaceDeclaration", deepness.getDeepness());

    }
    @Override
    public void visit(FieldDeclaration n, Void arg) {
        logger.logDebug( String.format("Entering FieldDeclaration %s ", n.getVariables()));
        logger.logDebug("  FieldDeclaration: Context=" + deepness.getCurrentContext(n), deepness.getDeepness());

        String fqdnParentClassName = deepness.GetFQDNParentClassName(n);
        if(deepness.getCurrentActiveObjectType() == ObjectType.CLASS) {
            Datastructure.SubDataStructure subDataStructure =
                    datastructure.get_datastructures_from_class_name(fqdnParentClassName);
            if(subDataStructure != null) {
                for (VariableDeclarator variableDeclarator : n.getVariables()) {
                    String argumentTypeString = SimplifyType(variableDeclarator.getTypeAsString());
                    if(!ignoreType.contains(argumentTypeString)) {

                        String mostProbableNS = argumentTypeString.contains(".") ?
                                "" :
                                deepness.getCurrentNamespace();

                        subDataStructure.add_variable(
                                variableDeclarator.getNameAsString(),
                                argumentTypeString,
                                mostProbableNS,
                                true);
                        logger.logTrace(String.format("Created ** Member ** variable name: %s, type: %s, mostProbableNS: %s, fqdnParentClassName: %s",
                                        variableDeclarator.getNameAsString(),
                                        argumentTypeString,
                                        mostProbableNS,
                                        fqdnParentClassName),
                                deepness.getDeepness());
                    }
                }
            } else {
                logger.logError("Could not find class " + fqdnParentClassName + " in datastructure");
            }

        }
        super.visit(n, arg);
    }
    @Override
    public void visit(PackageDeclaration n, Void arg) {
        logger.logDebug( String.format("Entering PackageDeclaration %s ", n.getNameAsString()));
        deepness.appendPackageName(n.getNameAsString());
        super.visit(n, arg);
    }
    @Override
    public void visit(ImportDeclaration n, Void arg) {
        String importName = n.getNameAsString();
        logger.logDebug( String.format("Entering ImportDeclaration %s ", importName));
        if(!importName.startsWith("java.") && !importName.startsWith("org.")) {
            allUsing.add(importName);
        }

        super.visit(n, arg);
    }

    public void visit(EnumConstantDeclaration n, Void arg) {
        String enumValueName = n.getNameAsString();
        logger.logDebug( String.format("Entering EnumConstantDeclaration %s ", enumValueName));
        logger.logDebug("  EnumConstantDeclaration: Context=" + deepness.getCurrentContext(n), deepness.getDeepness());

        String fqdnParentClassName = deepness.GetFQDNParentClassName(n);
        Datastructure.SubDataStructure subDataStructure =
                datastructure.get_datastructures_from_class_name(fqdnParentClassName);
        if(subDataStructure != null) {
            subDataStructure.add_variable(enumValueName, "EnumTypePlaceHolder", fqdnParentClassName, true);
            logger.logDebug(String.format("  EnumConstantDeclaration: Created enumValue %s for enum type %s", enumValueName, fqdnParentClassName), deepness.getDeepness());
        } else {
            logger.logWarning(String.format("  EnumConstantDeclaration: Could not create enumValue %s because " +
                    "parent enum type %s could not be found.", enumValueName, fqdnParentClassName), deepness.getDeepness());
        }
        super.visit(n, arg);
    }

    @Override
    public void visit(EnumDeclaration n, Void arg) {
        String fqdnCurrentClassName = deepness.GetFQDNCurrentClassName(n);
        String fqdnParentClassName = deepness.GetFQDNParentClassName(n);
        logger.logDebug( String.format("Entering EnumDeclaration %s ", fqdnCurrentClassName));
        logger.logDebug("  EnumDeclaration: Context=" + deepness.getCurrentContext(n), deepness.getDeepness());
        Datastructure.SubDataStructure subDataStructureParent =
                datastructure.get_datastructures_from_class_name(fqdnParentClassName);
        if(subDataStructureParent != null)
        {
            subDataStructureParent.add_inner_class(fqdnCurrentClassName);
        }
        Datastructure.SubDataStructure subDataStructureChild =
                datastructure.append_class(filename, deepness.getCurrentNamespace(), allUsing,
                        fqdnCurrentClassName, namespaceList);
        subDataStructureChild.setInnerClass(subDataStructureParent != null);

        deepness.appendClassName(fqdnCurrentClassName);

        super.visit(n, arg);
        deepness.removeLastClassName();
        logger.logDebug("Leaving VisitInterfaceDeclaration", deepness.getDeepness());

    }

    @Override
    public void visit(VariableDeclarator n, Void arg) {
        logger.logDebug( String.format("Entering VariableDeclarator %s ", n.getNameAsString()), deepness.getDeepness());
        String fqdnParentClassName = deepness.GetFQDNParentClassName(n);
        Datastructure.SubDataStructure subDataStructureParent =
                datastructure.get_datastructures_from_class_name(fqdnParentClassName);
        if(subDataStructureParent != null) {
            var variableName = n.getNameAsString();
            var variableType = n.getTypeAsString();
            var initializer = n.getInitializer().toString();
            logger.logTrace( String.format("  Before processing: Variable name: %s, variableType: %s, initializer: %s ", variableName, variableType, initializer), deepness.getDeepness());
            if(variableType.equals("var")) {
                variableType = initializer;
            }
            if (variableType.contains("new ")) {
                variableType = variableType.replace("new ", "").trim();
            }
            if (variableType.startsWith("Optional[")) {
                variableType = variableType.replace("Optional[", "");
                variableType = variableType.substring(0, variableType.length() - 1).trim();
            }

            logger.logTrace( String.format("  After processing: Variable name: %s, variableType: %s", variableName, variableType), deepness.getDeepness());

            if (variableType.length() > 0) {
                variableType = SimplifyType(variableType);

                if(variableType.matches("^[\\w\\[\\]]+$")) {

                    String methodName = deepness.GetCurrentMethodName();
                    Datastructure.Method method = subDataStructureParent.getMethod(methodName);
                    if (method != null) {
                        method.AddVariable(variableName, variableType, deepness.getCurrentNamespace());
                    } else {
                        logger.logTrace("  Could not find method " + methodName + " in class " + fqdnParentClassName, deepness.getDeepness());
                    }
                }

            }
        }


        super.visit(n, arg);

    }


/* 
    @Override
    public void visit(AssignExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "AssignExpr: " + (extended ? n : n.getTarget() + " = " + n.getValue()));
        super.visit(n, arg);
        deepness.decrease();
    }
    @Override
    public void visit(ClassExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ClassExpr: " + (extended ? n : n.getType()));
        super.visit(n, arg);
        deepness.decrease();
    }
    @Override
    public void visit(VoidType n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "VoidType: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(WhileStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "WhileStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(WildcardType n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "WildcardType: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }
*/

    public static void main(String[] args) throws Exception {
        for (String file : args) {
            System.out.println("Opening " + file);
            CompilationUnit cu = new JavaParser().parse(new File(file)).getResult().get();
            new ASTVisitorDebug(System.out, false).visit(cu, null);
            System.out.println();

        }
    }

}