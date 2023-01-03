using System;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using System.Text.RegularExpressions;

namespace DotNetPreAdapter
{
	public class AnalyzeAST
	{

        public void SearchRecurseCSharpToYAML(string fromDir, string toDir, Logger logger)
        {
            Datastructure datastructure = new Datastructure();
            var recurseFileProcess = new RecursiveFileProcessor();
            List<string> listFilePaths = recurseFileProcess.SearchPath(fromDir);
            foreach (string filePath in listFilePaths)
            {
                if (filePath.EndsWith(".cs"))
                {
                    logger.LogInfo($"Analyzing {filePath}");
                    string programText = File.ReadAllText(filePath);
                    SyntaxTree tree = CSharpSyntaxTree.ParseText(programText);
                    CompilationUnitSyntax root = tree.GetCompilationUnitRoot();

                    var compilation = CSharpCompilation.Create("HelloWorld")
                        .AddReferences(MetadataReference.CreateFromFile(
                            typeof(string).Assembly.Location)).AddSyntaxTrees(tree);
                    SemanticModel model = compilation.GetSemanticModel(tree);

                    string reducedFilePath = Regex.Replace(filePath.Replace(fromDir, ""), "^[\\s*\\/]*", "");

                    var visitor = new ASTVisitor(datastructure, reducedFilePath, model, logger);
                    visitor.Visit(root);
                }

            }
            //datastructure.ResolveClassNames();
            new CreateYml().Create(datastructure, toDir);

        }
    }
}

