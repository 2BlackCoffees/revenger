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
        static void removeMe()
        {
            MyNamespace.UnusedClass u1 = new();
            UnusedClass u2 = new();
            MyNamespace.UnusedClass1 u3 = new();
            new MyNamespace.UnusedClass1().doNothing();
            new UnusedClass().doNothing();
        }
        static int Main(string[] args)
        {
            // Test if input arguments were supplied.
            if (args.Length < 4)
            {
                Console.WriteLine("Usage:");
                Console.WriteLine("  --from_dir  <directory-to-extract-C#-files>");
                Console.WriteLine("  --out_dir   <directory-to-store-yml-files>");
                Console.WriteLine("  --trace      Log trace");
                Console.WriteLine("  --debug      Log debug");
                Console.WriteLine("  --info       Log info");
                Console.WriteLine("  --warning    Log warning (Default)");
                Console.WriteLine("  --error      Log error");
                return 1;
            }
            string from_dir = "/Users/jean-philippe.ulpiano/development/py2plantuml/dotnet-solution/dotnet-pre-adapter/dotnet-pre-adapter";
            string to_dir = "/Users/jean-philippe.ulpiano/development/py2plantuml/dotnet-solution/output";

            removeMe();
            Logger logger = new Logger(LoggingType.WARNING);
            for (int index = 0; index < args.Length; ++index)
            {
                if (args[index].Equals("--from_dir"))
                {
                    from_dir = args[index + 1];
                    index++;
                }
                else if (args[index].Equals("--out_dir"))
                {
                    to_dir = args[index + 1];
                    index++;
                }
                else if (args[index].Equals("--trace"))
                {
                    logger = new Logger(LoggingType.TRACE);
                    logger.LogInfo("Setting trace log");
                }
                else if (args[index].Equals("--debug"))
                {
                    logger = new Logger(LoggingType.DEBUG);
                    logger.LogInfo("Setting debug log");
                }
                else if (args[index].Equals("--INFO"))
                {
                    logger = new Logger(LoggingType.INFO);
                    logger.LogInfo("Setting info log");
                }
                else if (args[index].Equals("--warning"))
                {
                    logger = new Logger(LoggingType.WARNING);
                    logger.LogInfo("Setting warning log");
                }
                else if (args[index].Equals("--error"))
                {
                    logger = new Logger(LoggingType.ERROR);
                    Console.WriteLine("Setting ERROR Logs only");
                }
                else
                {
                    logger.LogError($"Option {args[index]} is unknown: Skipped.");
                }
            }



            var ast = new AnalyzeAST();
            ast.SearchRecurseCSharpToYAML(from_dir, to_dir, logger);
            return 0;
        }
    }
}
