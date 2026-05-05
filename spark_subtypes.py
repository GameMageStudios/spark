from spark_errors import *
from spark_values import *

class SparkInbuiltFunction_Print(SparkFunctionValue):
    def __init__(self):
        super().__init__("print", 0, True)

    def behavior(self, context: 'VisitContext', args):
        context.print_raw(" ".join(map(lambda v: v.format("s"), args)), "\n")
        return SparkNullValue(), None
    
class SparkInbuiltFunction_PrintF(SparkFunctionValue):
    def __init__(self):
        super().__init__("printf", 1, True)

    def behavior(self, context: 'VisitContext', args):
        format_string = args[0]

        if isinstance(format_string, SparkStringValue):
            format_string = format_string.value
        else:
            return SparkNullValue(), SparkRuntimeError("First argument must be a STRING")

        passed = args[1:]

        arg = 0
        ridx = 0
        template = ""
        collecting = False
        output = ""

        while ridx < len(format_string):
            c = format_string[ridx]

            if c == "%":
                template = ""
                collecting = True
            elif collecting:
                template += c
                if c in "sdf":
                    collecting = False
                    if arg < len(passed):
                        output += passed[arg].format(template)
                        arg += 1
                    else:
                        return SparkNullValue(), SparkRuntimeError("Not enough arguments for printf")
            else:
                output += c

            ridx += 1
        
        context.print(output, "")

        return SparkNullValue(), None

class SparkInbuiltFunction_Input(SparkFunctionValue):
    def __init__(self):
        super().__init__("input", 0, True)

    def behavior(self, context: 'VisitContext', args):
        context.print_raw(" ".join(map(lambda v: v.format("s"), args)), "")
        return SparkStringValue(input()), None

class SparkInbuiltFunction_CSet(SparkFunctionValue):
    def __init__(self):
        super().__init__("cSet", 3, False)
    
    def behavior(self, context, args):
        container = args[0]
        return container.cset(args[1], args[2])
        
class SparkInbuiltFunction_CGet(SparkFunctionValue):
    def __init__(self):
        super().__init__("cGet", 2, False)
    
    def behavior(self, context, args):
        container = args[0]
        return container.cget(args[1])
        
class SparkInbuiltFunction_CAdd(SparkFunctionValue):
    def __init__(self):
        super().__init__("cAdd", 2, False)
    
    def behavior(self, context, args):
        container = args[0]
        return container.cadd(args[1])

class SparkInbuiltFunction_Hash(SparkFunctionValue):
    def __init__(self):
        super().__init__("hash", 1, False)
    
    def behavior(self, context, args):
        h = args[0].hash()
        return SparkNumberValue(h[0]), h[1]

class SparkInbuiltFunction_Exit(SparkFunctionValue):
    def __init__(self):
        super().__init__("exit", 0, False)
    
    def behavior(self, context, args):
        context.halted = True
        return SparkNullValue(), None

class SparkInbuiltFunction_CContains(SparkFunctionValue):
    def __init__(self):
        super().__init__("cContains", 2, False)
    
    def behavior(self, context, args):
        if isinstance(args[0], SparkArrayValue):
            is_contained = False
            for element in args[0].value:
                ret = element.bin_eq(args[1])
                if ret[1]:
                    continue
                if ret[0].is_true():
                    is_contained = True
                    break
            return SparkBoolValue(is_contained), None
        elif isinstance(args[0], SparkStringValue) and isinstance(args[1], SparkStringValue):
            is_contained = False
            for c in args[0].value:
                ret = c == args[1].value
                if ret:
                    is_contained = True
                    break
            return SparkBoolValue(is_contained), None
        return SparkNullValue(), SparkRuntimeError(f"Expected ARRAY, ANY or STRING, STRING not {args[0].TYPE_NAME}, {args[1].TYPE_NAME}")

class SparkInbuiltFunction_CLength(SparkFunctionValue):
    def __init__(self):
        super().__init__("cLenght", 1, False)
    
    def behavior(self, context, args):
        if isinstance(args[0], SparkArrayValue) or isinstance(args[0], SparkStringValue):
            return SparkNumberValue(len(args[0].value)), None
        return SparkNullValue(), SparkRuntimeError(f"Expected ARRAY or STRING not {args[0].TYPE_NAME}")

class SparkInbuiltFunction_StrStrip(SparkFunctionValue):
    def __init__(self):
        super().__init__("strStrip", 1, False)
    
    def behavior(self, context, args):
        if isinstance(args[0], SparkStringValue):
            return SparkStringValue(args[0].value.strip()), None
        return SparkNullValue(), SparkRuntimeError(f"Expected STRING not {args[0].TYPE_NAME}")

class SparkInbuiltFunction_Repr(SparkFunctionValue):
    def __init__(self):
        super().__init__("repr", 1, False)
    
    def behavior(self, context, args):
        return SparkStringValue(repr(args[0].value)), None
    
class VisitContext:
    def __init__(self):
        self.halted = False
        self.ret: SparkValue = None
        self.can_return = False
        self.error: 'SparkRuntimeError' = None
        self.vars: dict[str, SparkValue] = {
            "print":  SparkInbuiltFunction_Print(),
            "printf": SparkInbuiltFunction_PrintF(),
            "input":  SparkInbuiltFunction_Input(),
            "cSet": SparkInbuiltFunction_CSet(),
            "cGet": SparkInbuiltFunction_CGet(),
            "cAdd": SparkInbuiltFunction_CAdd(),
            "cContains": SparkInbuiltFunction_CContains(),
            "cLenght": SparkInbuiltFunction_CLength(),
            "strStrip": SparkInbuiltFunction_StrStrip(),
            "repr": SparkInbuiltFunction_Repr(),
            "hash": SparkInbuiltFunction_Hash(),
            "exit": SparkInbuiltFunction_Exit(),
        }
        self.stdout = ""
    
    def print(self, val: SparkValue, end="\n"):
        self.stdout += str(val) + end
        print(str(val), end=end)
    
    def print_raw(self, string: str, end="\n"):
        self.stdout += string + end
        print(string, end=end)
    
    def add_error(self, error: SparkRuntimeError):
        if not self.error:
            self.error = error
    
    def make_var(self, name: str, value: SparkValue):
        if name in self.vars.keys():
            return SparkNullValue(), SparkRuntimeError(f"Variable already exists, cannot be defined: {repr(name)}")

        self.vars[name] = value

        return SparkNullValue(), None
    
    def set_var(self, name: str, value: SparkValue):
        if name not in self.vars.keys():
            return SparkNullValue(), SparkRuntimeError(f"Variable does not exist, cannot be accessed: {repr(name)}")

        self.vars[name] = value

        return SparkNullValue(), None
    
    def free_var(self, name: str):
        if name not in self.vars.keys():
            return SparkNullValue(), SparkRuntimeError(f"Variable does not exist, cannot be freed: {repr(name)}")
    
        del self.vars[name]

        return SparkNullValue(), None
    
    def get_var(self, name: str):
        if name not in self.vars.keys():
            return SparkNullValue(), SparkRuntimeError(f"Variable does not exist, cannot be accessed: {repr(name)}")
    
        return self.vars[name], None
    
    def __str__(self):
        return f"VisitContext.vars = {self.vars}"
