using static System.Console;

using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
// dotnet add package RoslynQuoter --version 1.0.1
// dotnet add package YamlDotNet --version 12.2.0
namespace DotNetPreAdapter
{
    class Program
    {
        static int Main(string[] args)
        {
            // Test if input arguments were supplied.
            if (args.Length < 4)
            {
                Console.WriteLine("Usage:");
                Console.WriteLine("  --from_dir <directory-to-extract-C#-files>");
                Console.WriteLine("  --out_dir   <directory-to-store-yml-files>");
                return 1;
            }
            string from_dir = "/Users/jean-philippe.ulpiano/development/py2plantuml/dotnet-solution/dotnet-pre-adapter/dotnet-pre-adapter";
            string to_dir = "/Users/jean-philippe.ulpiano/development/py2plantuml/dotnet-solution/output";

            MyNamespace.UnusedClass u1 = new();
            UnusedClass u2 = new();
            MyNamespace.UnusedClass1 u3 = new();
            new MyNamespace.UnusedClass1().doNothing();
            new UnusedClass().doNothing();

            for (int index = 0; index < args.Length; ++index)
            {
                if (args[index].Equals("--from_dir"))
                {
                    from_dir = args[index + 1];
                    index++;
                }
                if (args[index].Equals("--out_dir"))
                {
                    to_dir = args[index + 1];
                    index++;
                }
            }



            var ast = new AnalyzeAST();
            ast.SearchRecurseCSharpToYAML(from_dir, to_dir);
            return 0;
        }
    }
}
