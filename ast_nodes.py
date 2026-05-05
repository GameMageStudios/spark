from copy import deepcopy

from spark_types import *
from spark_values import *
from spark_subtypes import *

class ParserTreeNode:
    def __init__(self, start_pos: Position, end_pos: Position):
        self.start_pos = start_pos
        self.end_pos = end_pos

    def visit(self, context: VisitContext) -> SparkValue:
        ...

    def visit_repl_mode(self, context: VisitContext) -> None:
        print(self.visit(context))

class ProgramNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos):
        super().__init__(start_pos, end_pos)
        self.statements: list[ParserTreeNode] = []
    
    def visit(self, context):
        for statement in self.statements:
            if context.ret: break
            if context.halted: break
            if context.error: break
            statement.visit(context)

    def visit_repl_mode(self, context: VisitContext):
        ret = ""
        for statement in self.statements:
            if context.error: break
            val = statement.visit(context)
            if val: ret += repr(val) + "\n"
        return ret.strip()

    def __repr__(self):
        return "\n".join(map(
            lambda x: str(x),
            self.statements
        ))

class ConstantNode(ParserTreeNode):
    def __init__(self, start_pos: Position, end_pos: Position, value: SparkValue):
        super().__init__(start_pos, end_pos)
        self.value = value

    def visit(self, context):
        super().visit(context)

        return self.value
    
    def __repr__(self):
        return f"{self.value}"

class UnOpNode(ParserTreeNode):
    def __init__(self, start_pos: Position, end_pos: Position, op_tok: Token, right: ParserTreeNode):
        super().__init__(start_pos, end_pos)
        self.op_tok = op_tok
        self.right = right
    
    def visit(self, context):
        super().visit(context)

        right = self.right.visit(context)
    
        if self.op_tok.token_type == TT_PLUS:
            return right.un_plus()
        elif self.op_tok.token_type == TT_MINUS:
            return right.un_minus()
        elif self.op_tok.token_type == TT_BIT_NOT:
            return right.bit_not()
        elif self.op_tok.token_type == TT_LOG_NOT:
            return right.log_not()

    def __repr__(self):
        return f"({self.op_tok.token_type.upper()}, {self.right})"

class BinOpNode(ParserTreeNode):
    def __init__(self, start_pos: Position, end_pos: Position, left: ParserTreeNode, op_tok: Token, right: ParserTreeNode):
        super().__init__(start_pos, end_pos)
        self.left = left
        self.right = right
        self.op_tok = op_tok
    
    def visit(self, context):
        if not context.error:
            super().visit(context)

            left = self.left.visit(context)
            right = self.right.visit(context)

            ret = None

            if self.op_tok.token_type == TT_PLUS:
                ret = left.bin_plus(right)
            elif self.op_tok.token_type == TT_MINUS:
                ret = left.bin_minus(right)
            elif self.op_tok.token_type == TT_MUL:
                ret = left.bin_muled(right)
            elif self.op_tok.token_type == TT_DIV:
                ret = left.bin_dived(right)
            elif self.op_tok.token_type == TT_EQ:
                ret = left.bin_eq(right)
            elif self.op_tok.token_type == TT_NEQ:
                val = left.bin_eq(right)
                res = val[0].log_not()
                ret = res[0], res[1] if not val[1] else val[1]
            elif self.op_tok.token_type == TT_LT:
                ret = left.bin_lt(right)
            elif self.op_tok.token_type == TT_GT:
                ret = left.bin_gt(right)
            elif self.op_tok.token_type == TT_BIT_AND:
                ret = left.bit_and(right)
            elif self.op_tok.token_type == TT_BIT_OR:
                ret = left.bit_or(right)
            elif self.op_tok.token_type == TT_LOG_AND:
                ret = left.log_and(right)
            elif self.op_tok.token_type == TT_LOG_OR:
                ret = left.log_or(right)

            if ret[1]:
                ret[1].start_pos = self.start_pos
                ret[1].end_pos = self.end_pos
                context.add_error(ret[1])
                return SparkNullValue()

            return ret[0]

    def __repr__(self):
        return f"({self.left}, {self.op_tok.token_type.upper()}, {self.right})"

class VarDeclareNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, var: str, expr: ParserTreeNode):
        super().__init__(start_pos, end_pos)
        self.var = var
        self.expr = expr
    
    def visit(self, context):
        _, err = context.make_var(self.var, self.expr.visit(context))

        if err:
            err.start_pos = self.start_pos
            err.end_pos = self.end_pos
            context.add_error(err)
    
    def __repr__(self):
        return f"[DECLARE_VAR:'{self.var}' = ({self.expr})]"
    
class VarAssignNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, var: str, expr: ParserTreeNode):
        super().__init__(start_pos, end_pos)
        self.var = var
        self.expr = expr
    
    def visit(self, context):
        _, err = context.set_var(self.var, self.expr.visit(context))

        if err:
            err.start_pos = self.start_pos
            err.end_pos = self.end_pos
            context.add_error(err)
    
    def __repr__(self):
        return f"[ASSIGN_VAR:'{self.var}' = ({self.expr})]"

class VarFreeNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, var: str):
        super().__init__(start_pos, end_pos)
        self.var = var
    
    def visit(self, context):
        _, err = context.free_var(self.var)
        
        if err:
            err.start_pos = self.start_pos
            err.end_pos = self.end_pos
            context.add_error(err)
    
    def __repr__(self):
        return f"[FREE_VAR:'{self.var}']"

class VarAccessNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, var: str):
        super().__init__(start_pos, end_pos)
        self.var = var
    
    def visit(self, context):
        val, err = context.get_var(self.var)
        
        if err:
            err.start_pos = self.start_pos
            err.end_pos = self.end_pos
            context.add_error(err)

        return val
    
    def __repr__(self):
        return f"(VAR:'{self.var}')"
    
class TypeCastNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, type: str, value: ParserTreeNode):
        super().__init__(start_pos, end_pos)
        self.type = type
        self.value = value
    
    def visit(self, context):
        val, err = self.value.visit(context).cast(self.type)

        if err:
            err.start_pos = self.start_pos
            err.end_pos = self.end_pos
            context.add_error(err)
        
        return val
    
    def __repr__(self):
        return f"(CAST {repr(self.type)}: {self.value})"

class ArrayInitNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, values: list[ParserTreeNode]):
        super().__init__(start_pos, end_pos)
        self.values = values
    
    def visit(self, context):
        value = SparkArrayValue()

        for element in self.values:
            value.value.append(element.visit(context))
        
        return value
    
    def __repr__(self):
        return f"(ARRAY {self.value})"

class FunctionDeclareNode(ParserTreeNode):
    class UserFunction(SparkFunctionValue):
        def __init__(self, function_name, args: list[str], program_node: ProgramNode):
            super().__init__(function_name, len(args), False)
            self.program_node = program_node
            self.args = args
        
        def behavior(self, context: VisitContext, args):
            top_scope_vars = context.vars.copy()
            top_scope_can_return = context.can_return
            context.can_return = True

            for a, arg_name in enumerate(self.args):
                context.make_var(arg_name, args[a])

            self.program_node.visit(context)

            # Retrieve values

            for var in top_scope_vars:
                if var not in self.args:
                    top_scope_vars[var] = context.vars[var]

            context.vars = top_scope_vars
            context.can_return = top_scope_can_return

            if context.ret:
                ret = context.ret
                context.ret = None
                return ret, None
            else:
                return SparkNullValue(), None

    def __init__(self, start_pos, end_pos, func: str, args: list[str], program_node: ProgramNode):
        super().__init__(start_pos, end_pos)
        self.func = func
        self.program_node = program_node
        self.args = args
    
    def visit(self, context):
        _, err = context.make_var(
            self.func,
            self.UserFunction(
                self.func, self.args, self.program_node
            )
        )

        if err:
            err.start_pos = self.start_pos
            err.end_pos = self.end_pos
            context.add_error(err)
    
    def __repr__(self):
        return f"[DECLARE_FUNC:'{self.func}' = ({self.program_node})]"

class FunctionCallNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, function_name: str, args: list[ParserTreeNode]):
        super().__init__(start_pos, end_pos)
        self.function_name = function_name
        self.args = args
    
    def visit(self, context):
        func, err = context.get_var(self.function_name)

        if err:
            err.start_pos = self.start_pos
            err.end_pos = self.end_pos
            context.add_error(err)
            return SparkNullValue()
        
        ret, func_err = func.call(context, list(
            map(
                lambda x: x.visit(context),
                self.args
            )
        ))

        if func_err:
            func_err.start_pos = self.start_pos
            func_err.end_pos = self.end_pos
            context.add_error(func_err)
            return SparkNullValue()

        return ret
    
    def __repr__(self):
        return f"(CALL {repr(self.function_name)} <<< {", ".join(map(lambda x: str(x), self.args))})"

class ReturnStatementNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, expr: ParserTreeNode):
        super().__init__(start_pos, end_pos)
        self.expr = expr
    
    def visit(self, context):
        if context.can_return:
            context.ret = self.expr.visit(context)
        else:
            context.add_error(SparkRuntimeError("Cannot return in current scope", self.start_pos, self.end_pos))
        
    def __repr__(self):
        return f"[RETURN {self.expr}]"

class IfStatementNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, cond: ParserTreeNode, program_node: ProgramNode):
        super().__init__(start_pos, end_pos)
        self.cond = cond
        self.program_node = program_node
    
    def visit(self, context):
        if self.cond.visit(context).is_true():
            top_scope_vars = context.vars.copy()

            self.program_node.visit(context)

            # Retrieve values

            for var in top_scope_vars:
                top_scope_vars[var] = context.vars[var]

            context.vars = top_scope_vars
    
    def __repr__(self):
        return f"[IF({self.cond})({self.program_node})]"

class WhileStatementNode(ParserTreeNode):
    def __init__(self, start_pos, end_pos, cond: ParserTreeNode, program_node: ProgramNode):
        super().__init__(start_pos, end_pos)
        self.cond = cond
        self.program_node = program_node
    
    def visit(self, context):
        running = self.cond.visit(context).is_true()

        while running and not context.halted and context.ret is None and context.error is None:
            top_scope_vars = context.vars.copy()

            self.program_node.visit(context)

            # Retrieve values

            for var in top_scope_vars:
                top_scope_vars[var] = context.vars[var]

            context.vars = top_scope_vars
            
            cond_value = self.cond.visit(context)
            if cond_value:
                running = cond_value.is_true()
    
    def __repr__(self):
        return f"[WHILE({self.cond})({self.program_node})]"
