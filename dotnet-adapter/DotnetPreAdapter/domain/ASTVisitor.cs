using static System.Console;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using System.Collections.Generic;
using Microsoft.CodeAnalysis;
using System.Text.RegularExpressions;

using static DotNetPreAdapter.Domain.Datastructure;
using System.Reflection;
using System.Text;
using System.Xml.Linq;
using static DotNetPreAdapter.Domain.Datastructure.Method;


namespace DotNetPreAdapter
{
    namespace Domain
    {
        class ASTVisitor : CSharpSyntaxWalker
        {

            Datastructure datastructure;
            string filename;
            SemanticModel model;
            List<string> activeMethodList = new();
            List<string> activeClassnameList = new();
            List<string> namespaceList = new();
            List<string> allUsing = new();
            Dictionary<string, string> usingDict = new();
            List<string> ignoreType = new List<string>() {
            "string", "String", "int", "float", "bool", "Boolean", "list[string]",
            "list[int]", "list[bool]", "string[]", "int[]"
        };
            Utils.Logger logger;
            string dbgSpaces = "";
            public ASTVisitor(Datastructure datastructure_, string filename_, SemanticModel model_, Utils.Logger logger_)
            {
                datastructure = datastructure_;
                filename = filename_.Replace("\n", "").Replace("\r", "");
                model = model_;
                logger = logger_;
            }



            public ICollection<UsingDirectiveSyntax> Usings { get; } = new List<UsingDirectiveSyntax>();
            string SimplifyType(string type)
            {
                return type.Replace("System.Collections.Generic.List", "list")
                            .Replace("System.Collections.Generic.Dictionary", "dict")
                            .Replace("System.Tuple", "tuple")
                            .Replace("List", "list")
                            .Replace("<", "[")
                            .Replace(">", "]")
                            .Replace("?", "");
            }
            public string? SyntaxNode(SyntaxNode node)
            {
                if (node == null) return "";

                if (node is BlockSyntax)
                {
                    //Block() takes two arguments, & I don't want to worry about it w/ reflection.
                    return string.Join("", ((BlockSyntax)node).ChildNodes().Select(SyntaxNode));
                }
                ITypeSymbol? convertedType = model.GetTypeInfo(node).ConvertedType;
                if (convertedType != null)
                {
                    string? returnValue = convertedType.ToString();
                    if (returnValue != null)
                    {
                        return SimplifyType(returnValue);
                    }

                }
                return null;
            }
            private string GetCurrentClassName()
            {
                if (activeClassnameList.Count > 0) return activeClassnameList[^1];
                return "##NoClass##";
            }

