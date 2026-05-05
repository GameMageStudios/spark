from spark_types import *
from spark_errors import *
from ast_nodes import *
from spark_subtypes import *
from string import ascii_letters

class Lexer:
    DIGITS = "0123456789"
    LETTERS = ascii_letters + "_"
    LETTER_DIGITS = LETTERS + DIGITS
    KEYWORDS = [
        "null", "true", "false",
        "var", "free",
        "func", "return",
        "if", "while",
        "INT", "FLOAT", "BOOL", "STRING",
    ]

    COMMENT_NONE = 0
    COMMENT_ONELINE = 1
    COMMENT_MULTILINE = 2

    def __init__(self, code: str):
        self.pos = Position()
        self.c = None
        self.code = code
        self.err = None
        self.comment = self.COMMENT_NONE

        self.advance()
        
    def advance(self):
        self.c = self.pos.advance(self.code)
    
    def peek(self, chars: int):
        idx = self.pos.idx + chars

        if idx < len(self.code):
            return self.code[idx]
        return None
    
    def get_lexed(self) -> tuple[list[Token], SparkError]:
        self.err = None

        tokens: list[Lexer.Token] = []

        while self.c:
            if self.comment == self.COMMENT_NONE:
                if self.c in " \n\t":
                    self.advance()
                elif self.c in Lexer.DIGITS:
                    tokens.append(self.make_num())
                elif self.c in Lexer.LETTERS:
                    tokens.append(self.make_id())
                elif self.c == ";":
                    tokens.append(Token(TT_SEMICOLON, None, self.pos.copy()))
                    self.advance()
                elif self.c == "+":
                    tokens.append(Token(TT_PLUS, None, self.pos.copy()))
                    self.advance()
                elif self.c == "-":
                    tokens.append(Token(TT_MINUS, None, self.pos.copy()))
                    self.advance()
                elif self.c == "*":
                    tokens.append(Token(TT_MUL, None, self.pos.copy()))
                    self.advance()
                elif self.c == "/":
                    if self.peek(1) == "/":
                        start_pos = self.pos.copy()
                        self.advance()
                        self.comment = self.COMMENT_ONELINE
                    elif self.peek(1) == "*":
                        start_pos = self.pos.copy()
                        self.advance()
                        self.comment = self.COMMENT_MULTILINE
                    else:
                        tokens.append(Token(TT_DIV, None, self.pos.copy()))
                    self.advance()
                elif self.c == "(":
                    tokens.append(Token(TT_LPAREN, None, self.pos.copy()))
                    self.advance()
                elif self.c == ")":
                    tokens.append(Token(TT_RPAREN, None, self.pos.copy()))
                    self.advance()
                elif self.c == "[":
                    tokens.append(Token(TT_LBRACKET, None, self.pos.copy()))
                    self.advance()
                elif self.c == "]":
                    tokens.append(Token(TT_RBRACKET, None, self.pos.copy()))
                    self.advance()
                elif self.c == "{":
                    tokens.append(Token(TT_LBRACE, None, self.pos.copy()))
                    self.advance()
                elif self.c == "}":
                    tokens.append(Token(TT_RBRACE, None, self.pos.copy()))
                    self.advance()
                elif self.c == "=":
                    if self.peek(1) == "=":
                        start_pos = self.pos.copy()
                        self.advance()
                        tokens.append(Token(TT_EQ, None, start_pos, self.pos.copy()))
                    else:
                        tokens.append(Token(TT_ASSIGN, None, self.pos.copy()))
                    self.advance()
                elif self.c == ">":
                    tokens.append(Token(TT_GT, None, self.pos.copy()))
                    self.advance()
                elif self.c == "<":
                    tokens.append(Token(TT_LT, None, self.pos.copy()))
                    self.advance()
                elif self.c == ":":
                    tokens.append(Token(TT_COLON, None, self.pos.copy()))
                    self.advance()
                elif self.c == ",":
                    tokens.append(Token(TT_COMMA, None, self.pos.copy()))
                    self.advance()
                elif self.c in "\"'":
                    tokens.append(self.make_string())
                elif self.c == "&":
                    if self.peek(1) == "&":
                        start_pos = self.pos.copy()
                        self.advance()
                        tokens.append(Token(TT_LOG_AND, None, start_pos, self.pos.copy()))
                    else:
                        tokens.append(Token(TT_BIT_AND, None, self.pos.copy()))
                    self.advance()
                elif self.c == "|":
                    if self.peek(1) == "|":
                        start_pos = self.pos.copy()
                        self.advance()
                        tokens.append(Token(TT_LOG_OR, None, start_pos, self.pos.copy()))
                    else:
                        tokens.append(Token(TT_BIT_OR, None, self.pos.copy()))
                    self.advance()
                elif self.c == "!":
                    if self.peek(1) == "=":
                        start_pos = self.pos.copy()
                        self.advance()
                        tokens.append(Token(TT_NEQ, None, start_pos, self.pos.copy()))
                    else:
                        tokens.append(Token(TT_LOG_NOT, None, self.pos.copy()))
                    self.advance()
                elif self.c == "~":
                    tokens.append(Token(TT_BIT_NOT, None, self.pos.copy()))
                    self.advance()
                else:
                    return None, SparkUnknownCharacterError(repr(self.c), self.pos)
            else:
                if self.c == "\n" and self.comment == self.COMMENT_ONELINE:
                    self.comment = self.COMMENT_NONE
                if self.c == "*" and self.peek(1) == "/" and self.comment == self.COMMENT_MULTILINE:
                    self.comment = self.COMMENT_NONE
                    self.advance()
                    self.advance()
                else:
                    self.advance()
        return tokens, self.err
    
    def make_num(self):
        is_float = False
        num_str = ""
        start_pos = self.pos.copy()

        while self.c:
            if self.c not in Lexer.DIGITS + ".":
                break
            if self.c == ".":
                is_float = True
            num_str += self.c
            self.advance()

        if is_float:
            return Token(TT_FLOAT, float(num_str), start_pos, self.pos.copy())
        return Token(TT_INT, int(num_str), start_pos, self.pos.copy())

    def make_id(self):
        id_str = ""
        start_pos = self.pos.copy()

        while self.c:
            if self.c not in Lexer.LETTER_DIGITS:
                break
            
            id_str += self.c
            self.advance()

        if id_str in Lexer.KEYWORDS:
            return Token(TT_KEYWORD, id_str, start_pos, self.pos.copy())
        return Token(TT_IDENTIFIER, id_str, start_pos, self.pos.copy())

    def make_string(self):
        opening = self.c
        repr_str = ""
        start_pos = self.pos.copy()
        self.advance()

        while self.c != opening:
            if self.c == "\n" or self.c is None:
                self.err = SparkUnclosedStringError("Expected `\"` after string", self.pos.copy())
                return
            elif self.c == "\\":
                self.advance()

                if self.c is None:
                    self.err = SparkUnclosedStringError("Expected `\"` after string", self.pos.copy())
                    return
                elif self.c == "\\":
                    repr_str += "\\"
                elif self.c == "\"":
                    repr_str += "\""
                elif self.c == "\'":
                    repr_str += "\'"
                elif self.c == "n":
                    repr_str += "\n"
                elif self.c == "t":
                    repr_str += "\t"
                elif self.c == "r":
                    repr_str += "\r"
                elif self.c == "e":
                    repr_str += "\033"
                self.advance()
            else:
                repr_str += self.c
                self.advance()
        
        self.advance()

        return Token(TT_STRING, repr_str, start_pos, self.pos.copy())

