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
    List<String> ignoreType = new ArrayList<>(Arrays.asList( "string", "String", "int", "float", "bool", "Boolean", "list[string]",
            "list[int]", "list[bool]", "string[]", "int[]"));
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
        String fqdnParentClassName = deepness.GetFQDNParentClassName(node);

        Datastructure.SubDataStructure parentSubDataStructure =
                datastructure.get_datastructures_from_class_name(fqdnParentClassName);
        if (parentSubDataStructure != null) {
            logger.logDebug(String.format("    CreateClassInterface: %s is an inner class of %s", 
                            fqdnCurrentClassName, 
                            fqdnParentClassName),
                            deepness.getDeepness());
            parentSubDataStructure.add_inner_class(fqdnCurrentClassName);
        }

        datastructure.append_class(filename, fqdnParentClassName, allUsing, fqdnCurrentClassName, namespaceList);
        Datastructure.SubDataStructure subDataStructure = datastructure.get_datastructures_from_class_name(fqdnCurrentClassName);
        final String fqdnCurrentClassNameFinal = fqdnCurrentClassName;
        node.getExtendedTypes().forEach(extendedType -> {
            String extendedTypeStr = SimplifyType(extendedType.asString());
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
/*
    @Override
    public void visit(AnnotationDeclaration n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "AnnotationDeclaration: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(AnnotationMemberDeclaration n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "AnnotationMemberDeclaration: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(MethodCallExpr n, Void arg) {
        logger.logInfo(String.format("Entering MethodCallExpr: %s (%s)", n.getArguments().toString(), n.getScope()),
                deepness.getDeepness() );
        if(n.getTypeArguments().isPresent()) {
            NodeList<Type> arguments = n.getTypeArguments().get();
            logger.logInfo(String.format("  arguments: %s", arguments.toString()), deepness.getDeepness());
            for (Type argument : arguments) {
                String fqdnCurrentTypeName = deepness.GetFQDNCurrentClassName(argument);
                logger.logInfo(String.format("  Argument: %s (%s)", argument, fqdnCurrentTypeName),
                        deepness.getDeepness());
            }
        }
        super.visit(n, arg);
        deepness.decrease();
    }


    @Override
    public void visit(MethodReferenceExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "MethodReferenceExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }
*/
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
            for (var argument : n.getParameters()) {
                String fqdnCurrentTypeName = deepness.GetFQDNCurrentClassName(argument.getType());

                argumentsTuple.add(new Triplet<>(methodName,
                        fqdnCurrentTypeName,
                        fqdnParentClassName));
                logger.logTrace(String.format("  Method: %s, Adding parameter name: %s, type: %s, (%s), mostprobableNS: %s",
                        methodName,
                        argument.getNameAsString(),
                        argument.getTypeAsString(),
                        fqdnCurrentTypeName,
                        fqdnParentClassName));
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
                    String fqdnCurrentClassName = deepness.GetFQDNCurrentClassName(variableDeclarator.getType());
                    subDataStructure.add_variable(
                            variableDeclarator.getNameAsString(),
                            fqdnCurrentClassName,
                            fqdnParentClassName,
                            true);
                    logger.logTrace(String.format("Created ** Member ** variable name: %s, type: %s, ns: %s",
                                                    variableDeclarator.getNameAsString(),
                            fqdnCurrentClassName,
                                    fqdnParentClassName), deepness.getDeepness());
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
        subDataStructure.add_variable(enumValueName, "enumValue", fqdnParentClassName, true);
        super.visit(n, arg);
    }

    @Override
    public void visit(EnumDeclaration n, Void arg) {
        String fqdnCurrentClassName = deepness.GetFQDNCurrentClassName(n);
        String fqdnParentClassName = deepness.GetFQDNParentClassName(n);
        logger.logDebug( String.format("Entering EnumDeclaration %s ", fqdnCurrentClassName));
        logger.logDebug("  EnumDeclaration: Context=" + deepness.getCurrentContext(n), deepness.getDeepness());

        datastructure.append_class(filename, fqdnParentClassName, allUsing, fqdnCurrentClassName, namespaceList);
        deepness.appendClassName(fqdnCurrentClassName);

        super.visit(n, arg);
        deepness.removeLastClassName();
        logger.logDebug("Leaving VisitInterfaceDeclaration", deepness.getDeepness());

    }

    @Override
    public void visit(VariableDeclarator n, Void arg) {
        logger.logDebug( String.format("Entering VariableDeclarator %s ", n.getNameAsString()));

        String fqdnCurrentTypeName = deepness.GetFQDNCurrentClassName(n.getType());
        logger.logDebug("VariableDeclarator: " +  n + ", " +
                n.getNameAsString() + " of type " + fqdnCurrentTypeName + ", " + n.getType() + " init " + n.getInitializer().orElse(null), deepness.getDeepness());

        super.visit(n, arg);

    }


    /*
    @Override
    public void visit(ArrayAccessExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ArrayAccessExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ArrayCreationExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ArrayCreationExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ArrayCreationLevel n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ArrayCreationLevel: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ArrayInitializerExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ArrayInitializerExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ArrayType n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ArrayType: " + (extended ? n : n.getComponentType()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(AssertStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "AssertStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }
*/
    @Override
    public void visit(AssignExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "AssignExpr: " + (extended ? n : n.getTarget() + " = " + n.getValue()));
        super.visit(n, arg);
        deepness.decrease();
    }
/*
    @Override
    public void visit(BinaryExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "BinaryExpr: " + (extended ? n : n.getLeft() + " " + n.getOperator() + " " + n.getRight()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(BlockComment n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "BlockComment: " + (extended ? n : n.getContent()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(BlockStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "BlockStmt: " + (extended ? n : n.getStatements().size() + " statements"));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(BooleanLiteralExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "BooleanLiteralExpr: " + (extended ? n : n.getValue()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(BreakStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "BreakStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(CastExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "CastExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(CatchClause n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "CatchClause: " + (extended ? n : n.getParameter()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(CharLiteralExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "CharLiteralExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }
*/
    @Override
    public void visit(ClassExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ClassExpr: " + (extended ? n : n.getType()));
        super.visit(n, arg);
        deepness.decrease();
    }
/*
    @Override
    public void visit(ClassOrInterfaceType n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ClassOrInterfaceType: " + (extended ? n : n.getNameAsString()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(CompilationUnit n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "CompilationUnit: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ConditionalExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ConditionalExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ConstructorDeclaration n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ConstructorDeclaration: " + (extended ? n : n.getDeclarationAsString()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ContinueStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ContinueStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(DoStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "DoStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(DoubleLiteralExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "DoubleLiteralExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(EmptyStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "EmptyStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(EnclosedExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "EnclosedExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(EnumConstantDeclaration n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "EnumConstantDeclaration: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(EnumDeclaration n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "EnumDeclaration: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ExplicitConstructorInvocationStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ExplicitConstructorInvocationStmt: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ExpressionStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ExpressionStmt: " + (extended ? n : n.getExpression()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(FieldAccessExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "FieldAccessExpr: " + (extended ? n : n.getNameAsString()));
        super.visit(n, arg);
        deepness.decrease();
    }
*/

/*
    @Override
    public void visit(ForEachStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ForEachStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ForStmt n, Void arg) {
        // Collector<CharSequence, ?, String> joiner = Collectors.joining(", ");
        // out.logInfo(deepness.getDeepness() + "ForStmt: "
        // + (extended ? n : n.getInitialization().stream().map(node ->
        // Objects.toString(node)).collect(joiner)) + "; "
        // + n.getCompare()
        // + "; " + n.getUpdate().stream().map(node ->
        // Objects.toString(node)).collect(joiner)
        //
        // );
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(IfStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "IfStmt: " + (extended ? n : n.getCondition()));
        super.visit(n, arg);
        deepness.decrease();
    }



    @Override
    public void visit(InitializerDeclaration n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "InitializerDeclaration: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(InstanceOfExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "InstanceOfExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(IntegerLiteralExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "IntegerLiteralExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(IntersectionType n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "IntersectionType: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(JavadocComment n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "JavadocComment: " + (extended ? n : n.getContent()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(LabeledStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "LabeledStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(LambdaExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "LambdaExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(LineComment n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "LineComment: " + (extended ? n : n.getContent()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(LocalClassDeclarationStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "LocalClassDeclarationStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(LongLiteralExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "LongLiteralExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(MarkerAnnotationExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "MarkerAnnotationExpr: " + (extended ? n : n.getNameAsString()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(MemberValuePair n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "MemberValuePair: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }


    @Override
    public void visit(ModuleDeclaration n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ModuleDeclaration: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ModuleExportsDirective n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ModuleExportsStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ModuleOpensDirective n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ModuleOpensStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ModuleProvidesDirective n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ModuleProvidesStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ModuleRequiresDirective n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ModuleRequiresStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ModuleUsesDirective n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ModuleUsesStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(Name n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "Name: " + (extended ? n : n.getIdentifier()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(NameExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "NameExpr: " + (extended ? n : n.getNameAsString()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(NodeList n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "NodeList: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(NormalAnnotationExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "NormalAnnotationExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(NullLiteralExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "NullLiteralExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ObjectCreationExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ObjectCreationExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }
*/

/*
    @Override
    public void visit(Parameter n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "Parameter: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(PrimitiveType n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "PrimitiveType: " + (extended ? n : n.getType()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ReturnStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ReturnStmt: " + (extended ? n : n.getExpression()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(SimpleName n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "SimpleName: " + (extended ? n : n.getIdentifier()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(SingleMemberAnnotationExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "SingleMemberAnnotationExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(StringLiteralExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "StringLiteralExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(SuperExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "SuperExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(SwitchEntry n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "SwitchEntryStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(SwitchStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "SwitchStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(SynchronizedStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "SynchronizedStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ThisExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ThisExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(ThrowStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "ThrowStmt: " + (extended ? n : n.getExpression()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(TryStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "TryStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(TypeExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "TypeExpr: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(TypeParameter n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "TypeParameter: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(UnaryExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "UnaryExpr: " + (extended ? n : n.getOperator() + " " + n.getExpression()));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(UnionType n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "UnionType: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(UnknownType n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "UnknownType: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(UnparsableStmt n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "UnparsableStmt: " + (extended ? n : ""));
        super.visit(n, arg);
        deepness.decrease();
    }

    @Override
    public void visit(VariableDeclarationExpr n, Void arg) {
        logger.logInfo(deepness.getDeepness() + "VariableDeclarationExpr: " + (extended ? n : n));
        super.visit(n, arg);
        deepness.decrease();
    }
*/
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


    public static void main(String[] args) throws Exception {
        for (String file : args) {
            System.out.println("Opening " + file);
            CompilationUnit cu = new JavaParser().parse(new File(file)).getResult().get();
            new ASTVisitorDebug(System.out, false).visit(cu, null);
            System.out.println();

        }
    }

}