            Tuple<SubDataStructure?, string> CreateClassInterface<T>(T node) where T : BaseTypeDeclarationSyntax
            {
                logger.LogDebug($"  Entering CreateClassInterface", dbgSpaces);
                string filemodule = String.Join(".", namespaceList.ToArray());
                string activeClassName = "";
                if (activeClassnameList.Count > 0) activeClassName = activeClassnameList[^1];

                string? fqdn_class_name = SyntaxNode(node);
                if (fqdn_class_name == null)
                {
                    fqdn_class_name = $"{node.Identifier.ValueText}";
                    if (filemodule.Length > 0)
                    {
                        if (activeClassName.Length > 0)
                        {
                            fqdn_class_name = $"{activeClassName}.{fqdn_class_name}";
                            logger.LogWarning($"    CreateClassInterface: activeClassName={activeClassName}, " +
                                $"defining fqdn_class_name as {fqdn_class_name} = {{filemodule}}.{{fqdn_class_name}}", dbgSpaces);
                        }
                        else
                        {
                            fqdn_class_name = $"{filemodule}.{fqdn_class_name}";
                            logger.LogWarning($"    CreateClassInterface: activeClassName is empty, defining fqdn_class_name as " +
                                $"{fqdn_class_name} = {{filemodule}}.{{fqdn_class_name}}", dbgSpaces);
                        }
                    }

                }
                else
                {
                    logger.LogDebug($"    CreateClassInterface: fqdn_class_name: {fqdn_class_name} created from SyntaxNode", dbgSpaces);
                }

                SubDataStructure? parentSubDataStructure = datastructure.get_datastructures_from_class_name(GetCurrentClassName());
                if (parentSubDataStructure != null)
                {
                    logger.LogDebug($"    CreateClassInterface: {fqdn_class_name} is an inner class of {GetCurrentClassName()}",
                        dbgSpaces);
                    parentSubDataStructure.add_inner_class(fqdn_class_name);
                }

                datastructure.append_class(filename, filemodule, allUsing, fqdn_class_name, namespaceList);
                SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(fqdn_class_name);
                if (subDataStructure != null)
                {

                    var tmpBase = model.GetDeclaredSymbol(node) as ITypeSymbol;
                    if (tmpBase != null)
                    {
                        var baseType = tmpBase.BaseType;
                        if (baseType != null)
                        {
                            string baseClassName = baseType.Name;
                            if (baseClassName != "Object")
                            {
                                subDataStructure.add_base_class(baseClassName);
                                logger.LogDebug($"    CreateClassInterface: Inherited class: {baseClassName}", dbgSpaces);
                            }
                        }
                    }

                    var classSymbol = model.GetDeclaredSymbol(node);
                    if (classSymbol != null)
                    {
                        var implementedInterfaces = classSymbol.AllInterfaces;
                        foreach (var implementedInterface in implementedInterfaces)
                        {
                            logger.LogDebug($"    CreateClassInterface: ImplementedInterface.Name: {implementedInterface.Name}",
                                dbgSpaces);
                            subDataStructure.add_base_class(implementedInterface.Name);
                        }
                    }
                }
                else
                {
                    logger.LogDebug($"    CreateClassInterface: No enclosing class registered", dbgSpaces);

                }


                if (node.BaseList != null)
                {
                    foreach (var annotatedAndToken in node.BaseList.GetAnnotatedNodesAndTokens())
                    {
                        logger.LogInfo($"    CreateClassInterface: AnnotatedAndToken from BaseList: " +
                            $"{annotatedAndToken.ToString()}", dbgSpaces);

                    }
                }

                return new Tuple<SubDataStructure?, string>(subDataStructure, fqdn_class_name);

            }
            string getCurrentContext()
            {
                return $"ns:<{String.Join(".", namespaceList)}>.clss:<{String.Join(".", activeClassnameList)}>." +
                    $"mthd:<{String.Join(".", activeMethodList)}>";

            }

            string ArgumentsTupleToString(List<Tuple<string, string, string>> arguments_tuple)
            {
                string returnString = "";
                foreach (var element in arguments_tuple)
                {
                    if (returnString.Length > 0) returnString = $"{returnString}, ";
                    if (element.Item3.Length == 0)
                    {
                        returnString += $"{element.Item1}:{element.Item2}";
                    }
                    else
                    {
                        returnString += $"{element.Item1}:({element.Item3}?Probably).{element.Item2}";
                    }
                }
                return returnString;
            }

            string cleanForRegEx(string typeName)
            {
                if (typeName.EndsWith("[]"))
                {
                    typeName = $"list[{typeName}]";
                }
                return typeName;
#if DEACTIVATED_ON_PURPOSE

            string notAllowedChars = "[]{}/\\-()";
            if (notAllowedChars.Any(x => typeName.Contains(x)))
            {
                logger.LogDebug($"{dbgSpaces}  cleanForRegEx: typeName {typeName} contains not allowed chars " +
                    $"{notAllowedChars}", dbgSpaces);
                foreach (char regexChar in notAllowedChars)
                {
                    typeName = typeName.Replace(regexChar.ToString(), $"\\{regexChar}");
                }
                logger.LogDebug($"{dbgSpaces}    cleanForRegEx: typeName was transformed to {typeName}", dbgSpaces);
            }
            return typeName;
#endif
            }

            public override void VisitNamespaceDeclaration(NamespaceDeclarationSyntax node)
            {
                dbgSpaces = "  " + dbgSpaces;
                logger.LogDebug($"Entering VisitNamespaceDeclaration", dbgSpaces);
                logger.LogTrace($"with node:\n{node.ToFullString()}", dbgSpaces);
                string namespaceName = node.Name.GetText().ToString().Replace("\n", "").Replace("\r", "").TrimEnd(' ').TrimStart(' ');
                logger.LogDebug($"    Adding namespace {namespaceName}", dbgSpaces);

                namespaceList.Add(namespaceName);
                DefaultVisit(node);
                if (namespaceList.Count > 0) namespaceList.RemoveAt(namespaceList.Count - 1);
                logger.LogDebug($"Leaving VisitNamespaceDeclaration", dbgSpaces);
                dbgSpaces = dbgSpaces.Substring(2);
            }


