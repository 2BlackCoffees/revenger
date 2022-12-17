using static System.Console;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using System.Collections.Generic;
using Microsoft.CodeAnalysis;
using System.Text.RegularExpressions;

using static DotNetPreAdapter.Datastructure;
using System.Reflection;
using System.Text;
using System.Xml.Linq;
using static DotNetPreAdapter.Datastructure.Method;

namespace DotNetPreAdapter
{
    interface IMyTest
    {
        void unused();
    }
    class ASTVisitor : CSharpSyntaxWalker
    {

        // Delete this class !
        class InnerClassBase
        {
            int a = 5;
            public InnerClassBase(int a_)
            {
                int a = a_;
            }
        }
        class InnerClass : InnerClassBase, IMyTest
        {
            int a = 5;
            public InnerClass(int a_) : base(a_)
            {
                int a = a_;
            }

            void IMyTest.unused()
            {
                throw new NotImplementedException();
            }
        }

        static Datastructure unusedD = new Datastructure();



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
        public ASTVisitor(Datastructure datastructure_, string filename_, SemanticModel model_)
        {
            datastructure = datastructure_;
            filename = filename_.Replace("\n", "").Replace("\r", "");
            model = model_;
        }



        public ICollection<UsingDirectiveSyntax> Usings { get; } = new List<UsingDirectiveSyntax>();

