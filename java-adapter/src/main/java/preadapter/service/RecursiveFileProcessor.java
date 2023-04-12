package preadapter.service;

import java.io.File;
import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class RecursiveFileProcessor
{
    public List<String> SearchPath(String path)
    {
        List<String> fileList = new ArrayList<String>();
        ProcessDirectory(path, fileList);
        return fileList;
    }
    // Process all files in the directory passed in, recurse on any directories
    // that are found, and process the files they contain.
    private void ProcessDirectory(String sourceDirectory, List<String> fileList) {

        try (DirectoryStream<Path> stream = Files
                .newDirectoryStream(Paths.get(sourceDirectory))) {
            for (Path path : stream) {
                boolean isDirectory = Files.isDirectory(path);
                if (!isDirectory && path.toString().endsWith(".java")) {
                    fileList.add(String.valueOf(path.toFile()));
                } else if (isDirectory) {
                    ProcessDirectory(path.toString(), fileList);
                }
            }
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}