            public override void VisitUsingDirective(UsingDirectiveSyntax node)
            {
                dbgSpaces = "  " + dbgSpaces;
                logger.LogDebug($"Entering VisitUsingDirective with node:\n{node.ToFullString()}", dbgSpaces);
                if (node.Name.ToString() != "System" &&
                    !node.Name.ToString().StartsWith("System.") &&
                    node.Name.ToString() != "Microsoft" &&
                    !node.Name.ToString().StartsWith("Microsoft."))
                {
                    string name = node.Name.ToString();
                    logger.LogDebug($"    Adding using {name}", dbgSpaces);
                    allUsing.Add(name);
                }
                DefaultVisit(node);
                logger.LogDebug($"Leaving VisitUsingDirective", dbgSpaces);
                dbgSpaces = dbgSpaces.Substring(2);
            }
            public override void VisitEnumDeclaration(EnumDeclarationSyntax node)
            {
                dbgSpaces = "  " + dbgSpaces;
                logger.LogDebug($"Entering VisitEnumDeclaration with node:\n{node.ToFullString()}", dbgSpaces);
                logger.LogTrace($"with node:\n{node.ToFullString()}", dbgSpaces);
                logger.LogDebug($"  VisitEnumDeclaration: Context={getCurrentContext()}", dbgSpaces);

                var (subDataStructure, fqdn_class_name) = CreateClassInterface(node);
                if (subDataStructure != null) subDataStructure.set_abstract();

                activeClassnameList.Add(fqdn_class_name);
                DefaultVisit(node);

                if (activeClassnameList.Count > 0) activeClassnameList.RemoveAt(activeClassnameList.Count - 1);
                logger.LogDebug($"Leaving VisitClassDeclaration", dbgSpaces);

                dbgSpaces = dbgSpaces.Substring(2);
            }
            public override void VisitInterfaceDeclaration(InterfaceDeclarationSyntax node)
            {
                dbgSpaces = "  " + dbgSpaces;
                logger.LogDebug($"Entering VisitInterfaceDeclaration", dbgSpaces);
                logger.LogTrace($"with node:\n{node.ToFullString()}", dbgSpaces);
                logger.LogDebug($"  VisitInterfaceDeclaration: Context={getCurrentContext()}", dbgSpaces);

                var (subDataStructure, fqdn_class_name) = CreateClassInterface(node);
                if (subDataStructure != null) subDataStructure.setInterface();

                activeClassnameList.Add(fqdn_class_name);
                DefaultVisit(node);

                if (activeClassnameList.Count > 0) activeClassnameList.RemoveAt(activeClassnameList.Count - 1);

                logger.LogDebug($"Leaving VisitInterfaceDeclaration", dbgSpaces);
                dbgSpaces = dbgSpaces.Substring(2);
            }
            public override void VisitClassDeclaration(ClassDeclarationSyntax node)
            {
                dbgSpaces = "  " + dbgSpaces;
                logger.LogDebug($"Entering VisitClassDeclaration", dbgSpaces);
                logger.LogTrace($"with node:\n{node.ToFullString()}", dbgSpaces);
                logger.LogDebug($"  VisitClassDeclaration: Context={getCurrentContext()}", dbgSpaces);

                var (subDataStructure, fqdn_class_name) = CreateClassInterface(node);
                if (subDataStructure != null) subDataStructure.set_abstract();

                activeClassnameList.Add(fqdn_class_name);
                DefaultVisit(node);

                if (activeClassnameList.Count > 0) activeClassnameList.RemoveAt(activeClassnameList.Count - 1);
                logger.LogDebug($"Leaving VisitClassDeclaration", dbgSpaces);

                dbgSpaces = dbgSpaces.Substring(2);
            }

