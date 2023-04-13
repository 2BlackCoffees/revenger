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
        String from_dir = "/Users/jeanphi/Development/revenger/java-adapter/src/main/java/"; //args[0];
        String to_dir = "/Users/jeanphi/Development/revenger/java-adapter/tmp"; // args[1];

        if (args.length < 4) {
            System.out.println("Usage (from_dir and out_dir are mandatory parameters):");
            System.out.println("  --from_dir  <directory-to-extract-C#-files>");
            System.out.println("  --out_dir   <directory-to-store-yml-files>");
            System.out.println("  --trace      Log trace");
            System.out.println("  --debug      Log debug");
            System.out.println("  --info       Log info");
            System.out.println("  --warning    Log warning (Default)");
            System.out.println("  --error      Log error");
            //return;
        }

        Logger logger = new Logger(LoggingType.INFO);

        for (int index = 0; index < args.length; ++index) {
            logger.logInfo("Parsing option: " + args[index]);
            if (args[index].equals("--from_dir")) {
                from_dir = args[index + 1];
                ++index;
                logger.logInfo("Starting from directory: " + from_dir);
            } else if (args[index].equals("--out_dir")) {
                to_dir = args[index + 1];
                ++index;
                logger.logInfo("Generating assets in directory: " + to_dir);
            } else if (args[index].equals("--trace")) {
                logger = new Logger(LoggingType.TRACE);
                logger.logInfo("Setting trace log");
            } else if (args[index].equals("--debug")) {
                logger = new Logger(LoggingType.DEBUG);
                logger.logInfo("Setting debug log");
            } else if (args[index].equals("--INFO")) {
                logger = new Logger(LoggingType.INFO);
                logger.logInfo("Setting info log");
            } else if (args[index].equals("--warning")) {
                logger = new Logger(LoggingType.WARNING);
                logger.logInfo("Setting warning log");
            } else if (args[index].equals("--error")) {
                logger = new Logger(LoggingType.ERROR);
                logger.logInfo("Setting error log");

            } else {
                logger.logWarning("Option " + args[index] + " is unknown: Skipped.");
            }
        }

        var ast = new AnalyzeAST();
        ast.SearchRecurseCSharpToYAML(from_dir, to_dir, logger);

    }
}