        public string? SyntaxNode(SyntaxNode node)
        {
            if (node == null) return "";

            if (node.HasLeadingTrivia)
            {
                var ignoreNode = node.GetLeadingTrivia()
                    .Where(trivia =>
                            trivia.IsKind(SyntaxKind.MultiLineCommentTrivia) ||
                            trivia.IsKind(SyntaxKind.SingleLineCommentTrivia))
                    .Any(trivia => trivia.ToString().TrimStart('/', '*').ToLower().Trim() == "ignore");

                if (ignoreNode) return "";
            }

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
                    return returnValue.Replace("System.Collections.Generic.List", "list")
                        .Replace("System.Collections.Generic.Dictionary", "dict")
                        .Replace("System.Tuple", "tuple")
                        .Replace("List", "list")
                        .Replace("<", "[")
                        .Replace(">", "]")
                        .Replace("?", "");
                   
                }

            }
            return null;
        }
        public override void VisitNamespaceDeclaration(NamespaceDeclarationSyntax node)
        {
            namespaceList.Add(node.Name.GetText().ToString().Replace("\n", "").Replace("\r", ""));
            DefaultVisit(node);
            if (namespaceList.Count > 0) namespaceList.RemoveAt(namespaceList.Count - 1);
        }



        public override void VisitUsingDirective(UsingDirectiveSyntax node)
        {
            //WriteLine($"\tVisitUsingDirective called with {node.Name}.");
            if (node.Name.ToString() != "System" &&
                !node.Name.ToString().StartsWith("System.") &&
                node.Name.ToString() != "Microsoft" &&
                !node.Name.ToString().StartsWith("Microsoft."))
            {
                string name = node.Name.ToString();
                allUsing.Add(name);
            }
            DefaultVisit(node);
        }
        private string GetCurrentClassName()
        {
            if (activeClassnameList.Count > 0) return activeClassnameList[^1];
            return "##NoClass##";
        }

        Tuple<SubDataStructure?, string> CreateClassInterface<T>( T node) where T: TypeDeclarationSyntax
        {
            string filemodule = String.Join(".", namespaceList.ToArray());
            string activeClassName = "";
            if (activeClassnameList.Count > 0) activeClassName = activeClassnameList[^1];

            string? fqdn_class_name = SyntaxNode(node);
            if (fqdn_class_name == null)
            {
                fqdn_class_name = $"{node.Identifier.ValueText}";
                if (filemodule.Length > 0)
                {
                    if (activeClassName.Length > 0) fqdn_class_name = $"{filemodule}.{fqdn_class_name}";
                    else fqdn_class_name = $"{filemodule}.{fqdn_class_name}";
                }

            }

            SubDataStructure? parentSubDataStructure = datastructure.get_datastructures_from_class_name(GetCurrentClassName());
            if (parentSubDataStructure != null)
            {
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
                        if (baseClassName != "Object") subDataStructure.add_base_class(baseClassName);
                    }
                }

                var classSymbol = model.GetDeclaredSymbol(node);
                if (classSymbol != null)
                {
                    var implementedInterfaces = classSymbol.AllInterfaces;
                    foreach (var implementedInterface in implementedInterfaces)
                    {

                        subDataStructure.add_base_class(implementedInterface.Name);
                    }

                }


            }


            if (node.BaseList != null)
            {
                foreach (var annotatedAndToken in node.BaseList.GetAnnotatedNodesAndTokens())
                {
                    Console.WriteLine(annotatedAndToken.ToString());

                }
            }

            return new Tuple<SubDataStructure?, string>(subDataStructure, fqdn_class_name);

        }
        public override void VisitInterfaceDeclaration(InterfaceDeclarationSyntax node)
        {
            var (subDataStructure, fqdn_class_name) = CreateClassInterface(node);
            if(subDataStructure != null) subDataStructure.setInterface();
            activeClassnameList.Add(fqdn_class_name);
            DefaultVisit(node);
            if (activeClassnameList.Count > 0) activeClassnameList.RemoveAt(activeClassnameList.Count - 1);

        }
        public override void VisitClassDeclaration(ClassDeclarationSyntax node)
        {
            var (subDataStructure, fqdn_class_name) = CreateClassInterface(node);
            if (subDataStructure != null) subDataStructure.set_abstract();
            activeClassnameList.Add(fqdn_class_name);
            DefaultVisit(node);
            if (activeClassnameList.Count > 0) activeClassnameList.RemoveAt(activeClassnameList.Count - 1);

        }
        public override void VisitMethodDeclaration(MethodDeclarationSyntax node)
        {
            string methodName = node.Identifier.ValueText;
            activeMethodList.Add(methodName);
            bool hasPublicModifier = node.Modifiers.Any(a => a.Kind() == SyntaxKind.PublicKeyword);

            List<Tuple<string, string>> arguments_tuple = new List<Tuple<string, string>>();
            if (node.ParameterList != null)
            {
                foreach (var parameter in node.ParameterList.Parameters)
                {
                    string parameterType = "";
                    string parameterName = parameter.Identifier.ToFullString();
                    if (parameter != null)
                    {
                        if (parameter.Type != null)
                        {
                            string? tmpType = SyntaxNode(parameter.Type);
                            Console.WriteLine($"VisitMethodDeclaration: {methodName}({tmpType} {parameterName})");
                            parameterType =
                                tmpType != null? tmpType: parameter.Type.ToString();
                        }
                        if (!ignoreType.Contains(parameterType))
                        {
                            arguments_tuple.Add(new Tuple<string, string>(parameterName, parameterType));
                        }
                    }
                }
            }
            SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(GetCurrentClassName());
            if (subDataStructure != null)
            {
                subDataStructure.add_method(methodName, arguments_tuple, !hasPublicModifier);
            }
            DefaultVisit(node);
            if (activeMethodList.Count > 0) activeMethodList.RemoveAt(activeMethodList.Count - 1);


        }
        



        public override void VisitVariableDeclaration(VariableDeclarationSyntax node)
        {
            Console.WriteLine($"VisitDeclarationExpression: {node.ToString()}");
            string? typeName = SyntaxNode(node.Type);
            SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(GetCurrentClassName());
            if (typeName != null && typeName.Length > 0 && subDataStructure != null && !ignoreType.Contains(typeName))
            {
                
                // Special case: Ensure that 'var' isn't actually an alias to another type. (e.g. using var = System.String).
                IAliasSymbol? aliasInfo = model.GetAliasInfo(node.Type);
                if (aliasInfo == null)
                {
                    // Retrieve the type inferred for var.
                    ITypeSymbol? type = model.GetTypeInfo(node.Type).ConvertedType;
                    if (type != null)
                    {
                        //typeName = type.Name;
                    }
                    bool isMember = node.Parent is LocalDeclarationStatementSyntax;
                    for (int i = 0; i < node.Variables.Count; ++i)
                    {
                        string variableName = node.Variables[i].Identifier.Text;
                        if (isMember && type != null && type.IsStatic)
                        {
                            subDataStructure.add_static(variableName, typeName);

                        }
                        else
                        {
                            subDataStructure.add_variable(variableName, typeName, isMember);
                        }
                        Console.WriteLine($"Adding variable type found: {variableName}, type {typeName}, isMember: {isMember}");
                    }
                }
            }
            
            DefaultVisit(node);
        }

    


        public override void VisitInvocationExpression(InvocationExpressionSyntax node)
        {
            SubDataStructure? subDataStructure = datastructure.get_datastructures_from_class_name(GetCurrentClassName());
            if (subDataStructure != null)
            {
                string classUsage = Regex.Replace(node.Expression.ToString(), @"^\s*", "");
                // This is for normal class accesses
                if (classUsage.StartsWith("new "))
                {
                    classUsage = Regex.Replace(Regex.Replace(classUsage, @"\(.*$", ""), @"new\s*", "");
                    subDataStructure.addAnonymousInvocation(classUsage);
                }
                else
                {
                    // Static classes do not have new
                    subDataStructure.addAnonymousStaticInvocation(classUsage);
                }
            }
            DefaultVisit(node);
        }
    }

