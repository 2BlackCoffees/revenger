package Example;

import Example.SideExample.SideTestEnum;
import org.javatuples.Triplet;
import preadapter.Logger;

import java.util.*;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;
import Example.SideExample.SideExample;
class Useless {
    public void useless() {
        System.out.println("Useless");
        SideTestEnum testEnum = SideTestEnum.TestEnumValue1;
        SideExample.test(testEnum);
        SideExample.testNoParameter();
    }
}
interface IExample {
    public void example(Useless useless1, Useless useless2);
}

abstract class  AbstractBaseExample {
    abstract Useless exampleAbstract(Useless useless1, Useless useless2);

}

class  BaseExample extends AbstractBaseExample {
    @Override
    Useless exampleAbstract(Useless useless1, Useless useless2) {
        return null;
    }

    enum EnumTest {
        EnumValue1,
        EnumValue2
    }

    public void otherExample() {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'example'");
    }

}
public class ClassExample extends BaseExample implements IExample {
    Useless memberVarUseless = new Useless();
    EnumTest memberVarEnumTest = EnumTest.EnumValue1;
    public ClassExample() {
        Useless localVarUseless = new Useless();
        System.out.println(memberVarEnumTest);
        localVarUseless.useless();
        memberVarUseless.useless();
    }

    @Override
    public void example(Useless useless1, Useless useless2) {
        useless1.useless();
        useless2.useless();
        BaseExample localVarBaseExample = new BaseExample();
        localVarBaseExample.otherExample();

    }

    public IExample getExample() {
        return this;
    }

    @Override
    Useless exampleAbstract(Useless useless1, Useless useless2) {
        return null;
    }

    static class InnerClassExample {
        public  InnerClassExample() {
            System.out.println("InnerClassExample");
            class classInMethodExample {
                public classInMethodExample(Useless useless1) {
                    useless1.useless();
                }
            }
        }
        public void methodClassInnerClassExample(Useless useless1) {
            useless1.useless();
        }
    }
    
}