            public override void VisitMethodDeclaration(MethodDeclarationSyntax node)
            {
                dbgSpaces = "  " + dbgSpaces;
                logger.LogDebug($"Entering VisitMethodDeclaration", dbgSpaces);
                logger.LogTrace($"with node:\n{node.ToFullString()}", dbgSpaces);
                logger.LogDebug($"  VisitMethodDeclaration: Context={getCurrentContext()}", dbgSpaces);

                string methodName = node.Identifier.ValueText;
                activeMethodList.Add(methodName);
                bool hasPublicModifier = node.Modifiers.Any(a => a.Kind() == SyntaxKind.PublicKeyword);

                List<Tuple<string, string, string>> arguments_tuple = new List<Tuple<string, string, string>>();
                string mostProbableNamespace = String.Join(".", namespaceList);
                if (node.ParameterList != null)
                {
                    foreach (ParameterSyntax parameter in node.ParameterList.Parameters)
                    {
                        string parameterName = parameter.Identifier.ToFullString();
                        string parameterType = "";
                        IParameterSymbol? parameterSymbol = model.GetDeclaredSymbol(parameter);
                        if (parameterSymbol != null)
                        {
                            parameterType = parameterSymbol.Type.ToDisplayString();
                            logger.LogDebug($"  VisitMethodDeclaration: {methodName} Parameter of {parameterName} " +
                                $"from semantic model: {parameterType}.", dbgSpaces);
                            parameterType = SimplifyType(parameterType);
                            logger.LogDebug($"    VisitMethodDeclaration: Type was simplified to {parameterType}.", dbgSpaces);
                        }
                        else
                        {
                            logger.LogDebug($"  VisitMethodDeclaration: {methodName} Parameter of {parameterName} " +
                                $"could not be extrected from semantic model.", dbgSpaces);
                            if (parameter.Type != null)
                            {
                                string? tmpType = SyntaxNode(parameter.Type);
                                parameterType =
                                    tmpType != null ? tmpType : parameter.Type.ToString();
                                logger.LogDebug($"  VisitMethodDeclaration: {methodName}(parameterName={parameterName}: " +
                                    $"SyntaxNode(parameter.Type)={tmpType}, " +
                                    $"parameter.Type.ToString()={parameter.Type.ToString()})", dbgSpaces);
                            }
                            else
                            {
                                logger.LogDebug($"  VisitMethodDeclaration: {methodName}(parameterName={parameterName}:" +
                                    $" Parameter discarded because type is null ({parameter.ToFullString()}))", dbgSpaces);
                            }
                        }
                        if (!ignoreType.Contains(parameterType))
                        {
                            if (parameterType.Contains("."))
                            {
                                mostProbableNamespace = "";
                            }
                            arguments_tuple.Add(new Tuple<string, string, string>(
                                parameterName, cleanForRegEx(parameterType), mostProbableNamespace));
                            logger.LogDebug($"  VisitMethodDeclaration: Added arguments_tuple: " +
                                $"{ArgumentsTupleToString(arguments_tuple)}", dbgSpaces);
                        }
                        else
                        {
                            logger.LogDebug($"  VisitMethodDeclaration: {methodName}(parameterName={parameterName}: " +
                                $"Parameter discarded because type was discarded)", dbgSpaces);
                        }
                    }

                }
                else
                {
                    logger.LogDebug($"  VisitMethodDeclaration: Method has no parameters", dbgSpaces);
                }
                SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(GetCurrentClassName());
                if (subDataStructure != null)
                {
                    logger.LogDebug($"  VisitMethodDeclaration: Adding method:{methodName}, arguments_tuple:{ArgumentsTupleToString(arguments_tuple)}, hasPublicModifier:{hasPublicModifier}", dbgSpaces);
                    subDataStructure.add_method(methodName, arguments_tuple, !hasPublicModifier);
                }
                else
                {
                    logger.LogDebug($"  VisitMethodDeclaration: Skipping method as I could not find any enclosing class.", dbgSpaces);
                }
                DefaultVisit(node);
                if (activeMethodList.Count > 0) activeMethodList.RemoveAt(activeMethodList.Count - 1);
                logger.LogDebug($"Leaving VisitMethodDeclaration with node {node.ToString()}", dbgSpaces);
                dbgSpaces = dbgSpaces.Substring(2);
            }

