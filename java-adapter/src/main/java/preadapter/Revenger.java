/* 
# In VS Code, use the following command to clean the application:
rm -rf $HOME/Library/Application\ Support/Code/User/workspaceStorage/*

export PATH=$PATH:/opt/homebrew/bin
export JAVA_HOME=$(/usr/libexec/java_home)
export CLASSPATH=$CLASSPATH:$HOME/.m2/repository/com/github/javaparser/javaparser-core/3.25.2/javaparser-core-3.25.2.jar
java -jar /Users/jeanphi/.m2/repository/com/revenger/revenger/0.1.0/revenger-0.1.0-shaded.jar src/main/java /Users/jeanphi/Development/revenger/java-adapter/tmp

mvn install && java -jar /Users/jeanphi/.m2/repository/com/revenger/revenger/0.1.0/revenger-0.1.0-shaded.jar src/main/java/Example/Example.java
*/
package preadapter;

import preadapter.service.AnalyzeAST;

public class Revenger {
    // Create a method to parse a file
    public static void main(String[] args) {
        String from_dir = "/Users/jeanphi/Development/revenger/java-adapter/src/main/java/Example"; //args[0];
        String to_dir = "/Users/jeanphi/Development/revenger/java-adapter/tmp"; // args[1];
        Logger logger = new Logger(LoggingType.TRACE);
        var ast = new AnalyzeAST();
        ast.SearchRecurseCSharpToYAML(from_dir, to_dir, logger);

    }
}
