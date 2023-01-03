using System;
using Microsoft.CodeAnalysis.CSharp;

namespace MyNamespace
{
    public class UnusedClass
    {
        public UnusedClass()
        {
        }
    }
    public class UnusedClass1
    {
        public UnusedClass1()
        {
        }
        public void doNothing()
        {

        }
    }
}

namespace DotNetPreAdapter
{
    interface IMyTest
    {
        void unused();
    }
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
    class UnusedASTVisitor : CSharpSyntaxWalker
    {
        static Logger logger = new Logger(LoggingType.TRACE);
        static Datastructure unusedD = new Datastructure(logger);
    }
}

