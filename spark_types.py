from dataclasses import dataclass

@dataclass
class Position:
    col: int = -1
    ln: int = 0
    idx: int = -1
    
    def advance(self, code: str=""):
        self.idx += 1

        if (self.idx < len(code)):
            char = code[self.idx]

            self.col += 1

            if (char == '\n'):
                self.col = 0
                self.ln += 1

            return char
        return None

    def copy(self):
        return Position(self.col, self.ln, self.idx)

TT_SEMICOLON = "semicolon"
TT_INT = "int"
TT_FLOAT = "float"
TT_STRING = "string"
TT_PLUS = "plus"
TT_MINUS = "minus"
TT_MUL = "mul"
TT_DIV = "div"
TT_EQ = "eq"
TT_NEQ = "neq"
TT_GT = "gt"
TT_LT = "lt"
TT_LOG_AND = "logicand"
TT_BIT_AND = "bitand"
TT_LOG_OR = "logicor"
TT_BIT_OR = "bitor"
TT_LOG_NOT = "logicnot"
TT_BIT_NOT = "bitnot"
TT_LPAREN = "lparen"
TT_RPAREN = "rparen"
TT_RBRACKET = "rbracket"
TT_LBRACKET = "lbracket"
TT_LBRACE = "lbrace"
TT_RBRACE = "rbrace"
TT_ASSIGN = "assign"
TT_COLON = "colon"
TT_COMMA = "comma"
TT_KEYWORD = "keyword"
TT_IDENTIFIER = "identifier"

class Token:
    def __init__(self, token_type: str, value: any=None, start_pos: Position= None, end_pos: Position= None):
        self.token_type = token_type
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos
        if end_pos is None and start_pos is not None:
            self.end_pos = start_pos

    def __repr__(self):
        if self.value is not None:
            return f"{self.token_type.upper()}:{repr(self.value)}"
        return f"{self.token_type.upper()}"
