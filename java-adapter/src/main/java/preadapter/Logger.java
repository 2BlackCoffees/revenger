package  preadapter;

import java.util.Arrays;

public class Logger {
    private LoggingType loggingType;

    public Logger(LoggingType loggingType) {
        this.loggingType = loggingType;
    }

    private void log(String logType, String text, String startText) {
        String[] result = text.split("\\r?\\n");
        Arrays.stream(result).forEach(s -> System.out.println(logType + ": " + startText + s));
    }

    public void logError(String text, String startText) {
        if (loggingType.getValue() <= LoggingType.ERROR.getValue()) {
            log("ERROR (Java)", text, startText);
        }
    }
    public void logError(String text) {
        logTrace(text, "");
    }

    public void logWarning(String text, String startText) {
        if (loggingType.getValue() <= LoggingType.WARNING.getValue()) {
            log("WARN (Java)", text, startText);
        }
    }
    public void logWarning(String text) {
        logTrace(text, "");
    }

    public void logInfo(String text, String startText) {
        if (loggingType.getValue() <= LoggingType.INFO.getValue()) {
            log("INFO (Java)", text, startText);
        }
    }
    public void logInfo(String text) {
        logInfo(text, "");
    }

    public void logDebug(String text, String startText) {
        if (loggingType.getValue() <= LoggingType.DEBUG.getValue()) {
            log("DEBUG (Java)", text, startText);
        }
    }
    public void logDebug(String text) {
        logTrace(text, "");
    }

    public void logTrace(String text, String startText) {
        if (loggingType.getValue() <= LoggingType.TRACE.getValue()) {
            log("TRACE (Java)", text, startText);
        }
    }
    public void logTrace(String text) {
        logTrace(text, "");
    }

    }