class Parser:
    CASTABLE_KEYWORDS = [
        "INT", "FLOAT", "BOOL", "STRING",
    ]

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.i = -1
        self.t: Token = None
        self.err: SparkParserError = None

        self.advance()

    def advance(self):
        self.i += 1

        if self.i < len(self.tokens):
            self.t = self.tokens[self.i]
        else:
            self.t = None

    def get_tree(self):
        tree = self.program()

        return tree, self.err

    def log_err(self, error: SparkParserError):
        if not self.err:
            self.err = error

    def program(self):
        program_node = ProgramNode(None, None)

        while self.t is not None and self.err is None:
            statement = self.statement()
            if statement: program_node.statements.append(statement)
        
        return program_node
    
    def statement(self):
        if self.t.token_type == TT_KEYWORD:
            if self.t.value == "var":
                start_pos = self.t.start_pos
                self.advance()

                var_name = None

                identifier = self.consume(TT_IDENTIFIER)

                if not identifier:
                    return

                var_name = identifier.value

                self.consume(TT_ASSIGN)

                block = self.expr()

                semicolon = self.consume(TT_SEMICOLON)

                if not semicolon:
                    return

                return VarDeclareNode(start_pos, semicolon.end_pos, var_name, block)
            elif self.t.value == "free":
                start_pos = self.t.start_pos
                end_pos = None
                self.advance()

                var_name = None

                identifier = self.consume(TT_IDENTIFIER)

                if not identifier:
                    return

                var_name = identifier.value

                semicolon = self.consume(TT_SEMICOLON)

                if not semicolon:
                    return
                
                return VarFreeNode(start_pos, semicolon.end_pos, var_name)
            elif self.t.value == "func":
                start_pos = self.t.start_pos
                self.advance()

                identifier = self.consume(TT_IDENTIFIER)
                if not identifier: return
                func_name = identifier.value

                if not self.consume(TT_LPAREN): return

                params: list[str] = []
                if self.t and self.t.token_type != TT_RPAREN:
                    params.append(self.consume(TT_IDENTIFIER).value)
                    while self.t and self.t.token_type == TT_COMMA:
                        self.advance()
                        params.append(self.consume(TT_IDENTIFIER).value)
                
                if not self.consume(TT_RPAREN): return

                block = self.make_code_block()

                return FunctionDeclareNode(start_pos, block.end_pos, func_name, params, block)
            elif self.t.value == "return":
                start_pos = self.t.start_pos
                self.advance()

                expr = self.expr()

                semicolon = self.consume(TT_SEMICOLON)

                if not semicolon:
                    return
                
                return ReturnStatementNode(start_pos, semicolon.end_pos, expr)
            elif self.t.value == "if":
                start_pos = self.t.start_pos
                self.advance()

                cond = self.expr()

                block = self.make_code_block()

                return IfStatementNode(start_pos, block.end_pos, cond, block)
            elif self.t.value == "while":
                start_pos = self.t.start_pos
                self.advance()

                cond = self.expr()

                block = self.make_code_block()

                return WhileStatementNode(start_pos, block.end_pos, cond, block)
            
        if self.t.token_type == TT_IDENTIFIER and self.peek_safe(1).token_type == TT_ASSIGN:
            start_pos = self.t.start_pos
            identifier = self.t
            self.advance()
            self.advance()

            var_name = identifier.value

            block = self.expr()
            semicolon = self.consume(TT_SEMICOLON)

            if not semicolon:
                return
            
            return VarAssignNode(start_pos, semicolon.end_pos, var_name, block)
        if self.t.token_type in (TT_KEYWORD, TT_INT, TT_FLOAT, TT_STRING, TT_IDENTIFIER, TT_PLUS, TT_MINUS, TT_LOG_NOT, TT_BIT_NOT, TT_LPAREN, TT_LBRACKET):
            block = self.expr()
            semicolon = self.consume(TT_SEMICOLON)

            if not semicolon:
                return

            if block is None:
                return
            
            block.end_pos = semicolon.end_pos
            return block
        elif self.t.token_type == TT_SEMICOLON:
            self.advance()
            return None
        else:
            self.log_err(SparkParserError("Unexpected token", self.t.start_pos, self.t.end_pos))
            return
    
    def consume(self, *types: list[str]):
        if self.t:
            if self.t.token_type in types:
                t = self.t
                self.advance()
                return t
            if len(types) == 1:
                self.log_err(SparkParserError(f"Expected a{"n" if types[0][0] in "aeioui" else ""} {types[0]} after statement", self.t.start_pos, self.t.end_pos))
            else:
                self.log_err(SparkParserError(f"Expected `{"`, `".join(types[:-2])}` or `{types[-1]}` after statement", self.t.start_pos, self.t.end_pos))
            self.advance()
            return
        if len(types) == 1:
            self.log_err(SparkParserError(f"Expected a{"n" if types[0][0] in "aeioui" else ""} {types[0]} after statement", self.tokens[-1].start_pos))
        else:
            self.log_err(SparkParserError(f"Expected `{"`, `".join(types[:-2])}` or `{types[-1]}` after statement", self.tokens[-1].start_pos))
        self.advance()
    
    def peek(self, tokens: int):
        t = self.i + tokens

        if t < len(self.tokens):
            return self.tokens[t]
        return None
    
    def peek_safe(self, tokens: int):
        t = self.i + tokens

        if t < len(self.tokens):
            return self.tokens[t]
        return Token(None, None)
    
    def expr(self):
        left = self.compares()

        while self.t is not None:
            if self.err:
                break

            if self.t.token_type not in (TT_LOG_AND, TT_LOG_OR):
                break
            
            op_tok = self.t

            self.advance()

            right = self.compares()

            left = BinOpNode(left.start_pos, right.end_pos, left, op_tok, right)
        
        return left

    def compares(self):
        left = self.bit_manipulation()

        while self.t is not None:
            if self.err:
                break

            if self.t.token_type not in (TT_EQ, TT_NEQ, TT_LT, TT_GT):
                break
            
            op_tok = self.t

            self.advance()

            right = self.bit_manipulation()

            left = BinOpNode(left.start_pos, right.end_pos, left, op_tok, right)
        
        return left

    def bit_manipulation(self):
        left = self.arithmetic()

        while self.t is not None:
            if self.err:
                break

            if self.t.token_type not in (TT_BIT_AND, TT_BIT_OR):
                break
            
            op_tok = self.t

            self.advance()

            right = self.arithmetic()

            left = BinOpNode(left.start_pos, right.end_pos, left, op_tok, right)
        
        return left

    def arithmetic(self):
        left = self.term()

        while self.t is not None:
            if self.err:
                break

            if self.t.token_type not in (TT_PLUS, TT_MINUS):
                break
            
            op_tok = self.t

            self.advance()

            right = self.term()

            left = BinOpNode(left.start_pos, right.end_pos, left, op_tok, right)
        
        return left
    
    def term(self):
        left = self.factor()

        while self.t is not None:
            if self.err:
                break

            if self.t.token_type not in (TT_MUL, TT_DIV):
                break
            
            op_tok = self.t

            self.advance()

            right = self.factor()

            left = BinOpNode(left.start_pos, right.end_pos, left, op_tok, right)

        return left
    
    def factor(self):
        if self.t is not None:
            if self.t.token_type in (TT_INT, TT_FLOAT):
                val = ConstantNode(self.t.start_pos, self.t.end_pos, SparkNumberValue(self.t.value))
                self.advance()
                return val
            elif self.t.token_type == TT_STRING:
                val = ConstantNode(self.t.start_pos, self.t.end_pos, SparkStringValue(self.t.value))
                self.advance()
                return val
            elif self.t.token_type == TT_KEYWORD and self.t.value == "null":
                val = ConstantNode(self.t.start_pos, self.t.end_pos, SparkNullValue())
                self.advance()
                return val
            elif self.t.token_type == TT_KEYWORD and self.t.value == "true":
                val = ConstantNode(self.t.start_pos, self.t.end_pos, SparkBoolValue(True))
                self.advance()
                return val
            elif self.t.token_type == TT_KEYWORD and self.t.value == "false":
                val = ConstantNode(self.t.start_pos, self.t.end_pos, SparkBoolValue(False))
                self.advance()
                return val
            elif self.t.token_type in (TT_PLUS, TT_MINUS, TT_LOG_NOT, TT_BIT_NOT):
                op_tok = self.t
                self.advance()
                value = self.factor()
                if value is None:
                    self.log_err(SparkParserError("Expected `+`, `-`, `(`, INT, STRING or a variable name", op_tok.start_pos, op_tok.end_pos))
                    return
                return UnOpNode(op_tok.start_pos, value.end_pos, op_tok, value)
            elif self.t.token_type == TT_LPAREN and self.peek_safe(1).token_type == TT_KEYWORD and self.peek_safe(1).value in Parser.CASTABLE_KEYWORDS and self.peek_safe(2).token_type == TT_RPAREN:
                start_pos = self.t.start_pos
                self.advance()

                cast_type = self.t.value

                self.advance()
                self.advance()

                value = self.expr()

                return TypeCastNode(start_pos, value.end_pos, cast_type, value)
            elif self.t.token_type == TT_LPAREN:
                start_pos = self.t.start_pos
                self.advance()
                val = self.expr()
                if val is not None:
                    val.start_pos = start_pos
                    if self.t:
                        if self.t.token_type == TT_RPAREN:
                            val.end_pos = self.t.end_pos
                            self.advance()
                            return val
                    self.err = SparkParserError("Expected `)`", start_pos, val.end_pos)
                self.advance()
            elif self.t.token_type == TT_IDENTIFIER and self.peek_safe(1).token_type == TT_LPAREN:
                start_pos = self.t.start_pos
                function_name = self.t.value
                self.advance()
                self.advance()

                passed: list[ParserTreeNode] = []
                running = True

                expected_comma = False

                rparen = None

                while running:
                    if self.t is None:
                        self.log_err(SparkParserError("Expected `)` or `,` after an expresion", start_pos))
                        return
                    elif self.t.token_type == TT_RPAREN:
                        rparen = self.t
                        break
                    elif self.t.token_type == TT_COMMA:
                        self.advance()
                    elif expected_comma:
                        self.log_err(SparkParserError("Expected `)` or `,` after an expresion", start_pos))
                        return
                    passed.append(self.expr())
                    expected_comma = True
                
                self.advance()
                
                return FunctionCallNode(start_pos, rparen.end_pos, function_name, passed)
            elif self.t.token_type == TT_IDENTIFIER:
                var = VarAccessNode(self.t.start_pos, self.t.end_pos, self.t.value)
                self.advance()
                return var
            elif self.t.token_type == TT_LBRACKET:
                start_pos = self.t.start_pos
                self.advance()
                passed: list[ParserTreeNode] = []
                running = True

                expected_comma = False

                rbracket = None

                while running:
                    if self.t is None:
                        self.log_err(SparkParserError("Expected `]` or `,` after an expresion", start_pos))
                        return
                    elif self.t.token_type == TT_RBRACKET:
                        rbracket = self.t
                        break
                    elif self.t.token_type == TT_COMMA:
                        self.advance()
                    elif expected_comma:
                        self.log_err(SparkParserError("Expected `]` or `,` after an expresion", start_pos))
                        return
                    passed.append(self.expr())
                    expected_comma = True
                
                self.advance()

                return ArrayInitNode(start_pos, rbracket.end_pos, passed)
            else:
                self.err = SparkParserError("Expected `+`, `-`, `(`, INT, STRING or a variable name", self.t.start_pos, self.t.end_pos)
        self.err = SparkParserError("Expected `+`, `-`, `(`, INT, STRING or a variable name", self.tokens[self.i - 1].start_pos, self.tokens[self.i - 1].end_pos)

    def make_code_block(self):
        if self.t.token_type != TT_LBRACE:
            return None

        self.advance()
        
        tokens: list[Token] = []
        indent = 1

        while self.t is not None and indent > 0:
            if self.t.token_type == TT_LBRACE:
                indent += 1
            elif self.t.token_type == TT_RBRACE:
                indent -= 1
            
            if indent > 0:
                tokens.append(self.t)
                self.advance()
                
        if self.t and self.t.token_type == TT_RBRACE:
            self.advance()
        else:
            self.log_err(SparkParserError("Expected '}'", self.tokens[self.i-1].end_pos))

        block_parser = Parser(tokens)
        tree = block_parser.get_tree()

        if tree[1]:
            self.log_err(tree[1])

        return tree[0]

