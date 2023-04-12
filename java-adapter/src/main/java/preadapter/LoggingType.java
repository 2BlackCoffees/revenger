package preadapter;

public enum LoggingType {
    TRACE(0),
    DEBUG(1),
    INFO(2),
    WARNING(3),
    ERROR(4);

    private final int value;

    LoggingType(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
