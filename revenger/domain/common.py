from enum import Enum
from typing import Tuple


class Common:
    class ConnectionType(Enum):
        IS_BASE = 1
        USES = 2
        USES_PARAMETER = 2
        USES_LOCAL_VARIABLE = 3
        IS_MEMBER = 4
        IS_INNER_CLASS = 5

    COMPLEX_TYPE: str = "*** TYPE NOT DECODED ***"

    @staticmethod
    def reduce_member_type(
        member_type: str,
        connection_type: ConnectionType = ConnectionType.USES_PARAMETER,
    ) -> Tuple[str, str, str]:
        connection: str
        if connection_type == connection_type.IS_MEMBER:
            connection = "*-[#10BB10]-"
        elif connection_type == connection_type.IS_INNER_CLASS:
            connection = "+-[#10BBBB]-"
        elif connection_type == connection_type.USES_PARAMETER:
            connection = ".[#6060BB].>"
        elif connection_type == connection_type.USES_LOCAL_VARIABLE:
            connection = "-[#909090]->"
        note: str = ""
        if member_type.startswith("List["):
            member_type = member_type[5:-1]
            connection = f'"many" {connection} "1"'
            note = ": (list)"
        elif member_type.startswith("Set["):
            member_type = member_type[4:-1]
            connection = f'"many" {connection} "1"'
            note = ": (set)"
        elif 1 in [c in member_type for c in "[{(,)}]"]:
            member_type = Common.COMPLEX_TYPE
            note = ": (complex type)"
        if (
            connection_type == connection_type.USES_LOCAL_VARIABLE
            or connection_type == connection_type.USES_PARAMETER
        ):
            if len(note) == 0:
                note += " :"
            note += " uses "
        return connection, member_type, note
