package preadapter.service;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import preadapter.Logger;
import preadapter.domain.ASTVisitorDebug;
import preadapter.domain.Datastructure;
import preadapter.domain.ASTVisitor;
import preadapter.infrastructure.CreateYML;

import java.io.FileNotFoundException;
import java.util.List;
import java.io.File;

public class AnalyzeAST {

    public void SearchRecurseCSharpToYAML(String fromDir, String toDir, Logger logger) {
        Datastructure datastructure = new Datastructure(logger);
        var recurseFileProcess = new RecursiveFileProcessor();
        List<String> listFilePaths = recurseFileProcess.SearchPath(fromDir);
        for (String filePath : listFilePaths) {
            if (filePath.endsWith(".java")) {
                logger.logInfo(String.format("Analyzing %s", filePath));
                CompilationUnit cu;
                try {
                    cu = StaticJavaParser.parse(new File(filePath));
                    new ASTVisitor(datastructure, filePath, logger).visit(cu, null);
                } catch (FileNotFoundException e) {
                    e.printStackTrace();
                }
            }
        }
        datastructure.ResolveClassNames();
        String toFile = toDir + "/output.yml";
        new CreateYML().Create(datastructure, toFile, logger);
        //new Infrastructure.CreateYml().Create(datastructure, toDir, logger);
    }
}