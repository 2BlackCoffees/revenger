using System;
using static System.Net.Mime.MediaTypeNames;

namespace DotNetPreAdapter
{
    public enum LoggingType
    {
        TRACE = 0,
        DEBUG = 1,
        INFO = 2,
        WARNING = 3,
        ERROR = 4

    }
    public class Logger
	{
        LoggingType loggingType;

        public Logger(LoggingType loggingType_)
		{
            loggingType = loggingType_;

        }
        void log(string logType, string text, string startText)
        {
            string[] result = text.Split(new string[] { "\n", "\r\n" }, StringSplitOptions.None);
            foreach (string s in result)
                Console.WriteLine($"{logType}: {startText}{s}");
        }
        public void LogError(string text, string startText = "")
        {
            if (loggingType <= LoggingType.ERROR)      log("ERROR", text, startText);
        }
        public void LogWarning(string text, string startText = "")
        {
            if (loggingType <= LoggingType.WARNING)    log("WARNING", text, startText);
        }
        public void LogInfo(string text, string startText = "")
        {
            if (loggingType <= LoggingType.INFO) log("INFO", text, startText);
        }
        public void LogDebug(string text, string startText = "")
        {
            if (loggingType <= LoggingType.DEBUG) log("DEBUG", text, startText);
        }
        public void LogTrace(string text, string startText= "")
        {
            if (loggingType <= LoggingType.TRACE) log("TRACE", text, startText);
        }
    }
}