            public override void VisitVariableDeclaration(VariableDeclarationSyntax node)
            {
                dbgSpaces = "  " + dbgSpaces;
                logger.LogDebug($"{dbgSpaces}Entering VisitVariableDeclaration with node:\n{node.ToFullString()}", dbgSpaces);
                logger.LogDebug($"{dbgSpaces}  VisitVariableDeclaration: Context={getCurrentContext()}", dbgSpaces);

                string? typeName = SyntaxNode(node.Type);
                SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(GetCurrentClassName());
                logger.LogDebug($"{dbgSpaces}  VisitVariableDeclaration: typeName={typeName}, subDataStructure={subDataStructure}", dbgSpaces);

                if (typeName != null && typeName.Length > 0 && subDataStructure != null && !ignoreType.Contains(typeName))
                {
                    string mostProbableNamespace = String.Join(".", namespaceList);
                    if (typeName.Contains(".")) mostProbableNamespace = "";
                    typeName = cleanForRegEx(typeName);

                    // Special case: Ensure that 'var' isn't actually an alias to another type. (e.g. using var = System.String).
                    IAliasSymbol? aliasInfo = model.GetAliasInfo(node.Type);
                    if (aliasInfo == null)
                    {
                        // Retrieve the type inferred for var.
                        ITypeSymbol? type = model.GetTypeInfo(node.Type).ConvertedType;
                        bool isMember = node.Parent is not LocalDeclarationStatementSyntax;
                        for (int i = 0; i < node.Variables.Count; ++i)
                        {
                            string variableName = node.Variables[i].Identifier.Text;
                            if (isMember && type != null && type.IsStatic)
                            {
                                subDataStructure.add_static(variableName, typeName);
                                logger.LogDebug($"{dbgSpaces}  VisitVariableDeclaration: Adding STATIC variable type found: {variableName}, type {typeName}, isMember: {isMember}", dbgSpaces);
                            }
                            else
                            {
                                bool variableSaved = false;
                                if (activeMethodList.Count > 0)
                                {
                                    Method? method = subDataStructure.GetMethod(activeMethodList[^1]);
                                    if (method != null)
                                    {
                                        method.AddVariable(variableName, typeName, mostProbableNamespace);
                                        variableSaved = true;
                                    }
                                }
                                if (!variableSaved)
                                {
                                    subDataStructure.add_variable(variableName, typeName, mostProbableNamespace, isMember);
                                }
                                logger.LogDebug($"{dbgSpaces}  VisitVariableDeclaration: Adding variable type found: {variableName}, type {typeName}, isMember: {isMember}", dbgSpaces);
                            }
                        }
                    }
                }
                else
                {
                    logger.LogDebug($"{dbgSpaces}  VisitVariableDeclaration: Skipping variable: either typeName is null or enclosing class is not found or type belongs to the types to be skipped.", dbgSpaces);
                }

                DefaultVisit(node);
                logger.LogDebug($"{dbgSpaces}Leaving VisitVariableDeclaration", dbgSpaces);
                dbgSpaces = dbgSpaces.Substring(2);
            }

#if DEACTIVATED_ON_PURPOSE
        ITypeSymbol? getExpressionSymbol(InvocationExpressionSyntax node)
        {
            IMethodSymbol? symbol = model.GetSymbolInfo(node.Expression).Symbol as IMethodSymbol;
            return symbol switch
            {
                ILocalSymbol local      => local.Type,
                IParameterSymbol param  => param.Type,
                IFieldSymbol field      => field.Type,
                IPropertySymbol prop    => prop.Type,
                IMethodSymbol method    => method.MethodKind == MethodKind.Constructor ? method.ReceiverType : method.ReturnType,

                _                       => null
            };

        }

