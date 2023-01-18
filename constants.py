from enum import Enum


class InstructionType(Enum):
    ALU = 1
    LDST = 2
    BRANCH = 3


class PolicyType(Enum):
    RR = "RR"
    PRR = "PRR"


class InstructionError(Exception):
    pass


class PolicyTypeError(Exception):
    pass


INSTRUCTION_TYPE = "INSTRUCTION_TYPE"
ROW_ID = "ROW_ID"
FINISH_CYCLE = "FINISH_CYCLE"