def run(source: str, context: VisitContext, debug: bool = False, repl_mode: bool = False):
    lexer = Lexer(source)
        
    lexed = lexer.get_lexed()

    if debug: print(f"{' LEXER OUTPUT ':=^50}")

    if lexed[1]:
        print(lexed[1].to_string(source))
        return
    elif debug:
        print(lexed[0])

    if debug: print(f"{' PARSER OUTPUT ':=^50}")
    
    parser = Parser(lexed[0])

    parse_result = parser.get_tree()

    if debug: print(parse_result[0])

    if parse_result[1]:
        print(parse_result[1].to_string(source))
        return

    if debug: print(f"{' INTERPRETER OUTPUT ':=^50}")

    interpreter_output = parse_result[0].visit_repl_mode(context)

    if context.error:
        print(context.error.to_string(source))
    elif repl_mode and context.stdout.strip() == "":
        if debug: print("-" * 50)
        print(interpreter_output)


if __name__ == '__main__':
    import sys

    context = VisitContext()

    if len(sys.argv) == 2:
        with open(sys.argv[1], "r") as f:
            run(f.read(), context, False)
            sys.exit()

    if len(sys.argv) == 3:
        with open(sys.argv[1], "r") as f:
            run(f.read(), context, "d" in sys.argv[2])
            if "r" not in sys.argv[2]: sys.exit()

    while True:
        source = input("spark >>> ").strip()
        if not source.endswith(";"):
            source += ";"

        if source.startswith("#d "):
            print("--> " + repr(source[3:]))
            run(source[3:], context, True, repl_mode=True)
        else:
            run(source, context, repl_mode=True)
        
        context.error = None
        context.stdout = ""
