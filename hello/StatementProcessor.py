from typing import Dict, List
from hello.Statement import Statement

class StatementProcessor(object):
    def __init__(self, st: Statement):
        self.statement = st

    def setStatement(self, st: Statement):
        self.statement = st

    def getStatement(self) -> Statement:
        return  self.statement

    def recognize(self) -> bool:
        pass

    def extract(self) -> Dict[str, str]:
        pass


class TannaiticStatementProcessor(StatementProcessor):
    "Base class for processing statements found in Mishnayot, Braytot, Toseftot"
    pass


class AmoraicStatementProcessor(StatementProcessor):
    "Base class for processing statements made by Amoraim"
    pass


class SetamaicStatementProcessor(StatementProcessor):
    "Base class for processing statements made by Setama de-Gemara"
    pass