//    public override void VisitBaseExpression(BaseExpressionSyntax node)

//    public override void VisitTypeArgumentList(TypeArgumentListSyntax node)

//    public override void VisitAliasQualifiedName(AliasQualifiedNameSyntax node)

//    public override void VisitFunctionPointerParameterList(FunctionPointerParameterListSyntax node)

//    public override void VisitTupleType(TupleTypeSyntax node)

//    public override void VisitTupleElement(TupleElementSyntax node)

//    public override void VisitConditionalAccessExpression(ConditionalAccessExpressionSyntax node)

//    public override void VisitConditionalExpression(ConditionalExpressionSyntax node)


//    public override void VisitBaseExpression(BaseExpressionSyntax node)



//    public override void VisitArgumentList(ArgumentListSyntax node)


//                public override void VisitBracketedArgumentList(BracketedArgumentListSyntax node)


//                public override void VisitArgument(ArgumentSyntax node)

//    public override void VisitDeclarationExpression(DeclarationExpressionSyntax node)

//    public override void VisitParenthesizedLambdaExpression(ParenthesizedLambdaExpressionSyntax node)

////    public override void VisitImplicitObjectCreationExpression(ImplicitObjectCreationExpressionSyntax node)

//    public override void VisitObjectCreationExpression(ObjectCreationExpressionSyntax node)

//    public override void VisitAnonymousObjectCreationExpression(AnonymousObjectCreationExpressionSyntax node)

//    public override void VisitArrayCreationExpression(ArrayCreationExpressionSyntax node)

//    public override void VisitImplicitArrayCreationExpression(ImplicitArrayCreationExpressionSyntax node)


//    public override void VisitWhileStatement(WhileStatementSyntax node)

//    public override void VisitDoStatement(DoStatementSyntax node)

//    public override void VisitForStatement(ForStatementSyntax node)

//    public override void VisitForEachStatement(ForEachStatementSyntax node)

//    public override void VisitIfStatement(IfStatementSyntax node)

//    public override void VisitElseClause(ElseClauseSyntax node)

//    public override void VisitSwitchStatement(SwitchStatementSyntax node)

//    public override void VisitAttributeList(AttributeListSyntax node)

//    public override void VisitAttributeTargetSpecifier(AttributeTargetSpecifierSyntax node)

//    public override void VisitAttributeArgumentList(AttributeArgumentListSyntax node)

//    public override void VisitAttributeArgument(AttributeArgumentSyntax node)

//    public override void VisitTypeParameter(TypeParameterSyntax node)

//    public override void VisitStructDeclaration(StructDeclarationSyntax node)

//    public override void VisitInterfaceDeclaration(InterfaceDeclarationSyntax node)

//    public override void VisitEnumDeclaration(EnumDeclarationSyntax node)

//    public override void VisitBaseList(BaseListSyntax node)

//    public override void VisitSimpleBaseType(SimpleBaseTypeSyntax node)

//    public override void VisitFieldDeclaration(FieldDeclarationSyntax node)

//    public override void VisitEventFieldDeclaration(EventFieldDeclarationSyntax node)

}
