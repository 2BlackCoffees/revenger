#define DEMO_PURPOSE
#if DEMO_PURPOSE
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
        static Utils.Logger logger = new Utils.Logger(Utils.LoggingType.TRACE);
        static Domain.Datastructure unusedD = new Domain.Datastructure(logger);
    }
}

namespace DotNetPreAdapter
{
    namespace RecursiveFileProcessor
    {
        class InnerClass
        {
            int a = 5;
            public InnerClass(int a_)
            {
                int a = a_;
            }
        }
    }
}
#endif
