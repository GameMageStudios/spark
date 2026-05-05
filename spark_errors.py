from dataclasses import dataclass
from spark_types import *

@dataclass
class SparkError:
    error_type: str
    description: str
    start_pos: Position = None
    end_pos: Position = None

    def to_string(self, source: str = "") -> str:
        result = f"{self.error_type} Error: {self.description}"
        
        if not self.start_pos:
            return result

        location = f"\nAt: Line {self.start_pos.ln + 1}, Col {self.start_pos.col + 1}"
        if self.end_pos and (self.start_pos.idx != self.end_pos.idx):
            location = f"\nFrom: Line {self.start_pos.ln + 1}, Col {self.start_pos.col + 1} to Line {self.end_pos.ln + 1}, Col {self.end_pos.col + 1}"
        
        result += location

        if source:
            visual = self._generate_visual(source)
            result += f"\n\n{visual}"

        return result

    def _generate_visual(self, source: str) -> str:
        idx_start = max(source.rfind('\n', 0, self.start_pos.idx), 0)
        idx_end = source.find('\n', self.start_pos.idx)
        if idx_end < 0: 
            idx_end = len(source)

        line_content = source[idx_start:idx_end].lstrip('\n')
        
        length = 1
        if self.end_pos and self.end_pos.ln == self.start_pos.ln:
            length = max(1, self.end_pos.idx - self.start_pos.idx)
        elif self.end_pos and self.end_pos.ln != self.start_pos.ln:
            length = len(line_content) - self.start_pos.col

        padding = " " * self.start_pos.col
        arrows = "^" * length
        
        return f"{line_content}\n{padding}{arrows}"

class SparkUnknownCharacterError(SparkError):
    def __init__(self, description, start_pos):
        super().__init__("Unknown Character", description, start_pos)

class SparkUnclosedStringError(SparkError):
    def __init__(self, description, start_pos):
        super().__init__("Unclosed String", description, start_pos)

class SparkParserError(SparkError):
    def __init__(self, description, start_pos, end_pos=None):
        super().__init__("Parser", description, start_pos, end_pos)

class SparkRuntimeError(SparkError):
    def __init__(self, description, start_pos=None, end_pos=None):
        super().__init__("Runtime", description, start_pos, end_pos)