        public override void VisitInvocationExpression(InvocationExpressionSyntax node)
        {
            dbgSpaces = "  " + dbgSpaces;
            logger.LogDebug($"Entering VisitInvocationExpression with node:\n{node.ToFullString()}", dbgSpaces);
            logger.LogDebug($"  VisitInvocationExpression: Context={getCurrentContext()}", dbgSpaces);


             SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(GetCurrentClassName());
            if (subDataStructure != null)
            {
                string classUsage = "";
                ITypeSymbol? symbol = getExpressionSymbol(node);
                if (symbol != null)
                {
                    classUsage = symbol.ToDisplayString();
                }
                else
                {
                    classUsage = Regex.Replace(node.Expression.ToString(), @"^\s*", "");
                }
                // This is for normal class accesses
                if (classUsage.StartsWith("new "))
                {
                    logger.LogDebug($"  VisitInvocationExpression: Analyzing a creation with new: {classUsage}", dbgSpaces);
                    classUsage = Regex.Replace(Regex.Replace(classUsage, @"\(.*$", ""), @"new\s*", "");
                    logger.LogDebug($"  VisitInvocationExpression: After removing new: {classUsage}", dbgSpaces);
                    subDataStructure.addAnonymousInvocation(classUsage);
                }
                else
                {
                    // Static classes do not have new
                    logger.LogDebug($"  VisitInvocationExpression: Adding an anonymous static invocation: {classUsage}", dbgSpaces);
                    subDataStructure.addAnonymousStaticInvocation(classUsage);
                }
            }
            else
            {
                logger.LogDebug($"  VisitInvocationExpression: subDatastructure is null (No enclosing class found)", dbgSpaces);

            }
            DefaultVisit(node);
            logger.LogDebug($"Leaving VisitInvocationExpression", dbgSpaces);
            dbgSpaces = dbgSpaces.Substring(2);
        }
#endif

        }
    }


#if DEACTIVATED_ON_PURPOSE

    public override void VisitBaseExpression(BaseExpressionSyntax node)

        public override void VisitTypeArgumentList(TypeArgumentListSyntax node)

        public override void VisitAliasQualifiedName(AliasQualifiedNameSyntax node)

        public override void VisitFunctionPointerParameterList(FunctionPointerParameterListSyntax node)

        public override void VisitTupleType(TupleTypeSyntax node)

        public override void VisitTupleElement(TupleElementSyntax node)

        public override void VisitConditionalAccessExpression(ConditionalAccessExpressionSyntax node)

        public override void VisitConditionalExpression(ConditionalExpressionSyntax node)


        public override void VisitBaseExpression(BaseExpressionSyntax node)



        public override void VisitArgumentList(ArgumentListSyntax node)


                    public override void VisitBracketedArgumentList(BracketedArgumentListSyntax node)


                    public override void VisitArgument(ArgumentSyntax node)

        public override void VisitDeclarationExpression(DeclarationExpressionSyntax node)

        public override void VisitParenthesizedLambdaExpression(ParenthesizedLambdaExpressionSyntax node)

        public override void VisitImplicitObjectCreationExpression(ImplicitObjectCreationExpressionSyntax node)

        public override void VisitObjectCreationExpression(ObjectCreationExpressionSyntax node)

        public override void VisitAnonymousObjectCreationExpression(AnonymousObjectCreationExpressionSyntax node)

        public override void VisitArrayCreationExpression(ArrayCreationExpressionSyntax node)

        public override void VisitImplicitArrayCreationExpression(ImplicitArrayCreationExpressionSyntax node)


        public override void VisitWhileStatement(WhileStatementSyntax node)

        public override void VisitDoStatement(DoStatementSyntax node)

        public override void VisitForStatement(ForStatementSyntax node)

        public override void VisitForEachStatement(ForEachStatementSyntax node)

        public override void VisitIfStatement(IfStatementSyntax node)

        public override void VisitElseClause(ElseClauseSyntax node)

        public override void VisitSwitchStatement(SwitchStatementSyntax node)

        public override void VisitAttributeList(AttributeListSyntax node)

        public override void VisitAttributeTargetSpecifier(AttributeTargetSpecifierSyntax node)

        public override void VisitAttributeArgumentList(AttributeArgumentListSyntax node)

        public override void VisitAttributeArgument(AttributeArgumentSyntax node)

        public override void VisitTypeParameter(TypeParameterSyntax node)

        public override void VisitStructDeclaration(StructDeclarationSyntax node)

        public override void VisitInterfaceDeclaration(InterfaceDeclarationSyntax node)

        public override void VisitEnumDeclaration(EnumDeclarationSyntax node)

        public override void VisitBaseList(BaseListSyntax node)

        public override void VisitSimpleBaseType(SimpleBaseTypeSyntax node)

        public override void VisitFieldDeclaration(FieldDeclarationSyntax node)

        public override void VisitEventFieldDeclaration(EventFieldDeclarationSyntax node)
# endif
}
