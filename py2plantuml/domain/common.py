from typing import List, Dict, Tuple

class Common:
    COMPLEX_TYPE: str = '*** TYPE NOT DECODED ***'
    NOT_PROVIDED_TYPE: str = '**???**'
    @staticmethod
    def reduce_member_type(member_type: str, is_member: bool = True) -> Tuple[str, str, str]:
        connection: str = '*--' if is_member else '-->'
        note: str = ''
        if member_type.startswith('List['):
            member_type=member_type[5:-1]
            connection = f'"many" {connection} "1"'
            note = ': (list)'
        elif member_type.startswith('Set['):
            member_type=member_type[4:-1]
            connection = f'"many" {connection} "1"'
            note = ': (set)'
        elif 1 in [ c in member_type for c in '[{(,)}]' ]:
            member_type=Common.COMPLEX_TYPE
            note = ': (complex type)'
        if not is_member:
            if len(note) == 0: note += ' :'
            note += ' uses '
        return connection, member_type, note