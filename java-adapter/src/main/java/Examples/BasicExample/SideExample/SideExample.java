package Examples.BasicExample.SideExample;

import Examples.BadDesign.DB;

public class SideExample {
    public SideExample() {
        System.out.println("SideExample");
    }

    public static void test(SideTestEnum testEnum) {
        System.out.println("SideExample.test");
    }

    public static void testNoParameter() {
        System.out.println("SideExample.testNoParameter");
    }
}
