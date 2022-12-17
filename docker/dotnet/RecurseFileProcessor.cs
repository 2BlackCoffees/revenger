// For Directory.GetFiles and Directory.GetDirectories
// For File.Exists, Directory.Exists
using System;
using System.IO;
using System.Collections;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
namespace DotNetPreAdapter
{
    public class RecursiveFileProcessor
    {
        class InnerClass
        {
            int a = 5;
            public InnerClass(int a_)
            {
                int a = a_;
            }
        }
        public List<string> SearchPath(string path)
        {
            List<string> fileList = new List<string>();
            ProcessDirectory(path, fileList);
            return fileList;

        }

        // Process all files in the directory passed in, recurse on any directories
        // that are found, and process the files they contain.
        private void ProcessDirectory(string targetDirectory, List<string> fileList)
        {
            // Process the list of files found in the directory.
            string[] fileEntries = Directory.GetFiles(targetDirectory);
            foreach (string fileName in fileEntries)
            {
                fileList.Add(fileName);

            }

            // Recurse into subdirectories of this directory.
            string[] subdirectoryEntries = Directory.GetDirectories(targetDirectory);
            foreach (string subdirectory in subdirectoryEntries)
            {
                ProcessDirectory(subdirectory, fileList);
            }
        }

        // Insert logic for processing found files here.
        public void ProcessFile(string path)
        {
            Console.WriteLine("ProcessFile: Deactivated method!");
            /*
            string readText = File.ReadAllText(path);
            SyntaxTree tree = CSharpSyntaxTree.ParseText(path);
            CompilationUnitSyntax root = tree.GetCompilationUnitRoot();
            // </Snippet2>

            // <Snippet6>
            var collector = new UsingCollector();
            collector.Visit(root);
            foreach (var directive in collector.Usings)
            {
                //Console.WriteLine(directive.Name);
            }
            */

        }
    }
}