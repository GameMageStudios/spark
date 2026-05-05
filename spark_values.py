from spark_errors import *

class SparkValue:
    TYPE_NAME = "Type name not declared".replace(" ", "-").upper()
    
    def bin_plus(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform ADD operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    def bin_minus(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform ADD operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    def bin_muled(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform ADD operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    def bin_dived(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform ADD operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    
    def un_plus(self) -> 'SparkValue':
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform ADD operation on {self.TYPE_NAME}")
    def un_minus(self) -> 'SparkValue':
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform SUBTRACT operation on {self.TYPE_NAME}")
    
    def bin_eq(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform EQ operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    def bin_lt(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform LT operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    def bin_gt(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform GT operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    
    def is_true(self) -> bool: return False

    def log_and(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkBoolValue(self.is_true() and other.is_true()), None
    def log_or(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkBoolValue(self.is_true() or other.is_true()), None
    def log_not(self) -> 'SparkValue':
        return SparkBoolValue(not self.is_true())
    
    def bit_and(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform BITWISE AND operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    def bit_or(self, other: 'SparkValue') -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform BITWISE OR operation on {self.TYPE_NAME} and {other.TYPE_NAME}")
    def bit_not(self) -> 'SparkValue':
        return SparkNullValue(), SparkRuntimeError(f"Cannot preform BITWISE NOT operation on {self.TYPE_NAME}")
    
    def call(self, context, args) -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot call a {self.TYPE_NAME} type")
    
    def cset(self, key: 'SparkValue', value: 'SparkValue'):
        return SparkNullValue(), SparkRuntimeError(f"Cannot set {key} in {repr(self)} ({self.TYPE_NAME})")
    
    def cget(self, key: 'SparkValue'):
        return SparkNullValue(), SparkRuntimeError(f"Cannot get {key} in {repr(self)} ({self.TYPE_NAME})")
    
    def cadd(self, value: 'SparkValue'):
        return SparkNullValue(), SparkRuntimeError(f"Cannot add to {repr(self)} ({self.TYPE_NAME})")

    def format(self, template: str) -> str: return f"<UNDEFINED_FORMAT({repr(template)})FOR({self.TYPE_NAME})>"
    def cast(self, type_name: str) -> tuple['SparkValue', SparkRuntimeError]:
        return SparkNullValue(), SparkRuntimeError(f"Cannot cast {self.TYPE_NAME} to {type_name}")
    def hash(self):
        return SparkNullValue(), SparkRuntimeError(f"Cannot hash {self.TYPE_NAME}")

class SparkNullValue(SparkValue):
    TYPE_NAME = "NULL"

    def bin_eq(self, other: 'SparkValue') -> 'SparkValue':
        if isinstance(other, SparkNullValue):
            return SparkBoolValue(True), None
        return SparkBoolValue(False), None

    def format(self, template: str) -> str:
        f = template[-1]

        match f:
            case "d":
                return "0"
            case "s":
                return "<NULL>"
            case "f":
                return "0.0"
        return super().format(template)

    def hash(self):
        return 0, None

    def __repr__(self):
        return "<NULL>"

class SparkBoolValue(SparkValue):
    TYPE_NAME = "BOOL"

    def __init__(self, value: bool):
        self.value = value
    
    def bit_and(self, other):
        if isinstance(other, SparkBoolValue):
            return SparkBoolValue(self.value and other.value), None
        return super().bit_and(other)
    def bit_or(self, other):
        if isinstance(other, SparkBoolValue):
            return SparkBoolValue(self.value or other.value), None
        return super().bit_or(other)
    def bit_not(self):
        return SparkBoolValue(not self.value)

    def format(self, template: str) -> str:
        f = template[-1]

        match f:
            case "d":
                return "1" if self.value else "0"
            case "s":
                return "<TRUE>" if self.value else "<FALSE>"
            case "f":
                return "1.0" if self.value else "0.0"
        return super().format(template)
    def cast(self, type_name):
        if type_name == "INT":
            return SparkNumberValue(int(self.value)), None
        elif type_name == "FLOAT":
            return SparkNumberValue(float(self.value)), None
        elif type_name == "BOOL":
            return SparkBoolValue(self.value), None
        elif type_name == "STRING":
            return SparkStringValue(repr(self)), None
        return super().cast(type_name)
    
    def is_true(self):
        return self.value

    def hash(self):
        return int(self.value), None

    def __repr__(self):
        return "<TRUE>" if self.value else "<FALSE>"

class SparkNumberValue(SparkValue):
    TYPE_NAME = "NUMBER"

    def __init__(self, num: int | float):
        self.value = num
    
    def bin_plus(self, other):
        if isinstance(other, SparkNumberValue):
            return SparkNumberValue(self.value + other.value), None
        return super().bin_plus(other)
    def bin_minus(self, other):
        if isinstance(other, SparkNumberValue):
            return SparkNumberValue(self.value - other.value), None
        return super().bin_minus(other)
    def bin_muled(self, other):
        if isinstance(other, SparkNumberValue):
            return SparkNumberValue(self.value * other.value), None
        return super().bin_muled(other)
    def bin_dived(self, other):
        if isinstance(other, SparkNumberValue):
            if other.value == 0:
                return SparkNullValue(), SparkRuntimeError(f"Zero division error")
            return SparkNumberValue(self.value / other.value), None
        return super().bin_dived(other)
    def un_plus(self):
        return SparkNumberValue(self.value)
    def un_minus(self):
        if isinstance(self.value, int):
            return SparkNumberValue(~self.value + 1)
        else:
            return SparkNumberValue(-self.value)
    def bin_eq(self, other):
        if isinstance(other, SparkNumberValue):
            return SparkBoolValue(self.value == other.value), None
        return super().bin_eq(other)
    def bin_lt(self, other):
        if isinstance(other, SparkNumberValue):
            return SparkBoolValue(self.value < other.value), None
        return super().bin_lt(other)
    def bin_gt(self, other):
        if isinstance(other, SparkNumberValue):
            return SparkBoolValue(self.value > other.value), None
        return super().bin_gt(other)
    
    def bit_and(self, other):
        if isinstance(other, SparkNumberValue):
            return SparkNumberValue(int(self.value) & int(other.value)), None
        return super().bit_and(other)
    def bit_or(self, other):
        if isinstance(other, SparkNumberValue):
            return SparkNumberValue(int(self.value) | int(other.value)), None
        return super().bit_or(other)
    def bit_not(self):
        return SparkNumberValue(~int(self.value))

    def format(self, template: str) -> str:
        f = template[-1]

        match f:
            case "d":
                return str(int(self.value))
            case "s":
                return str(self.value)
            case "f":
                return str(float(self.value))
        return super().format(template)
    def cast(self, type_name):
        if type_name == "INT":
            return SparkNumberValue(int(self.value)), None
        elif type_name == "FLOAT":
            return SparkNumberValue(float(self.value)), None
        elif type_name == "BOOL":
            return SparkBoolValue(self.value != 0), None
        elif type_name == "STRING":
            return SparkStringValue(repr(self.value)), None
        return super().cast(type_name)
    
    def hash(self):
        return hash(self.value), None

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)

class SparkStringValue(SparkValue):
    TYPE_NAME = "STRING"

    def __init__(self, value: str):
        self.value = value
    
    def bin_plus(self, other: 'SparkValue') -> 'SparkValue':
        if isinstance(other, SparkStringValue):
            return SparkStringValue(self.value + other.value), None
        return super().bin_plus(other)
    def bin_muled(self, other: 'SparkValue') -> 'SparkValue':
        if isinstance(other, SparkNumberValue):
            i = int(other.value)

            return SparkStringValue(self.value * i), None
        return super().bin_muled(other)
    def bin_eq(self, other: 'SparkValue') -> 'SparkValue':
        if isinstance(other, SparkStringValue):
            return SparkBoolValue(self.value == other.value), None
        return SparkBoolValue(False), None

    def format(self, template: str) -> str:
        f = template[-1]

        match f:
            case "d":
                return "0"
            case "s":
                return self.value
            case "f":
                return "0.0"
        return super().format(template)
    def cast(self, type_name):
        if type_name == "INT":
            return self.__convert_to_int()
        elif type_name == "FLOAT":
            return self.__convert_to_float()
        elif type_name == "BOOL":
            return self.__convert_to_bool()
        elif type_name == "STRING":
            return SparkStringValue(self.value), None
        return super().cast(type_name)
    
    def is_true(self):
        return self.value != ""
    
    def __convert_to_int(self):
        ret = 0

        for p, c in enumerate(self.value):
            exponent = 10 ** (len(self.value) - p - 1)

            match c:
                case "0":
                    ...
                case "1":
                    ret += exponent
                case "2":
                    ret += exponent * 2
                case "3":
                    ret += exponent * 3
                case "4":
                    ret += exponent * 4
                case "5":
                    ret += exponent * 5
                case "6":
                    ret += exponent * 6
                case "7":
                    ret += exponent * 7
                case "8":
                    ret += exponent * 8
                case "9":
                    ret += exponent * 9
                case c:
                    return SparkNullValue(), SparkRuntimeError(f"Cannot cast {repr(self)} (STRING) to INT")
        
        return SparkNumberValue(ret), None
    
    def __convert_to_float(self):
        ret_str = ""
        has_dot = False

        for p, c in enumerate(self.value):
            exponent = 10 ** (len(self.value) - p - 1)

            match c:
                case ".":
                    if has_dot:
                        return SparkNullValue(), SparkRuntimeError(f"Cannot cast {repr(self)} (STRING) to FLOAT")
                    has_dot = True
                    ret_str += "."

                case c:
                    if c in "0123456789":
                        ret_str += c
                    else:
                        return SparkNullValue(), SparkRuntimeError(f"Cannot cast {repr(self)} (STRING) to FLOAT")

        if ret_str == "":
            return SparkNumberValue(0.0), None
        
        return SparkNumberValue(float(ret_str)), None
    
    def cset(self, key, value):
        if isinstance(key, SparkNumberValue):
            idx = int(key.value)

            if -len(self.value) <= idx and  idx < len(self.value):
                self.value[idx] = value
                return self, None

        return super().cset(key, value)
    
    def cget(self, key):
        if isinstance(key, SparkNumberValue):
            idx = int(key.value)

            if -len(self.value) <= idx and  idx < len(self.value):
                return SparkStringValue(self.value[idx]), None

        return super().cget(key)
    
    def hash(self):
        return hash(self.value), None

    def __convert_to_bool(self):
        if self.value.lower() in ("<true>", "true", "t", "1"):
            return SparkBoolValue(True), None
        if self.value.lower() in ("<false>", "false", "f", "0"):
            return SparkBoolValue(False), None
        return SparkNullValue(), SparkRuntimeError(f"Cannot cast {repr(self)} (STRING) to BOOL")

    def __repr__(self):
        return repr(self.value)

class SparkFunctionValue(SparkValue):
    TYPE_NAME = "FUNCTION"

    def __init__(self, function_name: str, expected_arg_count: int, can_be_more_args: bool = False):
        super().__init__()
        self.function_name = function_name
        self.expected_arg_count = expected_arg_count
        self.can_be_more_args = can_be_more_args
    
    def call(self, context, args: list[SparkValue]):
        if len(args) == self.expected_arg_count:
            return self.behavior(context, args)
        elif len(args) > self.expected_arg_count and self.can_be_more_args:
            return self.behavior(context, args)
        else:
            return SparkNullValue(), SparkRuntimeError(f"Function {self.function_name} expected {self.expected_arg_count} {"or more " if self.can_be_more_args else ""}argument{"" if self.expected_arg_count == 1 else "s"}, recieved {len(args)}")
    
    def behavior(self, context, args: list[SparkValue]):
        return SparkNullValue(), None
    
    def __repr__(self):
        return f"<FUNCTION:{self.function_name}({("..." if self.expected_arg_count == 0 else str(self.expected_arg_count) + " ...") if self.can_be_more_args else ("" if self.expected_arg_count == 0 else str(self.expected_arg_count))})>"

class SparkArrayValue(SparkValue):
    TYPE_NAME = "ARRAY"

    def __init__(self):
        super().__init__()
        self.value: list[SparkValue] = []

    def format(self, template: str) -> str:
        f = template[-1]

        match f:
            case "d":
                return "0"
            case "s":
                return repr(self)
            case "f":
                return "0.0"
        return super().format(template)
    
    def cset(self, key, value):
        if isinstance(key, SparkNumberValue):
            idx = int(key.value)

            if -len(self.value) <= idx and  idx < len(self.value):
                self.value[idx] = value
                return self, None

        return super().cset(key, value)
    
    def cget(self, key):
        if isinstance(key, SparkNumberValue):
            idx = int(key.value)

            if -len(self.value) <= idx and  idx < len(self.value):
                return self.value[idx], None

        return super().cget(key)
    
    def cadd(self, value):
        self.value.append(value)
        return self, None
    
    def __repr__(self):
        return f"[{", ".join(map(lambda x: str(x), self.value))}]"
